# Racetrack Plugin: Docker Daemon Infrastructure

A Racetrack plugin allowing to deploy services to remote Docker Daemon

## Setup

### Use SSH to protect the Docker daemon socket

1.  Install `racetrack` client and generate ZIP plugin by running `make bundle`.

2.  Activate the plugin in Racetrack Dashboard Admin page by uploading the zipped plugin file.

3.  Go to Racetrack's Dashboard, Administration, Edit Config of the plugin.
    Prepare the following data:
    
    - Host IP or DNS hostname
    - [`DOCKER_HOST` string](https://docs.docker.com/engine/security/protect-access/), eg. `ssh://dev-c1`
    - Credentials to the Docker Registry, where Fatman images are located -
      Docker `config.json` with your auth key to the Docker registry, if you need to get the images from a private registry.
    - SSH config entry (like `~/.ssh/config`) to reach your host
    - SSH private key to log in to the host,
    - Fingerprint of the public key to be added to verified hosts.
      You can obtain it by logging in to your host and checking `~/.ssh/known_hosts`

    Save the YAML configuration:
    ```yaml
    infrastracture_targets:
      docker-daemon-appdb:
        hostname: 1.2.3.4
        docker_host: ssh://dev-c1

    docker_config: |
      {
        "auths": {
          "registry.example.com": {
            "auth": "base64key=="
          }
        }
      }

    ssh:
      config: |
        Host dev-c1
          Hostname 1.2.3.4
          User racetrack
          Port 22
          IdentityFile ~/.ssh/docker-daemon.key
          Compression yes
          IdentitiesOnly yes
      docker-daemon.key: |
        -----BEGIN OPENSSH PRIVATE KEY-----
        IWONTTELLYOU=
        -----END OPENSSH PRIVATE KEY-----
      known_hosts: |
        |1|mAUt6K1PT+7n7=|6/qMO7XBgAP6zc= ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBDv22Cz4NasgSXblP57I=
    ```

Find out more about [Protecting the Docker daemon socket](https://docs.docker.com/engine/security/protect-access/)
