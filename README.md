# Racetrack Plugin: Remote Docker Daemon Infrastructure

A Racetrack plugin allowing to deploy services to remote Docker Daemon

## Setup

1.  Install [racetrack client](https://pypi.org/project/racetrack-client/) and generate ZIP plugin by running:
    ```shell
    make bundle
    ```

2.  Activate the plugin in Racetrack Dashboard Admin page by uploading the zipped plugin file:
    ```shell
    racetrack plugin install remote-docker-*.zip
    ```

3.  Download docker client and keep it in the working directory:
    ```shell
    mkdir -p ~/racetrack
    cd ~/racetrack
    curl https://download.docker.com/linux/static/stable/x86_64/docker-24.0.5.tgz --output docker.tgz
    tar -zxvf docker.tgz -C . --transform 's/^docker//' docker/docker
    rm docker.tgz
    ```
    This binary will be mounted to the remote Pub container.

4.  Install Racetrack's Pub gateway on a remote host, which will dispatch the traffic to the local jobs.
    Generate a strong password that will be used as a token to authorize only the requests coming from the master Racetrack:
    ```shell
    REMOTE_GATEWAY_TOKEN='5tr0nG_PA55VoRD'
    IMAGE=ghcr.io/theracetrack/racetrack/pub:latest
    DOCKER_GID=$((getent group docker || echo 'docker:x:0') | cut -d: -f3)
    
    mkdir -p .docker
    chmod 777 .docker
    
    docker network create racetrack_default || true
    docker pull $IMAGE
    docker rm -f pub-remote || true
    docker run -d \
      --name=pub-remote \
      --user=100000:$DOCKER_GID \
      --env=AUTH_REQUIRED=true \
      --env=AUTH_DEBUG=true \
      --env=PUB_PORT=7105 \
      --env=REMOTE_GATEWAY_MODE=true \
      --env=REMOTE_GATEWAY_TOKEN="$REMOTE_GATEWAY_TOKEN" \
      -p 7105:7105 \
      --volume "/var/run/docker.sock:/var/run/docker.sock" \
      --volume "`pwd`/docker:/opt/docker" \
      --volume "`pwd`/.docker:/.docker" \
      --restart=unless-stopped \
      --network="racetrack_default" \
      --add-host host.docker.internal:host-gateway \
      $IMAGE
    ```

5.  Go to Racetrack's Dashboard, Administration, Edit Config of the plugin.
    Prepare the following data:
    
    - Host IP or DNS hostname
    - Credentials to the Docker Registry, where Job images will be located.

    Save the YAML configuration of the plugin:
    ```yaml
    infrastructure_targets:
      docker-daemon-1:
        remote_gateway_url: 'http://1.2.3.4:7105/pub'
        remote_gateway_token: '5tr0nG_PA55VoRD'

    docker: 
      docker_registry: 'docker.registry.example.com'
      username: 'DOCKER_USERNAME'
      password: 'READ_WRITE_TOKEN'
    ```
