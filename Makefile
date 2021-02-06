current_dir = $(shell pwd)

PROJECT = mloq
DOCKER_ORG = fragiletech
VERSION ?= latest
UBUNTU_NAME = $(lsb_release -s -c)
n ?= auto
# Project usage commands

.POSIX:
style:
	black .
	isort .

.POSIX:
check:
	!(grep -R /tmp ${PROJECT}/tests)
	flakehell lint ${PROJECT}
	pylint ${PROJECT}
	black --check ${PROJECT}

.PHONY: pipenv-install
pipenv-install:
	rm -rf *.egg-info && rm -rf build && rm -rf __pycache__
	rm -f Pipfile && rm -f Pipfile.lock
	pipenv install --dev -r requirements-test.txt
	pipenv install --pre --dev -r requirements-lint.txt
	pipenv install -r requirements.txt
	pipenv install -e .
	pipenv lock

.PHONY: test
test:
	find -name "*.pyc" -delete
	pytest -n $n -s -o log_cli=true -o log_cli_level=info

.PHONY: pipenv-test
pipenv-test:
	find -name "*.pyc" -delete
	pipenv run pytest -s

.PHONY: docker-shell
docker-shell:
	docker run --rm -v $(pwd):/io --network host -w /${PROJECT} -it ${DOCKER_ORG}/${PROJECT}:${VERSION} bash

.PHONY: docker-notebook
docker-notebook:
	docker run --rm -v $(pwd):/io --network host -w /${PROJECT} -it ${DOCKER_ORG}/${PROJECT}:${VERSION}
