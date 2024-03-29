import threading
import time
from datetime import datetime, timezone
from typing import Callable

from lifecycle.infrastructure.infra_target import remote_shell
from lifecycle.monitor.base import LogsStreamer
from racetrack_client.log.logs import get_logger
from racetrack_client.utils.shell import CommandError
from racetrack_commons.deploy.resource import job_resource_name

from plugin_config import InfrastructureConfig

logger = get_logger(__name__)


class DockerDaemonLogsStreamer(LogsStreamer):
    """Source of a Job logs retrieved from a remote Docker container"""

    def __init__(self, infrastructure_target: str, infra_config: InfrastructureConfig) -> None:
        super().__init__()
        self.infra_config = infra_config
        self.infrastructure_target = infrastructure_target
        self.sessions: dict[str, bool] = {}

    def create_session(self, session_id: str, resource_properties: dict[str, str], on_next_line: Callable[[str, str], None]):
        """Start a session transmitting messages to a client."""
        job_name = resource_properties.get('job_name')
        job_version = resource_properties.get('job_version')
        tail = resource_properties.get('tail', 20)
        container_name = job_resource_name(job_name, job_version)

        def on_error(error: CommandError):
            # Negative return value is the signal number which was used to kill the process. SIGTERM is 15.
            if error.returncode != -15:  # ignore process Terminated on purpose
                logger.error(f'command "{error.cmd}" failed with return code {error.returncode}: {error.stdout}')

        def watch_logs():
            try:
                last_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                output = self.remote_shell(f'/opt/docker logs "{container_name}" --tail {tail} --until {last_time}')
                for line in filter(bool, output.splitlines()):
                    on_next_line(session_id, line)
                self.sessions[session_id] = True

                while self.sessions.get(session_id) is True:
                    now_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                    output = self.remote_shell(f'/opt/docker logs "{container_name}" --since {last_time} --until {now_time}')
                    last_time = now_time
                    for line in filter(bool, output.splitlines()):
                        on_next_line(session_id, line)
                    time.sleep(3)

            except CommandError as e:
                on_error(e)

        threading.Thread(target=watch_logs, args=(), daemon=True).start()

    def close_session(self, session_id: str):
        self.sessions.pop(session_id, None)

    def remote_shell(self, cmd: str, workdir: str | None = None) -> str:
        return remote_shell(cmd, self.infra_config.remote_gateway_url, self.infra_config.remote_gateway_token, workdir)
