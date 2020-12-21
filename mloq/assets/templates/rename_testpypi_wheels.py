from distutils.version import StrictVersion
import os
from pathlib import Path
import sys

import requests


def get_versions(package_name):
    url = "https://test.pypi.org/pypi/%s/json" % (package_name,)
    resp = requests.get(url)
    data = resp.json()
    versions = data["releases"].keys()
    try:
        versions = sorted(versions, key=lambda x: StrictVersion(x))
    except Exception:
        versions = sorted(versions, key=str)
    return versions


def rename_wheels(new_version=None):
    dist_dir = Path(os.getcwd()) / "dist"
    for file in os.listdir(str(dist_dir)):
        version = file.split("-")[1]
        new_file = file.replace(version, new_version)
        os.rename(str(dist_dir / file), str(dist_dir / new_file))


def main():
    project = os.environ.get("PROJECT_NAME", "{{project_name}}")
    last_version = get_versions(project)[-1]
    rename_wheels(last_version)


if __name__ == "__main__":
    sys.exit(main())
