current_dir = $(shell pwd)

PROJECT = {{project.project_name}}
{% if project.tests %}n ?= auto{% endif %}
{% if docker.makefile %}DOCKER_ORG = {{docker.docker_org}}
DOCKER_TAG ?= ${PROJECT}
VERSION ?= latest{% endif %}

{% if lint.makefile %}.POSIX:
style:
	black .
	isort .

.POSIX:
check:
	!(grep -R /tmp tests)
	flakehell lint src/${PROJECT}
	pylint src/${PROJECT}
	black --check src/${PROJECT}{% endif %}
{% if project.tests %}
.PHONY: test
test:
	find -name "*.pyc" -delete
	pytest -n $n -s -o log_cli=true -o log_cli_level=info

.PHONY: test-codecov
test-codecov:
	find -name "*.pyc" -delete
	pytest -n $n -s -o log_cli=true -o log_cli_level=info --cov=./src/{{project.project_name}} --cov-report=xml --cov-config=pyproject.toml{% endif %}
{% if docker.makefile %}
.PHONY: docker-shell
docker-shell:
	docker run --rm {% if docker.cuda %}--gpus all {% endif %}-v ${current_dir}:/${PROJECT} --network host -w /${PROJECT} -it ${DOCKER_ORG}/${PROJECT}:${VERSION} bash

.PHONY: docker-notebook
docker-notebook:
	docker run --rm {% if docker.cuda %}--gpus all {% endif %}-v ${current_dir}:/${PROJECT} --network host -w /${PROJECT} -it ${DOCKER_ORG}/${PROJECT}:${VERSION}

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
{% endif %}