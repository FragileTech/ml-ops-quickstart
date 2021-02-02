"""Contains the functions that generate the required configuration."""
from typing import Optional

from mloq.config.logic import get_docker_image, load_empty_config
from mloq.config.params import Config, PROJECT_CONFIG, TEMPLATE


def generate_project_config(
    project_config: Optional[Config] = None,
    interactive: bool = False,
) -> Config:
    """
    Generate a dictionary containing the necessary values to define the project configuration.

    The generated config contains all the values defined under the project_config \
    section in mloq.yml.

    Args:
        project_config: dict containing the default values for the different parameters parsed.
        interactive: If True, the non-defined values can be provided from the CLI. \
                     If False, an error will be raised if a parameter is not defined \
                     as an environment variable, or it's present on the provided project dict.

    Returns:
        Dictionary containing the generated project_config parameters.
    """
    _project = project_config or {}
    project_config = load_empty_config()["project_config"]
    project_config.update(_project)
    # Fill in project values
    project_config["open_source"] = PROJECT_CONFIG["open_source"](
        project_config,
        interactive,
        default=True,
    )
    # use_docker = PROJECT_CONFIG["docker"](project_config, interactive, default=True)
    project_config["docker"] = True  # use_docker
    project_config["ci"] = PROJECT_CONFIG["ci"](project_config, interactive, default="python")
    project_config["mlflow"] = PROJECT_CONFIG["mlflow"](project_config, interactive, default=False)
    project_config["requirements"] = PROJECT_CONFIG["requirements"](
        project_config,
        interactive,
        default="None",
    )
    return project_config


def generate_template(
    template: Optional[Config] = None,
    project_config: Optional[Config] = None,
    interactive: bool = False,
) -> Config:
    """
    Generate a dictionary containing the necessary values to customize the files generate by mloq.

    The generated config contains all the values defined under the template \
    section in mloq.yml.

    Args:
        template: dict containing the default values for the different template parameters parsed.
        project_config: dict containing the default values for the project_config parameters.
        interactive: If True, the non-defined values can be provided from the CLI. \
                     If False, an error will be raised if a parameter is not defined \
                     as an environment variable, or it's present on the provided project dict.

    Returns:
        Dictionary containing the generated template parameters.
    """
    # Initialize configuration placeholders
    _template, _project = template or {}, project_config or {}
    config = load_empty_config()
    project_config, template = config["project_config"], config["template"]
    project_config.update(_project)
    template.update(_template)
    # Fill in template values
    template["project_name"] = TEMPLATE["project_name"](template, interactive)
    template["description"] = TEMPLATE["description"](template, interactive)
    template["default_branch"] = TEMPLATE["default_branch"](
        template,
        interactive,
        default="master",
    )
    template["owner"] = TEMPLATE["owner"](template, interactive)
    template["author"] = TEMPLATE["author"](template, interactive, default=template["owner"])
    template["email"] = TEMPLATE["email"](template, interactive)
    copyright_holder = TEMPLATE["copyright_holder"](
        template,
        interactive,
        default=template["owner"],
    )
    template["copyright_holder"] = copyright_holder
    default_url = f"https://github.com/{template['owner']}/{template['project_name']}"
    template["project_url"] = TEMPLATE["project_url"](template, interactive, default=default_url)
    versions = TEMPLATE["python_versions"](template, interactive, default="3.6, 3.7, 3.8, 3.9")
    template["python_versions"] = versions
    # If project is undefined parse the full template
    if project_config["ci"] or project_config["ci"] is None:
        template["bot_name"] = TEMPLATE["bot_name"](
            template,
            interactive,
            default=template["author"],
        )
        template["bot_email"] = TEMPLATE["bot_email"](
            template,
            interactive,
            default=template["email"],
        )
    if not project_config["open_source"] or project_config["open_source"] is None:
        template["license"] = "proprietary"
    else:
        template["license"] = TEMPLATE["license_type"](template, interactive, default="MIT")
    base_docker = get_docker_image(template=template, project_config=project_config)
    if base_docker is not None:
        base_docker = TEMPLATE["docker_image"](template, interactive, default=base_docker)
    template["docker_image"] = str(base_docker) if base_docker is None else base_docker
    return template
