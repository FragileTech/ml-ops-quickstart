"""This module defines common functionality for rendering and writing File templates."""
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping, Union

from jinja2 import Environment, FileSystemLoader, select_autoescape
from omegaconf import DictConfig

from mloq import _logger
from mloq.files import File, read_file, TEMPLATES_PATH
from mloq.record import Ledger


jinja_env = Environment(
    loader=FileSystemLoader([str(TEMPLATES_PATH)]),
    autoescape=select_autoescape(["html", "xml"]),
    keep_trailing_newline=True,
)


def render_template(file: File, kwargs: Mapping[str, Any]) -> str:
    """
    Render a jinja template with the provided parameter dict.

    Args:
        file: File object representing the jinja template that will be rendered.
        kwargs: Dictionary containing the parameters key and corresponding values \
                that will be used to render the template.

    Returns:
        String containing the rendered template.
    """
    if file.is_static:
        return read_file(file)
    jinja_template = jinja_env.get_template(str(file.name))
    jinja_template.globals["now"] = datetime.now
    return jinja_template.render(**kwargs)


def write_template(
    file: File,
    config: DictConfig,
    path: Union[Path, str],
    ledger: Ledger,
    overwrite: bool = False,
):
    """
    Create new file containing the rendered template found in source_path.

    Args:
        file: File object representing the jinja template that will be rendered.
        config: OmegaConf dictionary containing the parameters key and corresponding values \
                that will be used to render the templates.
        path: Absolute path to the folder where the file will be written.
        ledger: Book keeper to keep track of the generated files.
        overwrite: If False, copy the file if it does not already exists in the \
                   target path. If True, overwrite the target file if it is already present.

    Returns:
        None.
    """
    if not overwrite and path.exists():
        _logger.debug(f"file {file.dst} already exists. Skipping")
        return

    ledger.register(file, description=file.description)
    rendered = render_template(file, config)
    with open(path, "w") as f:
        f.write(rendered)
