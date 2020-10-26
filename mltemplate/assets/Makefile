current_dir = $(shell pwd)

PROJECT = {project_name}
DOCKER_ORG = {docker_org}
VERSION ?= latest

.POSIX:
check:
	!(grep -R /tmp {project_name}/tests)
	flake8 --count {project_name}
	pylint %PROJECT_NAME
	black --check {project_name}

.PHONY: test
test:
	find -name "*.pyc" -delete
	pytest -s

.PHONY: docker-test
docker-test:
	find -name "*.pyc" -delete
	docker run --rm -it --network host -w /{project_name} --entrypoint python3 {docker_org}/{project_name}:${VERSION} -m pytest


.PHONY: docker-build
docker-build:
	docker build --pull -t {docker_org}/{project_name}:${VERSION} .

.PHONY: docker-push
docker-push:
	docker push {docker_org}/{project_name}:${VERSION}