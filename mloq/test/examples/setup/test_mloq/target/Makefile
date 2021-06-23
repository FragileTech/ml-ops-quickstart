current_dir = $(shell pwd)

PROJECT = mloqq
DOCKER_ORG = FragileTech  # TODO: evaluate if this is the right way
DOCKER_TAG ?= ${PROJECT}
VERSION ?= latest
n ?= auto

.POSIX:
style:
	black .
	isort .

.POSIX:
check: style
	!(grep -R /tmp ${PROJECT}/tests)
	flakehell lint ${PROJECT}
	pylint ${PROJECT}
	black --check ${PROJECT}

.PHONY: test
test:
	find -name "*.pyc" -delete
	pytest -n $n -s -o log_cli=true -o log_cli_level=info

.PHONY: test-codecov
test-codecov:
	find -name "*.pyc" -delete
	pytest -n $n -s -o log_cli=true -o log_cli_level=info --cov=./ --cov-report=xml --cov-config=pyproject.toml

.PHONY: pipenv-install
pipenv-install:
	rm -rf *.egg-info && rm -rf build && rm -rf __pycache__
	rm -f Pipfile && rm -f Pipfile.lock
	pipenv install --dev -r requirements-test.txt
	pipenv install --pre --dev -r requirements-lint.txt
	pipenv install -r requirements.txt
	pipenv install -e .
	pipenv lock

.PHONY: pipenv-test
pipenv-test:
	find -name "*.pyc" -delete
	pipenv run pytest -s

.PHONY: remove-dev-packages
remove-dev-packages:
	pip3 uninstall -y cython && \
	apt-get remove -y cmake pkg-config flex bison curl libpng-dev \
		libjpeg-turbo8-dev zlib1g-dev libhdf5-dev libopenblas-dev gfortran \
		libfreetype6-dev libjpeg8-dev libffi-dev && \
	apt-get autoremove -y && \
	apt-get clean && \
	rm -rf /var/lib/apt/lists/*
