# Racetrack Plugin: Docker Daemon Deployer

A Racetrack plugin allowing to deploy services to remote Docker Daemon

## Setup

### Use unprotected Docker daemon socket

1.  Make a local copy of `./docker-daemon-deployer/config.env.template`,
    rename it to `./docker-daemon-deployer/config.env`
    and fill the variables:
    ```
    DOCKER_HOST=tcp://1.2.3.4:2375
    DOCKER_TLS_VERIFY='0'
    DOCKER_DAEMON_HOST_IP='1.2.3.4'
    ```

2. Install `racetrack` client and generate ZIP plugin by running `make bundle`.

3.  Activate the plugin in Racetrack Dashboard Admin page by uploading the zipped plugin file.

### Use TLS (HTTPS) to protect the Docker daemon socket

1. Provide TLS certificates for communication between docker daemon server and client,
  put them into `certs` directory and mount it as a volume (eg. `/certs`) in `lifecycle` and `lifecycle-supervisor` containers:  
  - ca.pem
  - cert.pem
  - key.pem

2.  Make a local copy of `./docker-daemon-deployer/config.env.template`,
    rename it to `./docker-daemon-deployer/config.env`
    and fill the variables:
    ```
    DOCKER_HOST=tcp://1.2.3.4:2376
    DOCKER_TLS_VERIFY='1'
    DOCKER_CERT_PATH=/certs
    DOCKER_DAEMON_HOST_IP='1.2.3.4'
    ```

3.  Install `racetrack` client and generate ZIP plugin by running `make bundle`.

4.  Activate the plugin in Racetrack Dashboard Admin page by uploading the zipped plugin file.

### Use SSH to protect the Docker daemon socket

1.  Make a local copy of `./docker-daemon-deployer/config.env.template`,
    rename it to `./docker-daemon-deployer/config.env`
    and fill the variables:
    ```
    DOCKER_HOST=ssh://dev-host
    DOCKER_DAEMON_HOST_IP=1.2.3.4
    ```

2.  Put the following SSH files to `./docker-daemon-deployer/sshconfig`:
    - `config`:
    ```
    Host dev-host
      Hostname 1.2.3.4
      User racetrack
      Port 22
      IdentityFile ~/.ssh/docker-daemon.key
      Compression yes
      IdentitiesOnly yes
    ```

    - `docker-daemon.key` - the private key to log in to the host
    ```
    -----BEGIN OPENSSH PRIVATE KEY-----
    IWONTTELLYOU=
    -----END OPENSSH PRIVATE KEY-----
    ```

    - `known_hosts` - add verified fingerprint of the public key
    ```
    |1|mAUt6K1PT+7n7=|6/qMO7XBgAP6zc= ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBDv22Cz4NasgSXblP57I=
    ```

3.  Provide credentials to the Docker Registry, where Fatman images are located.
    Put the following file to `./docker-daemon-deployer/dockerconfig`:
    - `config.json`:
    ```json
    {
      "auths": {
        "registry.example.com": {
          "auth": "base64key=="
        }
      }
    }
    ```

4.  Install `racetrack` client and generate ZIP plugin by running `make bundle`.

5.  Activate the plugin in Racetrack Dashboard Admin page by uploading the zipped plugin file.

Find out more about [Protecting the Docker daemon socket](https://docs.docker.com/engine/security/protect-access/)
