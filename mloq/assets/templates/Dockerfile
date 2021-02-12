FROM {{ docker_image }}
ARG JUPYTER_PASSWORD="{{jupyter_password}}"
ENV BROWSER=/browser \
    LC_ALL=en_US.UTF-8 \
    LANG=en_US.UTF-8

COPY . {{project_name}}/

RUN cd {{project_name}} \
    && python3 -m pip install -U pip \
    && pip3 install -r requirements-lint.txt  \
    && pip3 install -r requirements-test.txt  \
    && pip3 install -r requirements.txt  \
    && pip install ipython jupyter \
    && pip3 install -e . \
    && git config --global init.defaultBranch master \
    && git config --global user.name "Whoever" \
    && git config --global user.email "whoever@fragile.tech"
RUN make remove-dev-packages
RUN mkdir /root/.jupyter && \
    echo 'c.NotebookApp.token = "'${JUPYTER_PASSWORD}'"' > /root/.jupyter/jupyter_notebook_config.py
CMD jupyter notebook --allow-root --port 8080 --ip 0.0.0.0