========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - |github-actions| |codecov|
    * - package
      - |version| |wheel| |supported-versions| |supported-implementations| |commits-since|
.. |docs| image:: https://readthedocs.org/projects/ml-ops-quickstart/badge/?style=flat
    :target: https://readthedocs.org/projects/ml-ops-quickstart/
    :alt: Documentation Status

.. |github-actions| image:: https://github.com/FragileTech/ml-ops-quickstart/actions/workflows/github-actions.yml/badge.svg
    :alt: GitHub Actions Build Status
    :target: https://github.com/FragileTech/ml-ops-quickstart/actions

.. |codecov| image:: https://codecov.io/gh/FragileTech/ml-ops-quickstart/branch/main/graphs/badge.svg?branch=main
    :alt: Coverage Status
    :target: https://app.codecov.io/github/FragileTech/ml-ops-quickstart

.. |version| image:: https://img.shields.io/pypi/v/mloq.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/mloq

.. |wheel| image:: https://img.shields.io/pypi/wheel/mloq.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/mloq

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/mloq.svg
    :alt: Supported versions
    :target: https://pypi.org/project/mloq

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/mloq.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/mloq

.. |commits-since| image:: https://img.shields.io/github/commits-since/FragileTech/ml-ops-quickstart/v0.1.0.svg
    :alt: Commits since latest release
    :target: https://github.com/FragileTech/ml-ops-quickstart/compare/v0.1.0...main



.. end-badges

Automate project creation following ML best practices.

* Free software: MIT license

Installation
============

::

    pip install mloq

You can also install the in-development version with::

    pip install https://github.com/FragileTech/ml-ops-quickstart/archive/main.zip


Documentation
=============


https://ml-ops-quickstart.readthedocs.io/


Development
===========

To run all the tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
