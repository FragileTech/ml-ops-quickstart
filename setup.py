from importlib.machinery import SourceFileLoader
from pathlib import Path

from setuptools import find_packages, setup


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
    install_requires=["ruyaml>=0.19.0,<0.20.0", "jinja2>=2.0.0"],
    package_data={
        "": ["README.md"],
        "mloq": [
            "mloq/assets/static/repository.yml",
            "mloq/assets/static/DCO.md",
            "mloq/assets/static/.gitignore",
            "mloq/assets/templates/*.md",
            "mloq/assets/templates/MIT_LICENSE",
            "mloq/assets/templates/pyproject.toml",
            "mloq/assets/templates/Makefile",
            "mloq/assets/templates/Dockerfile",
            "mloq/assets/templates/MLproject",
            "mloq/assets/workflows/*.yml",
            "mloq/assets/requirements/*.txt",
        ],
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries",
    ],
)
