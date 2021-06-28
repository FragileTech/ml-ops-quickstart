from pathlib import Path
from typing import Optional

import click
from omegaconf import DictConfig, OmegaConf

from mloq.command import Command
from mloq.commands.requirements import pytorch_req, RequirementsCMD, tensorflow_req
from mloq.files import DOCKER_PATH, file
from mloq.params import BooleanParam, config_group, ConfigParam, MultiChoiceParam


dockerfile = file("Dockerfile", DOCKER_PATH, description="Docker container for the project")
makefile_docker = file(
    "Makefile.docker", DOCKER_PATH, description="Makefile for the Docker container setup"
)
DOCKER_FILES = [dockerfile, makefile_docker]

_DOCKER = [
    BooleanParam("disable", "Disable docs command?"),
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
    name = "docker"
    files = tuple(DOCKER_FILES)
    CONFIG = config_group("DOCKER", _DOCKER)

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
        if not OmegaConf.is_missing(self.config, "cuda"):
            return self.config.cuda
        try:
            _ = self.config.requirements
        except:
            self.config.requirements = []
        return self.require_cuda_from_requirements(self.config)

    def get_base_image(self):
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
        self.config.docker_org = self.CONFIG.docker_org(self.config, self.interactive)
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
        self.record.register_file(file=dockerfile, path=Path())
        self.record.register_file(file=makefile_docker, path=Path())
