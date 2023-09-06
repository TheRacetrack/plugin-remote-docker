import re
from typing import Dict

from lifecycle.auth.subject import get_auth_subject_by_job_family
from lifecycle.config import Config
from lifecycle.deployer.base import JobDeployer
from lifecycle.infrastructure.infra_target import remote_shell
from lifecycle.deployer.secrets import JobSecrets
from lifecycle.job.models_registry import read_job_family_model
from plugin_config import InfrastructureConfig
from racetrack_client.client.env import merge_env_vars
from racetrack_client.log.logs import get_logger
from racetrack_client.manifest import Manifest
from racetrack_client.utils.shell import CommandError
from racetrack_client.utils.time import datetime_to_timestamp, now
from racetrack_commons.api.tracing import get_tracing_header_name
from racetrack_commons.deploy.image import get_job_image
from racetrack_commons.deploy.resource import job_resource_name
from racetrack_commons.entities.dto import JobDto, JobStatus, JobFamilyDto
from racetrack_commons.plugin.core import PluginCore
from racetrack_commons.plugin.engine import PluginEngine

JOB_INTERNAL_PORT = 7000  # Job listening port seen from inside the container

logger = get_logger(__name__)


class DockerDaemonDeployer(JobDeployer):
    """JobDeployer managing workloads on a remote docker instance"""
    def __init__(self, infrastructure_target: str, infra_config: InfrastructureConfig) -> None:
        super().__init__()
        self.infra_config = infra_config
        self.infrastructure_target = infrastructure_target

    def deploy_job(
        self,
        manifest: Manifest,
        config: Config,
        plugin_engine: PluginEngine,
        tag: str,
        runtime_env_vars: Dict[str, str],
        family: JobFamilyDto,
        containers_num: int = 1,
    ) -> JobDto:
        """Run Job as docker container on local docker"""
        if self.job_exists(manifest.name, manifest.version):
            self.delete_job(manifest.name, manifest.version)

        entrypoint_resource_name = job_resource_name(manifest.name, manifest.version)
        deployment_timestamp = datetime_to_timestamp(now())
        family_model = read_job_family_model(family.name)
        auth_subject = get_auth_subject_by_job_family(family_model)

        internal_name = f'{entrypoint_resource_name}:{JOB_INTERNAL_PORT}'

        common_env_vars = {
            'PUB_URL': config.internal_pub_url,
            'JOB_NAME': manifest.name,
            'AUTH_TOKEN': auth_subject.token,
            'JOB_DEPLOYMENT_TIMESTAMP': deployment_timestamp,
            'REQUEST_TRACING_HEADER': get_tracing_header_name(),
        }
        if config.open_telemetry_enabled:
            common_env_vars['OPENTELEMETRY_ENDPOINT'] = config.open_telemetry_endpoint

        if containers_num > 1:
            common_env_vars['JOB_USER_MODULE_HOSTNAME'] = self.get_container_name(entrypoint_resource_name, 1)

        conflicts = common_env_vars.keys() & runtime_env_vars.keys()
        if conflicts:
            raise RuntimeError(f'found illegal runtime env vars, which conflict with reserved names: {conflicts}')
        runtime_env_vars = merge_env_vars(runtime_env_vars, common_env_vars)
        plugin_vars_list = plugin_engine.invoke_plugin_hook(PluginCore.job_runtime_env_vars)
        for plugin_vars in plugin_vars_list:
            if plugin_vars:
                runtime_env_vars = merge_env_vars(runtime_env_vars, plugin_vars)
        env_vars_cmd = ' '.join([f'--env {env_name}="{env_val}"' for env_name, env_val in runtime_env_vars.items()])

        try:
            self.remote_shell(f'/opt/docker network create racetrack_default')
        except CommandError as e:
            if e.returncode != 1:
                raise e

        for container_index in range(containers_num):

            container_name = self.get_container_name(entrypoint_resource_name, container_index)
            image_name = get_job_image(config.docker_registry, config.docker_registry_namespace, manifest.name, tag, container_index)

            self.remote_shell(
                f'/opt/docker run -d'
                f' --name {container_name}'
                f' {env_vars_cmd}'
                f' --pull always'
                f' --network="racetrack_default"'
                f' --label job-name={manifest.name}'
                f' --label job-version={manifest.version}'
                f' {image_name}'
            )

        return JobDto(
            name=manifest.name,
            version=manifest.version,
            status=JobStatus.RUNNING.value,
            create_time=deployment_timestamp,
            update_time=deployment_timestamp,
            manifest=manifest,
            internal_name=internal_name,
            image_tag=tag,
            infrastructure_target=self.infrastructure_target,
        )

    def delete_job(self, job_name: str, job_version: str):
        entrypoint_resource_name = job_resource_name(job_name, job_version)
        for container_index in range(2):
            container_name = self.get_container_name(entrypoint_resource_name, container_index)
            self._delete_container_if_exists(container_name)

    def job_exists(self, job_name: str, job_version: str) -> bool:
        resource_name = job_resource_name(job_name, job_version)
        container_name = self.get_container_name(resource_name, 0)
        return self._container_exists(container_name)

    def _container_exists(self, container_name: str) -> bool:
        output = self.remote_shell(f'/opt/docker ps -a --filter "name=^/{container_name}$" --format "{{{{.Names}}}}"')
        return container_name in output.splitlines()

    def _delete_container_if_exists(self, container_name: str):
        if self._container_exists(container_name):
            self.remote_shell(f'/opt/docker rm -f {container_name}')

    def _get_next_job_port(self) -> int:
        """Return next unoccupied port for Job"""
        output = self.remote_shell(f'/opt/docker ps --filter "name=^/job-" --format "{{{{.Names}}}} {{{{.Ports}}}}"')
        occupied_ports = set()
        for line in output.splitlines():
            match = re.fullmatch(r'job-(.+) .+:(\d+)->.*', line.strip())
            if match:
                occupied_ports.add(int(match.group(2)))
        for port in range(7000, 8000, 10):
            if port not in occupied_ports:
                return port
        return 8000

    def save_job_secrets(
        self,
        job_name: str,
        job_version: str,
        job_secrets: JobSecrets,
    ):
        raise NotImplementedError("managing secrets is not supported on local docker")

    def get_job_secrets(
        self,
        job_name: str,
        job_version: str,
    ) -> JobSecrets:
        raise NotImplementedError("managing secrets is not supported on local docker")

    @staticmethod
    def get_container_name(resource_name: str, container_index: int) -> str:
        if container_index == 0:
            return resource_name
        else:
            return f'{resource_name}-{container_index}'

    def remote_shell(self, cmd: str, workdir: str | None = None) -> str:
        return remote_shell(cmd, self.infra_config.remote_gateway_url, self.infra_config.remote_gateway_token, workdir)
