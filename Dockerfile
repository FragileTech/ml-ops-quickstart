FROM fragiletech/ubuntu20.04-base-py38
ARG JUPYTER_PASSWORD=""
ENV BROWSER=/browser \
    LC_ALL=en_US.UTF-8 \
    LANG=en_US.UTF-8

COPY Makefile Makefile
COPY requirements.txt requirements.txt
COPY requirements-lint.txt requirements-lint.txt
COPY requirements-test.txt requirements-test.txt
COPY pyproject.toml pyproject.toml

COPY . mltemplate/

RUN cd mltemplate \
    && python3 -m pip install -U pip \
    && pip3 install -r requirements-lint.txt  \
    && pip3 install -r requirements-test.txt  \
    && pip3 install -r requirements.txt  \
    && pip install ipython jupyter \
    && pip3 install -e . --no-use-pep517
RUN make remove-dev-packages
RUN mkdir /root/.jupyter && \
    echo 'c.NotebookApp.token = "'${JUPYTER_PASSWORD}'"' > /root/.jupyter/jupyter_notebook_config.py
CMD pipenv run jupyter notebook --allow-root --port 8080 --ip 0.0.0.0