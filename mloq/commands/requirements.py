from pathlib import Path
import tempfile
from typing import Iterable, List, Union

import click
from omegaconf import DictConfig

from mloq.command import Command
from mloq.files import (
    data_science_req,
    data_viz_req,
    dogfood_req,
    File,
    pytorch_req,
    requirements,
    tensorflow_req,
)
from mloq.params import config_group, MultiChoiceParam


REQUIREMENTS_FILES = [pytorch_req, data_science_req, data_viz_req, tensorflow_req]

_REQUIREMENTS = [
    MultiChoiceParam(
        "requirements",
        text="Project requirements",
        choices=["data-science", "data-viz", "torch", "tensorflow", "none"],
    ),
]


class RequirementsCMD(Command):
    name = "requirements"
    files = tuple(REQUIREMENTS_FILES)
    CONFIG = config_group("REQUIREMENTS", _REQUIREMENTS)
    REQUIREMENTS_ALIASES = {
        data_science_req: ["data-science", "datascience", "ds"],
        pytorch_req: ["pytorch", "torch"],
        tensorflow_req: ["tensorflow", "tf"],
        data_viz_req: ["data-visualization", "data-viz", "data-vis", "dataviz", "datavis"],
    }

    def __init__(self, *args, **kwargs):
        super(RequirementsCMD, self).__init__(*args, **kwargs)
        self._temp_dir = tempfile.TemporaryDirectory()
        reqs_src = Path(self._temp_dir.name) / "requirements.txt"
        self._reqs_file = File(
            name=requirements.name,
            src=reqs_src,
            dst=requirements.dst,
            is_static=requirements.is_static,
            description=requirements.description,
        )
        self.files = tuple(list(self.files) + [self._reqs_file])

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._temp_dir.cleanup()
        return super(RequirementsCMD, self).__exit__(exc_type, exc_val, exc_tb)

    @classmethod
    def get_aliased_requirements_file(cls, option: str) -> File:
        """Get requirement file from aliased name."""
        for file, valid_alias in cls.REQUIREMENTS_ALIASES.items():
            if option in valid_alias:
                return file
        if option == "dogfood":
            return dogfood_req
        raise KeyError(
            f"{option} is not a valid name. Valid aliases are {cls.REQUIREMENTS_ALIASES}",
        )

    @classmethod
    def read_requirements_file(cls, option: str) -> str:
        """Return the content of the target requirements file form an aliased name."""
        req_file = cls.get_aliased_requirements_file(option)
        with open(req_file.src, "r") as f:
            return f.read()

    @classmethod
    def compose_requirements(cls, options: Iterable[str]) -> str:
        """
        Return the content requirements.txt file with pinned dependencies.

        The returned string contains the combined dependencies\
         for the different options sorted alphabetically.

        Args:
            options: Iterable containing the aliased names of the target \
                     dependencies for the project.

        Returns:
            str containing the pinned versions of all the selected requirements.
        """
        requirements_text = ""
        for i, opt in enumerate(options):
            pref = "\n" if i > 0 else ""  # Ensure one requirement per line
            requirements_text += pref + cls.read_requirements_file(opt)
        # Sort requirements alphabetically
        requirements_text = "\n".join(sorted(requirements_text.split("\n"))).lstrip("\n")
        return requirements_text

    def parse_config(self) -> DictConfig:
        value = self.CONFIG.requirements(self.record.config, self.interactive)
        self.record.config.requirements = value
        return self.record.config

    def interactive_config(self) -> DictConfig:
        """Generate the configuration of the project interactively."""
        click.echo("Please specify the requirements of the project as a comma separated list.")
        click.echo("Available values:")
        click.echo(
            "    data-science: Common data science libraries such as numpy, pandas, sklearn...",
        )
        click.echo(
            (
                "    data-viz: Visualization libraries such as holoviews, ",
                "bokeh, plotly, matplotlib...",
            )
        )
        click.echo("    pytorch: Latest version of pytorch, torchvision and pytorch_lightning")
        click.echo("    tensorflow: ")  # , data-viz, torch, tensorflow}")
        return self.parse_config()

    @staticmethod
    def requirements_is_empty(options: Union[List[str], str]) -> bool:
        if not options:
            return True
        if isinstance(options, str):
            options = [options]
        if None in options or "None" in options or "none" in options:
            return True
        return False

    def record_files(self) -> None:
        reqs_value = self.record.config.requirements
        if self.requirements_is_empty(reqs_value):
            return
        reqs_content = self.compose_requirements(reqs_value)
        with open(self._reqs_file.src, "w") as f:
            f.write(reqs_content)

        self.record.register_file(file=self._reqs_file, path=Path())
