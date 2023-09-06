bundle:
	cd src &&\
	racetrack plugin bundle --out=..

install:
	racetrack plugin install *.zip

download-docker-cli:
	curl https://download.docker.com/linux/static/stable/x86_64/docker-24.0.5.tgz --output docker.tgz
	tar -zxvf docker.tgz -C . --transform 's/^docker//' docker/docker
	rm docker.tgz
