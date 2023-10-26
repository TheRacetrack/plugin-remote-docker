FROM ghcr.io/theracetrack/racetrack/pub:latest

RUN apk --update add tar curl

# download docker CLI
RUN (mkdir -p /opt && cd /opt \
    && curl https://download.docker.com/linux/static/stable/x86_64/docker-24.0.5.tgz --output /opt/docker.tgz \
    && tar -zxvf /opt/docker.tgz -C . --transform 's/^docker//' docker/docker \
    && rm /opt/docker.tgz)
