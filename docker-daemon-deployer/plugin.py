from typing import Any, Dict

from deployer import DockerDaemonDeployer
from monitor import DockerDaemonMonitor
from logs_streamer import DockerDaemonLogsStreamer


class Plugin:

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
