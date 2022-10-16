current_dir = $(shell pwd)

PROJECT = mloq
n ?= auto
DOCKER_ORG = fragiletech
DOCKER_TAG ?= ${PROJECT}
VERSION ?= latest

.POSIX:
style:
	black .
	isort .

.POSIX:
check:
	!(grep -R /tmp tests)
	flakehell lint src/${PROJECT}
	pylint src/${PROJECT}
	black --check src/${PROJECT}

.PHONY: test
test:
	find -name "*.pyc" -delete
	pytest -n $n -s -o log_cli=true -o log_cli_level=info

.PHONY: test-codecov
test-codecov:
	find -name "*.pyc" -delete
	pytest -n $n -s -o log_cli=true -o log_cli_level=info --cov=./src/mloq --cov-report=xml --cov-config=pyproject.toml

.PHONY: docker-shell
docker-shell:
	docker run --rm -v ${current_dir}:/${PROJECT} --network host -w /${PROJECT} -it ${DOCKER_ORG}/${PROJECT}:${VERSION} bash

.PHONY: docker-notebook
docker-notebook:
	docker run --rm -v ${current_dir}:/${PROJECT} --network host -w /${PROJECT} -it ${DOCKER_ORG}/${PROJECT}:${VERSION}

.PHONY: docker-build
docker-build:
	docker build --pull -t ${DOCKER_ORG}/${PROJECT}:${VERSION} .

.PHONY: docker-test
docker-test:
	find -name "*.pyc" -delete
	docker run --rm --network host -w /${PROJECT} --entrypoint python3 ${DOCKER_ORG}/${PROJECT}:${VERSION} -m pytest -n $n -s -o log_cli=true -o log_cli_level=info

.PHONY: docker-push
docker-push:
	docker push ${DOCKER_ORG}/${DOCKER_TAG}:${VERSION}
	docker tag ${DOCKER_ORG}/${DOCKER_TAG}:${VERSION} ${DOCKER_ORG}/${DOCKER_TAG}:latest
	docker push ${DOCKER_ORG}/${DOCKER_TAG}:latest
