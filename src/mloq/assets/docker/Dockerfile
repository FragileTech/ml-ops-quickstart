FROM {{ docker.base_image }}
{% if docker.jupyter %}ARG JUPYTER_PASSWORD="{{docker.jupyter_password}}"{% endif %}
ENV BROWSER=/browser \
    LC_ALL=en_US.UTF-8 \
    LANG=en_US.UTF-8
COPY Makefile.docker Makefile
COPY . {{ docker.project_name }}/

RUN apt-get update && \
	apt-get install -y --no-install-suggests --no-install-recommends make cmake && \
    make install-python{{docker.python_version}} && \
    make install-common-dependencies && \
    make install-python-libs

RUN cd {{docker.project_name}} \
    && python3 -m pip install -U pip \
    {% if docker.lint %}&& pip3 install -r requirements-lint.txt  \{% endif %}
    {% if docker.test %}&& pip3 install -r requirements-test.txt  \{% endif %}
    && pip3 install -r requirements.txt  \
    {% if docker.jupyter %}&& pip3 install ipython jupyter \{% endif %}
    && pip3 install -e . \
    && git config --global init.defaultBranch master \
    && git config --global user.name "Whoever" \
    && git config --global user.email "whoever@fragile.tech"
{{ docker.extra }}
RUN make remove-dev-packages

{% if docker.jupyter %}RUN mkdir /root/.jupyter && \
    echo 'c.NotebookApp.token = "'${JUPYTER_PASSWORD}'"' > /root/.jupyter/jupyter_notebook_config.py
CMD jupyter notebook --allow-root --port 8080 --ip 0.0.0.0
{% endif %}