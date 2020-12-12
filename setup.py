from importlib.machinery import SourceFileLoader
from pathlib import Path

from setuptools import Distribution, find_packages, setup


class BinaryDistribution(Distribution):
    """
    Distribution which always forces a binary package with platform name
    Distribution which always forces a binary package with platform name
    See http://lucumr.pocoo.org/2014/1/27/python-on-wheels/
    and https://stackoverflow.com/questions/24071491/how-can-i-make-a-python-wheel-from-an-existing-native-library
    """

    def has_ext_modules(self):
        return True

    def is_pure(self):
        return False


version = SourceFileLoader(
    "mloq.version", str(Path(__file__).parent / "mloq" / "version.py"),
).load_module()

with open(Path(__file__).with_name("README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="mloq",
    description="Package for initializing ML projects following ML Ops best practices.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    version=version.__version__,
    license="MIT",
    author="Guillem Duran Ballester",
    author_email="guillem@fragile.tech",
    url="https://github.com/FragileTech/ml-ops-quickstart",
    download_url="https://github.com/FragileTech/ml-ops-quickstart.git",
    keywords=["Machine learning", "artificial intelligence"],
    tests_require=["pytest>=5.3.5", "hypothesis>=5.6.0"],
    install_requires=["ruyaml>=0.19.0", "jinja2>=2.0.0"],
    package_data={
        "": ["README.md"],
        "mloq": [
            "mloq/assets/static/repository.yml",
            "mloq/assets/static/DCO.md",
            "mloq/assets/static/.gitignore",
            "mloq/assets/templates/code_of_conduct.md",
            "mloq/assets/templates/LICENSE",
            "mloq/assets/templates/pyproject.toml",
            "mloq/assets/templates/setup.py",
            "mloq/assets/templates/Makefile",
            "mloq/assets/templates/Dockerfile",
            "mloq/assets/templates/MLproject",
            "mloq/assets/templates/README.md",
            "mloq/assets/workflows/bump-version.yml",
            "mloq/assets/workflows/lint-and-test.yml",
            "mloq/assets/workflows/test-docker.yml",
            "mloq/assets/static/__init__.py",
            "mloq/assets/static/__main__.py",
            "mloq/assets/static/version.py",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries",
    ],
    distclass=BinaryDistribution,
)
