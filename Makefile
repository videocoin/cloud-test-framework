GOOS?=linux
GOARCH?=amd64

DOCKER_REGISTRY?=gcr.io
NAME=tests
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
	docker run --network="host" ${IMAGE_TAG} pytest tests

run:
	cd src && pytest tests

release: docker-build docker-push