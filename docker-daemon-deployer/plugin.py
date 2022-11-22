import os
from pathlib import Path
import shutil
from typing import Any, Dict

from dotenv import load_dotenv

from racetrack_client.log.logs import get_logger

logger = get_logger(__name__)

try:
    from deployer import DockerDaemonDeployer
    from monitor import DockerDaemonMonitor
    from logs_streamer import DockerDaemonLogsStreamer
except ModuleNotFoundError:
    logger.debug('Skipping Lifecycle\'s imports')


class Plugin:

    def __init__(self):

        env_file: Path = self.plugin_dir / 'config.env'
        if env_file.is_file():
            load_dotenv(env_file.as_posix())

        home_dir = Path('/home/racetrack')
        if home_dir.is_dir() and (self.plugin_dir / 'sshconfig/config').is_file():
            ssh_dir = home_dir / '.ssh'
            ssh_dir.mkdir(exist_ok=True)
            shutil.copy(self.plugin_dir / 'sshconfig/config', ssh_dir / 'config')
            shutil.copy(self.plugin_dir / 'sshconfig/docker-daemon.key', ssh_dir / 'docker-daemon.key')
            shutil.copy(self.plugin_dir / 'sshconfig/known_hosts', ssh_dir / 'known_hosts')
            (ssh_dir / 'config').chmod(0o600)
            (ssh_dir / 'docker-daemon.key').chmod(0o600)
            logger.info('Docker Daemon SSH key has been prepared')

        if home_dir.is_dir() and (self.plugin_dir / 'dockerconfig/config.json').is_file():
            docker_dir = home_dir / '.docker'
            docker_dir.mkdir(exist_ok=True)
            shutil.copy(self.plugin_dir / 'dockerconfig/config.json', docker_dir / 'config.json')
            (docker_dir / 'config.json').chmod(0o600)
            logger.info('Docker Registry config has been prepared')

    def fatman_deployers(self) -> Dict[str, Any]:
        """
        Fatman Deployers provided by this plugin
        :return dict of deployer name -> an instance of lifecycle.deployer.base.FatmanDeployer
        """
        return {
            'docker-daemon': DockerDaemonDeployer(),
        }

    def fatman_monitors(self) -> Dict[str, Any]:
        """
        Fatman Monitors provided by this plugin
        :return dict of deployer name -> an instance of lifecycle.monitor.base.FatmanMonitor
        """
        return {
            'docker-daemon': DockerDaemonMonitor(),
        }

    def fatman_logs_streamers(self) -> Dict[str, Any]:
        """
        Fatman Monitors provided by this plugin
        :return dict of deployer name -> an instance of lifecycle.monitor.base.LogsStreamer
        """
        return {
            'docker-daemon': DockerDaemonLogsStreamer(),
        }
