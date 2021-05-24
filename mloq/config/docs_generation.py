"""Contains the functions that generate the required configuration."""
from datetime import datetime
from typing import Optional

from omegaconf import DictConfig

from mloq.config.logic import load_empty_config_docs
from mloq.config.params import PROJECT, TEMPLATE


def _generate_project_config(config: Optional[DictConfig] = None) -> DictConfig:
    """
    Generate a dictionary containing the necessary values to define the project doc configuration.

    The generated config contains all the values defined under the project_config
    section in docs.yml.

    Args:
        config: default values of the parameters.

    Returns:
        Dictionary containing the generated "project" config parameters.
    """
    project = load_empty_config_docs().project
    project.update(config.project if config is not None else {})
    # Fill in the project settings
    project.docs = PROJECT.docs(project, False, default=True)
    project.requirements = PROJECT.requirements(project, False, default="None")
    return project


def _generate_template_config(config: Optional[DictConfig] = None) -> DictConfig:
    """
    Generate a dictionary containing the necessary values to customize the files generated by mloq.

    The generated config contains all the values defined under the template
    section in docs.yml.

    Args:
        config: default values of the parameters.

    Returns:
        Dictionary containing the generated "template" config parameters.
    """
    # Initialize configuration placeholders
    if config is not None:
        _template, _project = config.template, config.project
    else:
        _template, _project = {}, {}
    config = load_empty_config_docs()
    project, template = config.project, config.template
    project.update(_project)
    template.update(_template)
    # Fill in template values
    template.project_name = TEMPLATE.project_name(template, False)
    template.description = TEMPLATE.description(template, False)
    template.author = TEMPLATE.author(template, False)
    copyright_holder = TEMPLATE.copyright_holder(template, False, default=template.author)
    template.copyright_year = datetime.now().year
    template.copyright_holder = copyright_holder
    return template


def generate_config(config: Optional[DictConfig] = None) -> DictConfig:
    """
    Generate a dictionary containing the necessary values to customize the files generated by mloq.

    Args:
        config: default values of the parameters.

    Returns:
        Dictionary containing the generated config parameters.
    """
    return DictConfig(
        {
            "project": _generate_project_config(config=config),
            "template": _generate_template_config(config=config),
        },
    )
