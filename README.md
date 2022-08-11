# Racetrack Plugin: Docker Daemon Deployer

A Racetrack plugin allowing to deploy workloads to remote Docker Daemon

## Setup
1. Activate the plugin in Racetrack, 
  add the following to your Lifecycle configuration (in kustomize ConfigMap):

```yaml
plugins:
- name: docker-daemon-deployer
  git_remote: https://github.com/TheRacetrack/plugin-docker-daemon-deployer
  git_ref: '1.0.0'
  git_directory: docker-daemon-deployer

```

2. Provide TLS certificates for communication between docker daemon server and client,
  put them into `certs` directory and mount it as a volume (eg. `/certs`) in `lifecycle` and `lifecycle-supervisor` containers:  
  - ca.pem
  - cert.pem
  - key.pem

3. Configure these environment variables in `lifecycle` and `lifecycle-supervisor` containers:  
  - DOCKER_HOST: tcp://1.2.3.4:2376
  - DOCKER_TLS_VERIFY: '1'
  - DOCKER_CERT_PATH: /certs
  - DOCKER_DAEMON_HOST_IP: '1.2.3.4'
