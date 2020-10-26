current_dir = $(shell pwd)

PROJECT = %PROJECT_NAME
DOCKER_ORG = %DOCKER_ORG
VERSION ?= latest

.POSIX:
check:
	!(grep -R /tmp ./tests)
	flake8 --count %PROJECT_NAME
	pylint %PROJECT_NAME
	black --check %PROJECT_NAME

.PHONY: test
test:
	find -name "*.pyc" -delete
	pytest -s

.PHONY: docker-test
docker-test:
	find -name "*.pyc" -delete
	docker run --rm -it --network host -w /%PROJECT_NAME --entrypoint python3 %DOCKER_ORG/%PROJECT_NAME:${VERSION} -m pytest


.PHONY: docker-build
docker-build:
	docker build --pull -t %DOCKER_ORG/%PROJECT_NAME:${VERSION} .

.PHONY: docker-push
docker-push:
	docker push %DOCKER_ORG/%PROJECT_NAME:${VERSION}