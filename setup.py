"""mloq package installation metadata."""
from importlib.machinery import SourceFileLoader
from pathlib import Path

from setuptools import find_packages, setup


version = SourceFileLoader(
    "mloq.version",
    str(Path(__file__).parent / "src" / "mloq" / "version.py"),
).load_module()

with open(Path(__file__).with_name("README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="mloq",
    description="Package for initializing ML projects following ML Ops best practices.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages("src"),
    package_dir={"": "src"},
    version=version.__version__,
    license="MIT",
    author="FragileTech",
    author_email="guillem@fragile.tech",
    url="https://github.com/FragileTech/ml-ops-quickstart",
    download_url="https://github.com/FragileTech/ml-ops-quickstart/releases",
    keywords=["Machine learning", "artificial intelligence"],
    test_suite="tests",
    tests_require=["pytest>=5.3.5", "hypothesis>=5.6.0"],
    install_requires=[
        "flogging>=0.0.14",
        "jinja2>=3.0.0",
        "click>=8.0.0",
        "invoke>=1.4.1",
        "hydra-core>=1.1.1",
        "param>=1.11.0",
        "pre-commit>=2.15.0",
        "typing-extensions>=4.0.0",
    ],
    package_data={
        "": ["README.md"],
        "mloq": ["assets/**/*", "assets/**/.*", "tests/**/*", "tests/**/.*"],
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
    entry_points="""
            [console_scripts]
            mloq=mloq.cli:cli
        """,
)
