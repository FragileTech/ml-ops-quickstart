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
    install_requires=["ruyaml>=0.19.0"],
    package_data={
        "": ["README.md"],
        "mloq": [
            "mloq/assets/requirements/*.txt",
            "mloq/assets/templates/.gitignore",
            "mloq/assets/templates/*.py",
            "mloq/assets/templates/*.md",
            "mloq/assets/templates/*.toml",
            "mloq/assets/templates/Makefile",
            "mloq/assets/templates/LICENSE",
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
)
