import os
import re
from typing import Callable, Iterable

from lifecycle.config import Config
from lifecycle.monitor.base import FatmanMonitor
from lifecycle.monitor.health import check_until_fatman_is_operational, quick_check_fatman_condition
from lifecycle.monitor.metric_parser import read_last_call_timestamp_metric, scrape_metrics
from racetrack_client.log.exception import short_exception_details
from racetrack_client.utils.shell import shell_output
from racetrack_client.utils.time import datetime_to_timestamp, now
from racetrack_commons.deploy.resource import fatman_resource_name
from racetrack_commons.entities.dto import FatmanDto, FatmanStatus
from racetrack_client.log.logs import get_logger

from plugin_config import InfrastructureConfig

logger = get_logger(__name__)


class DockerDaemonMonitor(FatmanMonitor):
    """Discoverer listing fatman workloads deployed on a remote docker instance"""
    def __init__(self, infrastructure_target: str, infra_config: InfrastructureConfig) -> None:
        super().__init__()
        self.infra_config = infra_config
        self.infrastructure_target = infrastructure_target

    def list_fatmen(self, config: Config) -> Iterable[FatmanDto]:
        # Heredoc to not mix quotes inside
        # Ports section needs to be last, because there were differences in outputs on developer systems:
        # One system had: 0.0.0.0:7020->7000/tcp
        # The other: 0.0.0.0:7000->7000/tcp, :::7000->7000/tcp
        cmd = f'DOCKER_HOST={self.infra_config.docker_host} ' + """
        docker ps -a --filter "name=^/fatman-" --format '{{.Names}} {{ .Label "fatman-name" }} {{ .Label "fatman-version" }} {{.Ports}}'
        """.strip()
        regex = r'(?P<resource_name>fatman-.+) (?P<fatman_name>.+) (?P<fatman_version>.+) 0\.0\.0\.0:(?P<fatman_port>\d+)->7000\/tcp'
        output = shell_output(cmd)

        assert self.infra_config.hostname, 'hostname of a docker daemon must be set'

        for line in output.splitlines():
            match = re.match(regex, line.strip())
            if match:
                resource_name = match.group('resource_name')
                fatman_name = match.group('fatman_name')
                fatman_version = match.group('fatman_version')
                fatman_port = match.group('fatman_port')

                internal_name = f'{self.infra_config.hostname}:{fatman_port}'

                fatman = FatmanDto(
                    name=fatman_name,
                    version=fatman_version,
                    status=FatmanStatus.RUNNING.value,
                    create_time=datetime_to_timestamp(now()),
                    update_time=datetime_to_timestamp(now()),
                    manifest=None,
                    internal_name=internal_name,
                    error=None,
                    infrastructure_target=self.infrastructure_target,
                )
                try:
                    fatman_url = f'http://{fatman.internal_name}'
                    quick_check_fatman_condition(fatman_url)
                    fatman_metrics = scrape_metrics(f'{fatman_url}/metrics')
                    fatman.last_call_time = read_last_call_timestamp_metric(fatman_metrics)
                except Exception as e:
                    error_details = short_exception_details(e)
                    fatman.error = error_details
                    fatman.status = FatmanStatus.ERROR.value
                    logger.warning(f'Fatman {fatman} is in bad condition: {error_details}')
                yield fatman

    def check_fatman_condition(self,
                               fatman: FatmanDto, 
                               deployment_timestamp: int = 0, 
                               on_fatman_alive: Callable = None,
                               logs_on_error: bool = True,
                               ):
        try:
            check_until_fatman_is_operational(f'http://{fatman.internal_name}', deployment_timestamp, on_fatman_alive)
        except Exception as e:
            if logs_on_error:
                logs = self.read_recent_logs(fatman)
                raise RuntimeError(f'{e}\nFatman logs:\n{logs}')
            else:
                raise RuntimeError(str(e))

    def read_recent_logs(self, fatman: FatmanDto, tail: int = 20) -> str:
        container_name = fatman_resource_name(fatman.name, fatman.version)
        return shell_output(f'DOCKER_HOST={self.infra_config.docker_host} docker logs "{container_name}" --tail {tail}')
