# Pytest and code coverage
install_python_project = [
    "pip install --upgrade pip cython coverage[toml] codecov pytest ipython pipenv",
    "pipenv install .",
    'find . -wholename "*/tests/*" -type d -exec chmod 555 {} \\;',
]

coverage_script = [
    "coverage run --concurrency=multiprocessing -m pytest .",
    "travis_retry coverage combine",
]
# Bump version
bump_version_install = [
    'git config --global user.name "{bot_name}"',
    'git config --global user.email "{bot_email}"',
    "pip install bump2version",
]
bump_version_script = [
    "set -e",
    "git pull --no-edit origin master",
    "version_file={project_name}/version.py",
    'current_version=$(grep __version__ $version_file | cut -d\\" -f2)',
    "bumpversion --tag --current-version $current_version --commit patch $version_file",
    "git remote add {bot_name}-remote "
    "https://{bot_name}:${GITHUB_TOKEN}@github.com/$TRAVIS_REPO_SLUG",
    "git push --tags {bot_name}-remote HEAD:master",
    "set +e",
]
# Deploy to Pypi
pypi_install = ["pip install --upgrade pip", "pip install twine pyopenssl"]
pypi_script = [
    "set -e",
    'test "v$(python3 setup.py --version)" == "$TRAVIS_TAG"',
    "python3 setup.py bdist_wheel",
    "set +e",
]
pypi_deploy_script = "twine upload dist/*.whl -u $PYPI_LOGIN -p $PYPI_PASS"
# Deploy to dockerhub
dockerhub_install = ['docker login -u "$DOCKER_USERNAME" -p "$DOCKER_PASSWORD" docker.io']
dockerhub_script = ["make docker-build VERSION=$TRAVIS_TAG"]
dockerhub_deploy_script = "make docker-push VERSION=$TRAVIS_TAG"
# Docker test
docker_test_script = ["make docker-build", "make docker-test"]
# Style check
style_install = ["pip install -r requirements-lint.txt"]
style_script = ["make check"]
