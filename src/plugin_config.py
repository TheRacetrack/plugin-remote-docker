from pydantic import BaseModel, Extra


class InfrastructureConfig(BaseModel, extra=Extra.forbid, arbitrary_types_allowed=True):
    # IP or Domain name of a host, eg. "1.2.3.4"
    hostname: str
    # DOCKER_HOST variable, eg. "ssh://dev-host"
    docker_host: str
    remote_gateway_url: str | None = None
    remote_gateway_token: str | None = None


class PluginConfig(BaseModel, extra=Extra.forbid, arbitrary_types_allowed=True):
    infrastructure_targets: dict[str, InfrastructureConfig] = None
    docker_config: str | None = None
    ssh: dict[str, str] | None = None
