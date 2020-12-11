current_dir = $(shell pwd)

PROJECT = mltemplate
DOCKER_ORG = fragile
VERSION ?= latest
UBUNTU_NAME = $(lsb_release -s -c)
# Project usage commands
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


# Installation commands used by Dockerfiles
# Install system packages
.PHONY: install-common-dependencies
install-common-dependencies:
	apt-get update && \
	apt-get install -y --no-install-suggests --no-install-recommends \
		ca-certificates locales pkg-config apt-utils gcc g++ wget make cmake git curl flex ssh gpgv \
		libffi-dev libjpeg-turbo-progs libjpeg8-dev libjpeg-turbo8 libjpeg-turbo8-dev gnupg2 \
		libpng-dev libpng16-16 libglib2.0-0 bison gfortran lsb-release \
		libsm6 libxext6 libxrender1 libfontconfig1 libhdf5-dev libopenblas-base libopenblas-dev \
		libfreetype6 libfreetype6-dev zlib1g-dev zlib1g xvfb python-opengl ffmpeg && \
	ln -s /usr/lib/x86_64-linux-gnu/libz.so /lib/ && \
	ln -s /usr/lib/x86_64-linux-gnu/libjpeg.so /lib/ && \
	echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
	locale-gen && \
	wget -O - https://bootstrap.pypa.io/get-pip.py | python3 && \
	rm -rf /var/lib/apt/lists/* && \
	echo '#!/bin/bash\n\\n\echo\n\echo "  $@"\n\echo\n\' > /browser && \
	chmod +x /browser

# Install Python 3.7
.PHONY: install-python3.8
install-python3.8:
	apt-get install -y --no-install-suggests --no-install-recommends \
		python3.8 python3.8-dev python3-distutils python3-setuptools libhdf5-103


# Install phantomjs for holoviews image save
.PHONY: install-phantomjs
install-phantomjs:
	curl -sSL https://deb.nodesource.com/gpgkey/nodesource.gpg.key | apt-key add - && \
	echo "deb https://deb.nodesource.com/node_10.x ${UBUNTU_NAME} main" | tee /etc/apt/sources.list.d/nodesource.list && \
	echo "deb-src https://deb.nodesource.com/node_10.x ${UBUNTU_NAME} main" | tee -a /etc/apt/sources.list.d/nodesource.list && \
	apt-get update && apt-get install -y nodejs && \
	cat /etc/apt/sources.list.d/nodesource.list && \
	npm install phantomjs --unsafe-perm && \
	npm install -g phantomjs-prebuilt --unsafe-perm

.PHONY: remove-dev-packages
remove-dev-packages:
	pip3 uninstall -y cython && \
	apt-get remove -y cmake pkg-config flex bison curl libpng-dev \
		libjpeg-turbo8-dev zlib1g-dev libhdf5-dev libopenblas-dev gfortran \
		libfreetype6-dev libjpeg8-dev libffi-dev && \
	apt-get autoremove -y && \
	apt-get clean && \
	rm -rf /var/lib/apt/lists/*
