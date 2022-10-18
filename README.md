# Racetrack Plugin: Docker Daemon Deployer

A Racetrack plugin allowing to deploy workloads to remote Docker Daemon

## Setup
1. Install `racetrack` client and generate ZIP plugin by running `make bundle`.

2. Activate the plugin in Racetrack Dashboard Admin page
  by uploading the zipped plugin file.

3. Provide TLS certificates for communication between docker daemon server and client,
  put them into `certs` directory and mount it as a volume (eg. `/certs`) in `lifecycle` and `lifecycle-supervisor` containers:  
  - ca.pem
  - cert.pem
  - key.pem

4. Configure these environment variables in `lifecycle` and `lifecycle-supervisor` containers:  
  - DOCKER_HOST: tcp://1.2.3.4:2376
  - DOCKER_TLS_VERIFY: '1'
  - DOCKER_CERT_PATH: /certs
  - DOCKER_DAEMON_HOST_IP: '1.2.3.4'
