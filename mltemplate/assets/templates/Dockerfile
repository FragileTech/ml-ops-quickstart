FROM nvidia/cuda:11.0-runtime-ubuntu20.04
ARG JUPYTER_PASSWORD=""
ENV BROWSER=/browser \
    LC_ALL=en_US.UTF-8 \
    LANG=en_US.UTF-8

COPY ../../../Makefile Makefile
COPY ../../../requirements.txt requirements.txt

COPY ../../.. mltemplate/

RUN cd mltemplate && make pipenv-build && pipenv sync && pipenv install ipython jupyter
RUN make remove-dev-packages
RUN mkdir /root/.jupyter && \
    echo 'c.NotebookApp.token = "'${JUPYTER_PASSWORD}'"' > /root/.jupyter/jupyter_notebook_config.py
CMD pipenv run jupyter notebook --allow-root --port 8080 --ip 0.0.0.0