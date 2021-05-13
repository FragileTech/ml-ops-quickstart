## Repository files
Set up the following common repository files personalized for your project with the values
defined in `mloq.yml`:

- [README.md](../assets/templates/README.md)
- [DCO.md](../assets/static/DCO.md)
- [CONTRIBUTING.md](../assets/templates/CONTRIBUTING.md)
- [CODE_OF_CONDUCT.md](../assets/templates/CODE_OF_CONDUCT.md)
- [LICENSE](../assets/templates/MIT_LICENSE)
- [.gitignore](../assets/static/.gitignore)

## Packaging

Automatic configuration of `pyproject.toml` and `setup.py` to distribute your project as a Python package.

## Code style
All the necessary configuration for the following tools is defined in [pyproject.toml](../assets/templates/pyproject.toml).
- [black](https://black.readthedocs.io/en/stable/?badge=stable): Automatic code formatter.
- [isort](https://pycqa.github.io/isort/): Rearrange your imports automatically.
- [flakehell](https://flakehell.readthedocs.io/): Linter tool build on top of `flake8`, `pylint` and `pycodestyle`

## Requirements
`mloq` creates three different requirements files in the root directory of the project. Each file contains pinned dependencies.

- [requirements-lint.txt](../assets/requirements/requirements-lint.txt): 
Contains the dependencies for running style check analysis and automatic formatting of the code.
- [requirements-test.txt](../assets/requirements/requirements-test.txt):

Dependencies for running pytest, hypothesis, and test coverage.
  
- `requirements.txt`: Contains different pre-configured dependencies that can be defined in `mloq.yml`. The available pre-configured dependencies are:
   * [data-science](../assets/requirements/data-science.txt): Dependencies of common data science libraries.
   * [data-visualization](../assets/requirements/data-visualization.txt): Common visualization libraries.
   * Last version of [pytorch](../assets/requirements/pytorch.txt) and [tensorflow](../assets/requirements/tensorflow.txt)
   
## Docker

A [Dockerfile](../assets/templates/Dockerfile) that builds a container on top of the FragileTech [Docker Hub](https://hub.docker.com/orgs/fragiletech/repositories) images:
- If *tensorflow* or *pytorch* are selected as requirements, the container has CUDA 11.0 installed.
- Installs all the packages listed in `requirements.txt`.
- Installs `requirements-test.txt` and `requirements-lint.txt` dependencies.
- Install a `jupyter notebook` server with a configurable password on port 8080.
- Installs the project with `pip install -e .`.

## Continuous integration using GitHub Actions
Set up automatically a continuous integration (CI) pipeline using GitHub actions with the following jobs:
![GitHub Actions pipeline](../../images/ci_python.png)

Automatic build and tests:

- **Style Check**: Run `flake8` and `black --check` to ensure a consistent code style.
- **Pytest**: Test the project using pytest on all supported Python versions and output a code coverage report.
- **Test-docker**: Build the project's Docker container and run the tests inside it.
- **Build-pypi**: Build the project and upload it to [Test Pypi](https://test.pypi.org/) with a version tag unique to each commit.
- **Test-pypi**: Install the project from Test Pypi and run the tests using pytest.
- **Bump-version**: Automatically bump the project version and create a tag in the repository every time the default branch is updated.

Deploy each new version:
- **Push-docker-container**: Upload the project's Docker container to [Docker Hub](https://hub.docker.com/).
- **Release-package**: Upload to [Pypi](https://pypi.org/) the source of the project and the corresponding wheels.

## Testing
The last versions of `pytest`, `hypothesis`, and `pytest-cov` can be found in `requirements-test.txt`.

The folder structure for the library and tests is created.

## Project Makefile
A `Makefile` will be created in the root directory of the project. It contains the following commands:

- `make style`: Run `isort` and `black` to automatically arrange the imports and format the project.
- `make check`: Run `flakehell` and check black style. If it raises any error the CI will fail.
- `make test`: Clear the tests cache and run pytest.
- `make pipenv-install`: Install the project in a new Pipenv environment and create a new `Pipfile` and `Pipfile.lock`.
- `make pipenv-test`: Run pytest inside the project's Pipenv.
- `make docker-build`: Build the project's Docker container.
- `make docker-test`: Run pytest inside the projects docker container.
- `make docker-shell`: Mount the current project as a docker volume and open a terminal in the project's container.
- `make docker-notebook`: Mount the current project as a docker volume and open a jupyter notebook in the project's container. 
  It exposes the notebook server on the port `8080`.