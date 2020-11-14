from importlib.machinery import SourceFileLoader
from pathlib import Path

from setuptools import find_packages, setup


version = SourceFileLoader(
    "mltemplate.version", str(Path(__file__).parent / "mltemplate" / "version.py"),
).load_module()

with open(Path(__file__).with_name("README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="mltemplate",
    description="Package for initializing ML projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    version=version.__version__,
    license="MIT",
    author="Guillem Duran Ballester",
    author_email="guillem.db@gmail.com",
    url="https://github.com/guillemdb/ml-repo-template",
    download_url="https://github.com/Guillemdb/ml-repo-template.git",
    keywords=["Machine learning", "artificial intelligence"],
    tests_require=["pytest>=5.3.5", "hypothesis>=5.6.0"],
    install_requires=["ruyaml>=0.19.0"],
    package_data={
        "": ["README.md"],
        "mltemplate": [
            "mltemplate/assets/requirements/*.txt",
            "mltemplate/assets/templates/.gitignore",
            "mltemplate/assets/templates/*.py",
            "mltemplate/assets/templates/*.md",
            "mltemplate/assets/templates/*.toml",
            "mltemplate/assets/templates/Makefile",
            "mltemplate/assets/templates/LICENSE",
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
