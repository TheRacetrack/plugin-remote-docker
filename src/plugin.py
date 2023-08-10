from __future__ import annotations
from pathlib import Path
from typing import Any

from racetrack_client.log.logs import get_logger
from racetrack_client.utils.datamodel import parse_yaml_file_datamodel
from lifecycle.deployer.infra_target import InfrastructureTarget

from deployer import DockerDaemonDeployer
from monitor import DockerDaemonMonitor
from logs_streamer import DockerDaemonLogsStreamer
from plugin_config import PluginConfig

logger = get_logger(__name__)


class Plugin:

    def __init__(self):
        self.plugin_config: PluginConfig = parse_yaml_file_datamodel(self.config_path, PluginConfig)
        self.docker_config_dir: str = ''

        home_dir = Path('/home/racetrack')
        if home_dir.is_dir():

            if self.plugin_config.docker_config:
                docker_dir = home_dir / '.docker-plugin'
                docker_dir.mkdir(exist_ok=True)
                dest_config_file = docker_dir / 'config.json'
                dest_config_file.write_text(self.plugin_config.docker_config)
                dest_config_file.chmod(0o600)
                self.docker_config_dir = docker_dir.as_posix()
                logger.info('Docker Registry config has been prepared')

            if self.plugin_config.ssh:
                ssh_dir = home_dir / '.ssh'
                ssh_dir.mkdir(exist_ok=True)
                
                for filename, content in self.plugin_config.ssh.items():
                    dest_file = ssh_dir / filename
                    dest_file.write_text(content)
                    dest_file.chmod(0o600)
                
                logger.info('SSH config has been prepared')
        
        self._infrastructure_targets = self.plugin_config.infrastructure_targets or {}
        infra_num = len(self._infrastructure_targets)
        logger.info(f'Docker Daemon plugin loaded with {infra_num} infrastructure targets')

    def infrastructure_targets(self) -> dict[str, Any]:
        """
        Infrastructure Targets (deployment targets) for Jobs provided by this plugin
        :return dict of infrastructure name -> an instance of lifecycle.deployer.infra_target.InfrastructureTarget
        """
        return {
            infra_name: InfrastructureTarget(
                job_deployer=DockerDaemonDeployer(infra_name, infra_config, self.docker_config_dir),
                job_monitor=DockerDaemonMonitor(infra_name, infra_config),
                logs_streamer=DockerDaemonLogsStreamer(infra_name, infra_config),
            )
            for infra_name, infra_config in self._infrastructure_targets.items()
        }
