"""This module defines common functionality for rendering and writing File templates."""
from pathlib import Path
from typing import Union

from jinja2 import Environment, FileSystemLoader, select_autoescape

from mloq import _logger
from mloq.config import Config
from mloq.directories import read_file
from mloq.files import File, TEMPLATES_PATH, WORKFLOWS_PATH


jinja_env = Environment(
    loader=FileSystemLoader([str(TEMPLATES_PATH), str(WORKFLOWS_PATH)]),
    autoescape=select_autoescape(["html", "xml"]),
)


def render_template(file: File, template: Config) -> str:
    """
    Render a jinja template with the provided parameter dict.

    Args:
        file: File object representing the jinja template that will be rendered.
        template: Dictionary containing the parameters key and corresponding values \
                that will be used to render the template.

    Returns:
        String containing the rendered template.
    """
    if file.is_static:
        return read_file(file)
    jinja_template = jinja_env.get_template(str(file.name))
    return jinja_template.render(**template)


def write_template(file: File, template: Config, path: Union[Path, str], override: bool = False):
    """
    Create new file containing the rendered template found in source_path.

    Args:
        file: File object representing the jinja template that will be rendered.
        template: Dictionary containing the parameters key and corresponding values \
                that will be used to render the templates.
        path: Absolute path to the folder containing the target templates.
        override: If False, copy the file if it does not already exists in the \
                  target path. If True, overwrite the target file if it is already present.

    Returns:
        None.
    """
    path = Path(path)
    if not override and (path / file.dst).exists():
        _logger.debug(f"file {file.name} already exists. Skipping")
        return
    rendered = render_template(file, template)
    with open(path / file.dst, "w") as f:
        f.write(rendered)
