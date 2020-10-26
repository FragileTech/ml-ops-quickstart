current_dir = $(shell pwd)

PROJECT = %PROJECT_NAME
DOCKER_ORG = %DOCKER_ORG
VERSION ?= latest

.POSIX:
check:
	!(grep -R /tmp mltemplate/test)
	flake8 --count mltemplate
	pylint mltemplate
	black --check mltemplate

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