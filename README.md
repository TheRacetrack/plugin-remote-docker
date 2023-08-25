# Racetrack Plugin: Docker Daemon Infrastructure

A Racetrack plugin allowing to deploy services to remote Docker Daemon

## Setup

### Use SSH to protect the Docker daemon socket

1.  Install [racetrack client](https://pypi.org/project/racetrack-client/) and generate ZIP plugin by running:
    ```shell
    make bundle
    ```

2.  Activate the plugin in Racetrack Dashboard Admin page by uploading the zipped plugin file:
    ```shell
    racetrack plugin install docker-daemon-deployer-*.zip
    ```

3.  Install Racetrack's PUB gateway on a remote host, which will dispatch the traffic to the local jobs.
    Generate a strong password that will be used as a token to authorize only the requests coming from the master Racetrack:
    ```shell
    REMOTE_GATEWAY_TOKEN='5tr0nG_PA55VoRD'
    ```
    ```shell
    docker pull ghcr.io/theracetrack/racetrack/pub:latest
    docker rm -f pub  # make sure it's not running
    docker run -d \
      --name=pub \
      --user=100000:100000 \
      --env=AUTH_REQUIRED=true \
      --env=AUTH_DEBUG=true \
      --env=PUB_PORT=7105 \
      --env=REMOTE_GATEWAY_MODE=true \
      --env=REMOTE_GATEWAY_TOKEN='5tr0nG_PA55VoRD' \
      -p 7105:7105 \
      --restart=unless-stopped \
      --network="racetrack_default" \
      --add-host host.docker.internal:host-gateway \
      ghcr.io/theracetrack/racetrack/pub:latest
    ```

4.  Go to Racetrack's Dashboard, Administration, Edit Config of the plugin.
    Prepare the following data:
    
    - Host IP or DNS hostname
    - [`DOCKER_HOST` string](https://docs.docker.com/engine/security/protect-access/), eg. `ssh://dev-c1`
    - Credentials to the Docker Registry, where Job images will be located.
    - SSH config entry (like `~/.ssh/config`) to reach your host
    - SSH private key to log in to the host,
    - Fingerprint of the public key to be added to verified hosts.
      You can obtain it by logging in to your host and checking `~/.ssh/known_hosts`

    Save the YAML configuration of the plugin:
    ```yaml
    infrastructure_targets:
      docker-daemon-appdb:
        hostname: 1.2.3.4
        docker_host: ssh://dev-c1
        remote_gateway_url: 'http://1.2.3.4:7105'
        remote_gateway_token: '5tr0nG_PA55VoRD'

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
    
    docker: 
      docker_registry: 'docker.registry.example.com'
      username: 'DOCKER_USERNAME'
      password: 'READ_WRITE_TOKEN'
    ```

Find out more about [Protecting the Docker daemon socket](https://docs.docker.com/engine/security/protect-access/)
