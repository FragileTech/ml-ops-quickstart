current_dir = $(shell pwd)

PROJECT = {{project_name}}
DOCKER_ORG = {{project_org}}
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

.PHONY: pipenv-build
pipenv-build:
	# Rename pyproject.toml to avoid pep 517 errors when using pipenv
	if [ -f pyproject.toml ]; then mv pyproject.toml _pyproject.toml; fi
	rm -rf *.egg-info && rm -rf build && rm -rf __pycache__
	rm -f Pipfile && rm -f Pipfile.lock
	pipenv install --skip-lock --dev -r requirements-test.txt
	pipenv install --skip-lock --pre --dev -r requirements-lint.txt
	pipenv install --skip-lock -r requirements.txt
	pipenv install --skip-lock .
	pipenv lock
	if [ -f _pyproject.toml ]; then mv _pyproject.toml pyproject.toml; fi

.PHONY: pipenv-test
pipenv-test:
	find -name "*.pyc" -delete
	pipenv run pytest -s

.PHONY: docker-test
docker-test:
	find -name "*.pyc" -delete
	docker run --rm -it  -v $(pwd):/io --network host -w /${PROJECT} --entrypoint python3 ${DOCKER_ORG}/${PROJECT}:${VERSION} -m pytest


.PHONY: docker-build
docker-build:
	docker build --pull -t ${DOCKER_ORG}/${PROJECT}:${VERSION} .


.PHONY: remove-dev-packages
remove-dev-packages:
	pip3 uninstall -y cython && \
	apt-get remove -y cmake pkg-config flex bison curl libpng-dev \
		libjpeg-turbo8-dev zlib1g-dev libhdf5-dev libopenblas-dev gfortran \
		libfreetype6-dev libjpeg8-dev libffi-dev && \
	apt-get autoremove -y && \
	apt-get clean && \
	rm -rf /var/lib/apt/lists/*

.PHONY: docker-push
docker-push:
	docker push ${DOCKER_ORG}/${DOCKER_TAG}:${VERSION}
	docker tag ${DOCKER_ORG}/${DOCKER_TAG}:${VERSION} ${DOCKER_ORG}/${DOCKER_TAG}:latest
	docker push ${DOCKER_ORG}/${DOCKER_TAG}:latest