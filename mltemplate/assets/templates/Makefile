current_dir = $(shell pwd)

PROJECT = {project_name}
DOCKER_ORG = {docker_org}
VERSION ?= latest

.POSIX:
check:
	!(grep -R /tmp ${PROJECT}/tests)
	flakehell lint ${PROJECT}
	pylint ${PROJECT}
	black --check ${PROJECT}

.PHONY: test
test:
	find -name "*.pyc" -delete
	pytest -s

.PHONY: docker-test
docker-test:
	find -name "*.pyc" -delete
	docker run --rm -it --network host -w /${PROJECT} --entrypoint python3 ${DOCKER_ORG}/${PROJECT}:${VERSION} -m pytest


.PHONY: docker-build
docker-build:
	docker build --pull -t ${DOCKER_ORG}/${PROJECT}:${VERSION} .

.PHONY: docker-push
docker-push:
	docker push ${DOCKER_ORG}/${PROJECT}:${VERSION}