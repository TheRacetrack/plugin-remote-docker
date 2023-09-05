import sys

from racetrack_client.log.logs import get_logger
from racetrack_client.utils.datamodel import parse_yaml_file_datamodel
from racetrack_client.utils.shell import shell

if 'lifecycle' in sys.modules:
    from lifecycle.deployer.infra_target import InfrastructureTarget
    from deployer import DockerDaemonDeployer
    from monitor import DockerDaemonMonitor
    from logs_streamer import DockerDaemonLogsStreamer

from plugin_config import PluginConfig, InfrastructureConfig

logger = get_logger(__name__)


class Plugin:

    def __init__(self):
        self.plugin_config: PluginConfig = parse_yaml_file_datamodel(self.config_path, PluginConfig)
        self.docker_config_dir: str = ''

        docker_config = self.plugin_config.docker
        if docker_config and docker_config.docker_registry and docker_config.username:
            shell(f'echo "{docker_config.password}" | docker login --username "{docker_config.username}" --password-stdin "{docker_config.docker_registry}"')
            logger.info(f'Logged in to Docker Registry: {docker_config.docker_registry}')
        
        self._infrastructure_targets: dict[str, InfrastructureConfig] = self.plugin_config.infrastructure_targets or {}
        infra_num = len(self._infrastructure_targets)
        logger.info(f'Docker Daemon plugin loaded with {infra_num} infrastructure targets')

    def infrastructure_targets(self) -> dict[str, 'InfrastructureTarget']:
        """
        Infrastructure Targets (deployment targets) for Jobs provided by this plugin
        :return dict of infrastructure name -> an instance of lifecycle.deployer.infra_target.InfrastructureTarget
        """
        return {
            infra_name: InfrastructureTarget(
                name=infra_name,
                job_deployer=DockerDaemonDeployer(infra_name, infra_config),
                job_monitor=DockerDaemonMonitor(infra_name, infra_config),
                logs_streamer=DockerDaemonLogsStreamer(infra_name, infra_config),
                remote_gateway_url=infra_config.remote_gateway_url,
                remote_gateway_token=infra_config.remote_gateway_token,
            )
            for infra_name, infra_config in self._infrastructure_targets.items()
        }
