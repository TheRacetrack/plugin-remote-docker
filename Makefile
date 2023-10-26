bundle:
	cd src &&\
	racetrack plugin bundle --out=..

install:
	racetrack plugin install *.zip

download-docker-cli:
	curl https://download.docker.com/linux/static/stable/x86_64/docker-24.0.5.tgz --output docker.tgz
	tar -zxvf docker.tgz -C . --transform 's/^docker//' docker/docker
	rm docker.tgz

build-remote-pub:
	cd build && DOCKER_BUILDKIT=1 docker build \
		-t ghcr.io/theracetrack/plugin-remote-docker/pub-remote:latest \
		-f Dockerfile .

push-image:
	docker push ghcr.io/theracetrack/plugin-remote-docker/pub-remote:latest
