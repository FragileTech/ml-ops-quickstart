"""This module defines common functionality for rendering and writing File templates."""
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader, select_autoescape

from mloq.directories import read_file
from mloq.files import File, TEMPLATES_PATH, WORKFLOWS_PATH


jinja_env = Environment(
    loader=FileSystemLoader([str(TEMPLATES_PATH), str(WORKFLOWS_PATH)]),
    autoescape=select_autoescape(["html", "xml"]),
)


def render_template(file: File, params: Dict[str, Any]) -> str:
    """
    Render a jinja template with the provided parameter dict.

    Args:
        file: File object representing the jinja template that will be rendered.
        params: Dictionary containing the parameters key and corresponding values \
                that will be used to render the template.

    Returns:
        String containing the rendered template.
    """
    if file.is_static:
        return read_file(file)
    template = jinja_env.get_template(str(file.name))
    return template.render(**params)


def write_template(file: File, params, path, override: False):
    """
    Create new file containing the rendered template found in source_path.

    Args:
        file: File object representing the jinja template that will be rendered.
        params: Dictionary containing the parameters key and corresponding values \
                that will be used to render the templates.
        path: Absolute path to the folder containing the target templates.
        override: If False, copy the file if it does not already exists in the \
                  target path. If True, override the target file if it is already present.

    Returns:
        None.
    """
    if not override and (path / file.dst).exists():
        print(f"file {file.name} not written: override {override} |cond: {file.src.exists()}")
        return
    rendered = render_template(file, params)
    with open(path / file.dst, "w") as f:
        f.write(rendered)
