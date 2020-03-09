GOOS?=linux
GOARCH?=amd64

DOCKER_REGISTRY?=gcr.io
NAME=rtmp-runner
GCP_PROJECT=videocoin-network
VERSION=$$(git rev-parse --short HEAD)
IMAGE_TAG=${DOCKER_REGISTRY}/${GCP_PROJECT}/${NAME}:${VERSION}
IMAGE_TAG_STATIC=${DOCKER_REGISTRY}/${GCP_PROJECT}/${NAME_STATIC}:${VERSION}

ENV?=dev

.PHONY: deploy

default: build

version:
	@echo ${VERSION}

docker-build:
	docker build -t ${IMAGE_TAG} -f Dockerfile .

docker-push:
	@echo "==> Pushing ${NAME} docker image..."
	docker push ${IMAGE_TAG}

docker-pull:
	@echo "==> Pulling ${NAME} docker image..."
	docker pull ${IMAGE_TAG}

docker-run:
	docker run -p 8080:8080 ${IMAGE_TAG} python3 manage.py runserver 0.0.0.0:8080 --settings=project.settings

release: docker-build docker-push