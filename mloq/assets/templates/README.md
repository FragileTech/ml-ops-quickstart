# {{project_name}}
[![Documentation Status](https://readthedocs.org/projects/{{project_name}}/badge/?version=latest)](https://{{project_name}}.readthedocs.io/en/latest/?badge=latest)
[![Code coverage](https://codecov.io/github/{{owner}}/{{project_name}}/coverage.svg)](https://codecov.io/github/{{owner}}/{{project_name}})
[![PyPI package](https://badgen.net/pypi/v/{{project_name}})](https://pypi.org/project/{{project_name}}/)
{% if project.docker %}[![Latest docker image](https://badgen.net/docker/pulls/{{owner}}/{{project_name}})](https://hub.docker.com/r/{{owner}}/{{project_name}}/tags)
{% endif %}[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![license: {{license}}](https://img.shields.io/badge/license-{{license}}-green.svg)](https://opensource.org/licenses/{{license}})

{{description}}