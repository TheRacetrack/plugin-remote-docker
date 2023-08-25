from pydantic import BaseModel, Extra


class InfrastructureConfig(BaseModel, extra=Extra.forbid, arbitrary_types_allowed=True):
    # IP or Domain name of a host, e.g. "1.2.3.4"
    hostname: str
    # DOCKER_HOST variable, eg. "ssh://dev-host"
    docker_host: str
    remote_gateway_url: str | None = None
    remote_gateway_token: str | None = None


class DockerConfig(BaseModel, extra=Extra.forbid, arbitrary_types_allowed=True):
    docker_registry: str | None = None  # hostname (and port) of docker registry
    username: str | None = None
    password: str | None = None  # read-write token


class PluginConfig(BaseModel, extra=Extra.forbid, arbitrary_types_allowed=True):
    infrastructure_targets: dict[str, InfrastructureConfig] | None = None
    ssh: dict[str, str] | None = None
    docker: DockerConfig | None = None
