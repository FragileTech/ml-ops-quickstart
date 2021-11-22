"""Mloq docker command implementation."""
from pathlib import Path
from typing import Optional

import click
from omegaconf import DictConfig, MISSING, OmegaConf

from mloq.command import Command
from mloq.commands.requirements import (  # REQUIREMENT_CHOICES,
    pytorch_req,
    RequirementsCMD,
    tensorflow_req,
)
from mloq.config.param_patch import param
from mloq.files import DOCKER_PATH, file
from mloq.params import BooleanParam, ConfigParam, MultiChoiceParam


dockerfile = file("Dockerfile", DOCKER_PATH, description="Docker container for the project")
makefile_docker = file(
    "Makefile.docker",
    DOCKER_PATH,
    description="Makefile for the Docker container setup",
)
DOCKER_FILES = [dockerfile, makefile_docker]

_DOCKER = [
    # BooleanParam("disable", "Disable docs command?"),
    BooleanParam("cuda", "Install CUDA?"),
    ConfigParam("cuda_image_type", "Type of cuda docker container"),
    ConfigParam("cuda_version", "CUDA version installed in the container"),
    ConfigParam("ubuntu_version", "Ubuntu version of the base image"),
    ConfigParam("project_name", "Select project name"),
    ConfigParam("docker_org", "Name of your Docker organization"),
    ConfigParam("python_version", "Python version installed in the container"),
    ConfigParam("base_image", "Base Docker image used to build the container"),
    BooleanParam("test", "Install requirements-test.txt?"),
    BooleanParam("lint", "Install requirements-lint.txt?"),
    BooleanParam("jupyter", "Install a jupyter notebook server?"),
    BooleanParam("jupyter_password", "password for the Jupyter notebook server"),
    MultiChoiceParam(
        "requirements",
        text="Project requirements",
        choices=["data-science", "data-viz", "torch", "tensorflow", "none"],
    ),
]


class DockerCMD(Command):
    """Implement the functionality of the docker Command."""

    cmd_name = "docker"
    files = tuple(DOCKER_FILES)
    disable = param.Boolean(default=None, doc="Disable docker command?")
    cuda = param.Boolean(None, doc="Install CUDA?")
    cuda_image_type = param.String(MISSING, doc="Type of cuda docker container")
    cuda_version = param.String("11.2", doc="CUDA version installed in the container")
    ubuntu_version = param.String("20.04", doc="Ubuntu version of the base image")
    project_name = param.String("${globals.project_name}", doc="Select project name")
    docker_org = param.String("${globals.owner}", doc="Name of your Docker organization")
    python_version = param.String("3.8", doc="Python version installed in the container")
    base_image = param.String(MISSING, doc="Base Docker image used to build the container")
    test = param.Boolean(True, doc="Install requirements-test.txt?")
    lint = param.Boolean(True, doc="Install requirements-lint.txt?")
    jupyter = param.Boolean(True, doc="Install a jupyter notebook server?")
    jupyter_password = param.String(
        "${docker.project_name}",
        doc="password for the Jupyter notebook server",
    )
    requirements = param.List(default=["none"], doc="Project requirements")
    extra = param.String("", doc="Extra code to add to Dockerfile")
    makefile = param.Boolean(True, doc="Add docker commands to makefile")
    # requirements = param.ListSelector(
    #    default="none", doc="Project requirements", objects=REQUIREMENT_CHOICES,
    # )

    @staticmethod
    def require_cuda_from_requirements(project_config: Optional[DictConfig] = None) -> bool:
        """Return True if any of the project dependencies require CUDA."""
        project_config = {} if project_config is None else project_config
        if "requirements" not in project_config:
            return False
        options = project_config.get("requirements", [])
        if RequirementsCMD.requirements_is_empty(options):
            return False
        elif isinstance(options, str):
            options = [options]
        tf_alias = RequirementsCMD.REQUIREMENTS_ALIASES[tensorflow_req]
        torch_alias = RequirementsCMD.REQUIREMENTS_ALIASES[pytorch_req]
        for option in options:
            if option in tf_alias or option in torch_alias:
                return True
        return False

    def requires_cuda(self) -> bool:
        """Return True if the Docker container requires CUDA."""
        if not OmegaConf.is_missing(self.config, "cuda") and self.cuda is not None:
            return self.config.cuda
        try:
            _ = self.config.requirements
        except Exception:
            self.config.requirements = []
        return self.require_cuda_from_requirements(self.config)

    def get_base_image(self):
        """Return the name of the base image for the project Docker container."""
        if not OmegaConf.is_missing(self.config, "base_image"):
            return self.config.base_image
        elif self.config.cuda:
            cuda_image = (
                f"nvidia/cuda:{self.config.cuda_version}-{self.config.cuda_image_type}"
                f"-ubuntu{self.config.ubuntu_version}"
            )
            return cuda_image
        return f"ubuntu:{self.config.ubuntu_version}"

    def parse_config(self) -> DictConfig:
        """Update the configuration dictionary from the data entered by the user."""
        if self.cuda is None:
            self.cuda = self.requires_cuda()
        # FIXME: Auto inference of base image is broken (when base_image is missing)
        self.base_image = self.get_base_image()
        return super(DockerCMD, self).parse_config()

    def _____parse_config(self) -> DictConfig:
        """Update the configuration DictConfig with the Command parameters."""
        self.config.docker_org = self.CONFIG.docker_org(self.config, self.interactive).lower()
        self.config.python_version = self.CONFIG.python_version(self.config, self.interactive)
        self.config.requirements = self.CONFIG.requirements(self.config, self.interactive)
        cuda = self.CONFIG.cuda(self.config, self.interactive, default=self.requires_cuda())
        self.config.cuda = cuda
        self.config.cuda_image_type = self.CONFIG.cuda_image_type(self.config, self.interactive)
        self.config.cuda_version = self.CONFIG.cuda_version(self.config, self.interactive)
        self.config.ubuntu_version = self.CONFIG.ubuntu_version(self.config, self.interactive)
        base_image = self.get_base_image()
        self.config.base_image = self.CONFIG.base_image(
            self.config,
            self.interactive,
            default=base_image,
        )
        self.config.test = self.CONFIG.test(self.config, self.interactive)
        self.config.lint = self.CONFIG.lint(self.config, self.interactive)
        self.config.jupyter = self.CONFIG.jupyter(self.config, self.interactive)
        self.config.jupyter_password = self.CONFIG.jupyter_password(self.config, self.interactive)
        self.config.project_name = self.CONFIG.project_name(self.config, self.interactive)
        return self.record.config

    def interactive_config(self) -> DictConfig:
        """Generate the configuration of the project interactively."""
        click.echo("Provide the values to generate the project Docker container.")
        return self.parse_config()

    def record_files(self) -> None:
        """Register the files that will be generated by mloq."""
        self.record.register_file(file=dockerfile, path=Path())
        self.record.register_file(file=makefile_docker, path=Path())
