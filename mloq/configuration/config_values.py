import click

from mloq.configuration.core import Config, ConfigEntry, ConfigFile, ConfigGroup, MultiChoiceConfig


project_name = ConfigEntry(
    "project_name", prompt_text="Select project name", help="Name of the project",
)

owner = ConfigEntry(
    "owner", prompt_text="Github handle of the project owner", help="Owner of the project",
)

email = ConfigEntry("email", prompt_text="Owner contact email")

author = ConfigEntry(
    "author",
    prompt_text="Author of the project",
    help="Person or entity listed as the project author in setup.py",
    default_prompt=owner,
)

copyright_holder = ConfigEntry(
    "copyright_holder",
    default_prompt=owner,
    help="Owner of the copyright of the project.",
    prompt_text="Copyright holder",
)

project_url = ConfigEntry(
    "project_url",
    default_prompt=(
        lambda: (
            None
            if (owner.value is None and project_name.value is None)
            else f"https://github.com/{owner.value}/{project_name.value}"
        )
    ),
    prompt_text="GitHub project url",
    force_prompt=True,
)
download_url = ConfigEntry(
    "download_url",
    default_prompt=lambda: (None if (project_url.value is None) else f"{project_url.value}.git"),
    prompt_text="Download url",
    force_prompt=True,
)
bot_name = ConfigEntry(
    "bot_name",
    prompt_text="Bot account to push from ci",
    help="Bot account to bump the project version",
    default_prompt=owner,
)

bot_email = ConfigEntry("bot_email", prompt_text="Bot account email", default_prompt=email)
default_branch = ConfigEntry(
    "default_branch", default_prompt="master", prompt_text="Default branch of the project"
)
license = ConfigEntry("license", help="Project license type", default_prompt="MIT")
description = ConfigEntry("description", help="Short description of the project")
python_versions = MultiChoiceConfig(
    name="python_versions",
    help="Supported python versions",
    choices=["3.6", "3.7", "3.8", "3.9"],
    default_prompt=["3.6", "3.7", "3.8", "3.9"],
    show_default="3.6, 3.7, 3.8, 3.9",
    force_prompt=True,
)

requirements = MultiChoiceConfig(
    "requirements",
    help="Requirement types of the project as a comma separated list. "
    "Available values: {data-science, data-viz, torch, tensorflow}",
    choices=["data-science", "data-viz", "torch", "tensorflow"],
    default_prompt=["data-science", "data-viz"],
    show_default="data-science, data-viz",
    force_prompt=True,
)


workflow = ConfigEntry(
    "workflow",
    help="Push workflow for Github Actions CI",
    default_prompt="python",
    type=click.Choice(["python", "dist", "none"], case_sensitive=False),
    force_prompt=True,
)

TEMPLATE = ConfigGroup(
    "template",
    [
        project_name,
        description,
        owner,
        email,
        author,
        copyright_holder,
        project_url,
        download_url,
        bot_name,
        bot_email,
        license,
        python_versions,
        default_branch,
    ],
)

MLOQFile = ConfigFile(Config([TEMPLATE, requirements, workflow]))

DEFAULT_CONFIG = dict(MLOQFile.to_dict())
