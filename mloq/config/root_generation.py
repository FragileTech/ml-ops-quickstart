"""Contains the functions that generate the required configuration."""
from datetime import datetime
from typing import Optional

from omegaconf import DictConfig

from mloq.config.logic import get_docker_image, load_empty_config_root
from mloq.config.params import PROJECT, TEMPLATE


def _generate_project_config(config: Optional[DictConfig] = None) -> DictConfig:
    """
    Generate a dictionary containing the necessary values to define the project root configuration.

    The generated config contains all the values defined under the project_config
    section in root.yml.

    Args:
        config: default values of the parameters.

    Returns:
        Dictionary containing the generated "project" config parameters.
    """
    project = load_empty_config_root().project
    project.update(config.project if config is not None else {})
    # Fill in the project settings
    project.open_source = PROJECT.open_source(project, False, default=True)
    project.docker = PROJECT.docker(project, False, default=True)
    project.mlflow = PROJECT.mlflow(project, False, default=False)
    return project


def _generate_template_config(config: Optional[DictConfig] = None) -> DictConfig:
    """
    Generate a dictionary containing the necessary values to customize the files generate by mloq.

    The generated config contains all the values defined under the template
    section in root.yml.

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
    config = load_empty_config_root()
    project, template = config.project, config.template
    project.update(_project)
    template.update(_template)
    # Fill in template values
    template.project_name = TEMPLATE.project_name(template, False)
    template.description = TEMPLATE.description(template, False)
    template.owner = TEMPLATE.owner(template, False)
    template.author = TEMPLATE.author(template, False, default=template.owner)
    template.email = TEMPLATE.email(template, False)
    copyright_holder = TEMPLATE.copyright_holder(template, False, default=template.owner)
    template.copyright_year = datetime.now().year
    template.copyright_holder = copyright_holder
    default_url = f"https://github.com/{template['owner']}/{template['project_name']}"
    template.project_url = TEMPLATE.project_url(template, False, default=default_url)
    versions = TEMPLATE.python_versions(template, False, default="3.6, 3.7, 3.8, 3.9")
    template.python_versions = versions
    # If project is undefined parse the full template
    if not project.open_source or project.open_source is None:
        template.license = "proprietary"
    else:
        template.license = TEMPLATE.license(template, False, default="MIT")
    if project.docker:
        base_docker = get_docker_image(config)
        if base_docker is not None:
            base_docker = TEMPLATE.docker_image(template, False, default=base_docker)
        template.docker_image = str(base_docker) if base_docker is None else base_docker
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
