from typing import Dict, Optional

from pydantic import BaseModel, Extra


class InfrastructureConfig(BaseModel, extra=Extra.forbid, arbitrary_types_allowed=True):
    # IP or Domain name of a host, eg. "1.2.3.4"
    hostname: str
    # DOCKER_HOST variable, eg. "ssh://dev-host"
    docker_host: str


class PluginConfig(BaseModel, extra=Extra.forbid, arbitrary_types_allowed=True):
    infrastracture_targets: Dict[str, InfrastructureConfig] = None
    docker_config: Optional[str] = None
    ssh: Optional[Dict[str, str]] = None
