current_dir = $(shell pwd)

PROJECT = mloq
DOCKER_ORG = fragile
VERSION ?= latest
UBUNTU_NAME = $(lsb_release -s -c)
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

.PHONY: pipenv-build
pipenv-build:
	# Rename pyproject.toml to avoid pep 517 errors when using pipenv
	if [ -f pyproject.toml ]; then mv pyproject.toml _pyproject.toml; fi
	rm -rf *.egg-info && rm -rf build && rm -rf __pycache__
	rm -f Pipfile && rm -f Pipfile.lock
	pipenv install --skip-lock --dev -r requirements-test.txt
	pipenv install --skip-lock --pre --dev -r requirements-lint.txt
	pipenv install --skip-lock -r requirements.txt
	pipenv install --skip-lock -e .
	pipenv lock
	if [ -f _pyproject.toml ]; then mv _pyproject.toml pyproject.toml; fi

.PHONY: pipenv-test
pipenv-test:
	find -name "*.pyc" -delete
	pipenv run pytest -s

.PHONY: test
test:
	find -name "*.pyc" -delete
	pytest -s

.PHONY: docker-test
docker-test:
	find -name "*.pyc" -delete
	docker run --rm -v $(pwd):/io --network host -w /${PROJECT} --entrypoint python3 ${DOCKER_ORG}/${PROJECT}:${VERSION} -m pytest

.PHONY: docker-build
docker-build:
	docker build --pull -t ${DOCKER_ORG}/${PROJECT}:${VERSION} .

.PHONY: docker-push
docker-push:
	docker push ${DOCKER_ORG}/${PROJECT}:${VERSION}
