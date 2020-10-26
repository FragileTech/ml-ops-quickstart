from importlib.machinery import SourceFileLoader
from pathlib import Path

from setuptools import find_packages, setup


version = SourceFileLoader(
    "%PROJECT_NAME.version", str(Path(__file__).parent / "%PROJECT_NAME" / "version.py"),
).load_module()

with open(Path(__file__).with_name("README.md"), encoding="utf-8") as f:
    long_description = f.read()

# Module-specific dependencies.
extras = {
    "atari": ["atari-py==0.1.1", "opencv-python", "gym", "pillow-simd", "plangym>=0.0.7"],
    "dataviz": [
        "matplotlib",
        "bokeh<2.0.0",
        "pandas",
        "panel",
        "holoviews",
        "hvplot",
        "plotly",
        "streamz",
        "param",
        "selenium",
        "pyarrow",
    ],
    "test": ["pytest>=5.3.5", "hypothesis==5.6.0"],
    "ray": ["ray", "setproctitle"],
}

# Meta dependency groups.
extras["all"] = [item for group in extras.values() for item in group]

setup(
    name="%PROJECT_NAME",
    description="%DESCRIPTION",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    version=version.__version__,
    license="%LICENSE",
    author="%AUTHOR",
    author_email="%EMAIL",
    url="%URL",
    download_url="%URL",
    keywords=["Machine learning", "artificial intelligence"],
    tests_require=["pytest>=5.3.5", "hypothesis>=5.6.0"],
    extras_require=extras,
    install_requires=[],
    package_data={"": ["README.md"]},
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
