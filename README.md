# Racetrack Plugin: Docker Daemon Deployer

A Racetrack plugin allowing to deploy workloads to remote Docker Daemon

## Setup
1. Create webhook for a Teams channel - 
  https://docs.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook
2. Activate the plugin in Racetrack, 
  add the following to your Lifecycle configuration (in kustomize ConfigMap):

```yaml
plugins:
- name: docker-daemon-deployer
  git_remote: https://plugin-docker-daemon-deployer:glpat-ChNPyhz5AfuRZpB5NcEJ@rep.erst.dk/git/kubernilla/racetrack/plugin-docker-daemon-deployer
  git_ref: '1.0.0'
  git_directory: docker-daemon-deployer

```