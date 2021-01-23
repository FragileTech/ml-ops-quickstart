from typing import Any, Dict, Optional

import click

from mloq.config.logic import get_docker_image, load_empty_config
from mloq.config.params import Config, PROJECT, TEMPLATE


def generate_project(project: Optional[Config] = None, interactive: bool = False):
    _project = project or {}
    project = load_empty_config()["project"]
    # Fill in project values
    project["open_source"] = PROJECT["open_source"](project, interactive, default=True)
    project["proprietary"] = PROJECT["proprietary"](project, interactive, default=False)
    project["docker"] = PROJECT["docker"](project, interactive, default=False)
    project["ci"] = PROJECT["ci"](project, interactive, default="python")
    project["mlflow"] = PROJECT["mlflow"](project, interactive, default=False)
    if interactive:
        click.echo("Please specify the requirements of the project as a comma separated list.")
        click.echo("Available values: {data-science, data-viz, torch, tensorflow}")
    project["requirements"] = PROJECT["requirements"](project, interactive, default="None")
    return project


def generate_template(
    template: Optional[Config] = None, project: Optional[Config] = None, interactive: bool = False
) -> Dict[str, Any]:
    # Initialize configuration placeholders
    _template, _project = template or {}, project or {}
    config = load_empty_config()
    project, template = config["project"], config["template"]
    project.update(_project)
    template.update(_template)
    # Fill in template values
    template["project_name"] = TEMPLATE["project_name"](template, interactive)
    template["default_branch"] = TEMPLATE["default_branch"](
        template, interactive, default="master"
    )
    template["owner"] = TEMPLATE["owner"](template, interactive)
    template["author"] = TEMPLATE["author"](template, interactive, default=template["owner"])
    template["email"] = TEMPLATE["email"](template, interactive)
    copyright_holder = TEMPLATE["copyright_holder"](
        template, interactive, default=template["owner"]
    )
    template["copyright_holder"] = copyright_holder
    default_url = f"https://github.com/{template['owner']}/{template['project_name']}"
    template["project_url"] = TEMPLATE["project_url"](template, interactive, default=default_url)
    versions = TEMPLATE["python_versions"](template, interactive, default="3.6, 3.7, 3.8, 3.9")
    template["python_versions"] = versions
    # If project is undefined parse the full template
    if project["ci"] or project["ci"] is None:
        template["bot_name"] = TEMPLATE["bot_name"](
            template, interactive, default=template["author"]
        )
        template["bot_email"] = TEMPLATE["bot_email"](
            template, interactive, default=template["email"]
        )
    if project["proprietary"]:
        template["license"] = "proprietary"
    else:
        template["license"] = TEMPLATE["license_type"](template, interactive, default="MIT")
    base_docker = get_docker_image(template=template, project=project)
    if base_docker is not None:
        base_docker = TEMPLATE["docker_image"](template, interactive, default=base_docker)
    template["docker_image"] = str(base_docker) if base_docker is None else base_docker
    return template
