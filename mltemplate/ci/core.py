import copy
from typing import List, Set, Tuple, Union
from mltemplate.ci.yaml_order import PHASE_ORDER, sort_stages, STAGE_ORDER


def is_ci_object(x):
    return isinstance(x, (Command, Phase, Job, Stage, Pipeline))


class Command:
    """Represents a shell command or group of commands to be executed on a console."""

    def __init__(
        self,
        name: str,
        cmd: Union[str, List[str], Tuple[str]],
        as_string: bool = False,
        aliased: bool = False,
        no_format: bool = False,
    ):
        self._name = name
        self._raw = cmd
        self.as_string = as_string
        self.aliased = aliased
        self.no_format = no_format
        self._cmd = self._build_command(cmd)

    def __repr__(self):
        text = self.to_string()
        return f"{self.__class__.__name__}:\n {text}"

    @property
    def name(self):
        return self._name

    @property
    def raw(self):
        return self._raw

    @property
    def cmd(self):
        return self._cmd

    @property
    def alias_definition(self):
        return f"&_{self.name}&"

    @property
    def alias(self):
        return f"*`_{self.name}`*"

    def to_string(self, keyword=None):
        from mltemplate.ci.writers import yaml_as_string

        cmd = self.compile_aliases() if self.aliased else self.compile()
        compiled = {keyword if keyword is not None else self.name: cmd}
        alias_names = [self.name] if self.aliased else []
        text = yaml_as_string(compiled, aliases_names=alias_names)
        return text

    def compile(self, alias=None):
        if alias is not None:
            self.aliased = alias
        return self.alias if self.aliased else self.cmd

    def compile_aliases(self):
        return {self.alias_definition: self.cmd}

    def _build_command(self, cmd):
        if self.as_string and isinstance(cmd, (list, tuple)):
            cmd = " && ".join(cmd)
        return cmd


class Phase:
    def __init__(self, name, **kwargs):
        self._kwargs = kwargs
        self.name = name
        self.aliased = False

    def __repr__(self):
        from mltemplate.ci.writers import yaml_as_string

        text = yaml_as_string([self.compile()])
        return f"{self.__class__.__name__}:\n{text}"

    def compile(self, alias=None):
        return {k: c.compile(alias) if is_ci_object(c) else c for k, c in self._kwargs.items()}

    def compile_aliases(self):
        values = {}
        for k, command in self._kwargs.items():
            if is_ci_object(command) and command.aliased:
                values.update(command.compile_aliases())
        return values


class Job:
    def __init__(self, name: str, phase_order=PHASE_ORDER, **kwargs):
        self._name = name
        self._phases = kwargs
        self.phase_order = phase_order

    @property
    def name(self) -> str:
        return self._name

    @property
    def keywords(self) -> Set[str]:
        return set(self._phases.keys())

    @property
    def job_desc(self):
        return self._name.capitalize().replace("_", " ")

    def __getattr__(self, item):
        if self.valid_phase_name(item):
            return self._phases[item]
        return self.__getattribute__(item)

    def __setattr__(self, key, value):
        if self.valid_phase_name(key):
            self._phases[key] = value
        else:
            super(Job, self).__setattr__(key, value)

    def __getitem__(self, item):
        return self._phases[item]

    def __setitem__(self, key, value):
        self._phases[key] = value

    def __repr__(self):
        from mltemplate.ci.writers import yaml_as_string

        alias_names = tuple(self.aliased_names())
        text = yaml_as_string([self.compile()], aliases_names=alias_names)
        return f"{self.__class__.__name__}:\n{text}"

    def valid_phase_name(self, key):
        if key.startswith("_") or not isinstance(key, str):
            return False
        return key in self._phases

    def set_stage(self, stage: str):
        self.stage = stage

    def get(self, *args, **kwargs):
        return self._phases.get(*args, **kwargs)

    def keys(self):
        return self._phases.keys()

    def phases(self):
        return self._phases.values()

    def items(self):
        return self._phases.items()

    def aliased_phases(self):
        return (phase for phase in self.phases() if is_ci_object(phase) and phase.aliased)

    def aliased_keys(self):
        return (phase for key, phase in self.items() if is_ci_object(phase) and phase.aliased)

    def aliased_names(self):
        return [
            phase.name for phase in self.aliased_phases() if is_ci_object(phase) and phase.aliased
        ]

    def to_dict(self) -> dict:
        return copy.deepcopy(self._phases)

    def compile_aliases(self):
        aliases = {}
        for phase in self.aliased_phases():
            if is_ci_object(phase):
                aliases.update(phase.compile_aliases())
        return aliases

    def compile(self, alias=None) -> dict:
        jobs_dict = {
            kw: (phase.compile(alias) if is_ci_object(phase) else phase)
            for kw, phase in self.items()
        }
        jobs_dict["name"] = self.job_desc
        return jobs_dict


class PythonJob(Job):
    def __init__(self, **kwargs):
        super(PythonJob, self).__init__(**kwargs)

    @property
    def job_desc(self):
        if "_py" not in self.name:
            sup_name = super(PythonJob, self).job_desc
        else:
            sup_name = self.name[:-5].capitalize().replace("_", " ")
        version = self.get("python_version")
        return f"{sup_name} on python {version}" if version is not None else sup_name


class Stage:
    def __init__(self, name, jobs: List[Job]):
        self._name = name
        self._jobs = jobs

    def __repr__(self):
        from mltemplate.ci.writers import yaml_as_string

        text = yaml_as_string(self.compile(), aliases_names=self.aliased_names())
        return f"{self.__class__.__name__}:\n{text}"

    @property
    def name(self) -> str:
        return self._name

    @property
    def jobs(self) -> List[Job]:
        return self._jobs

    def set_job_stages(self, stage: str):
        for job in self.jobs:
            job.set_stage(stage)

    def aliased_names(self):
        aliases = []
        for job in self.jobs:
            aliases.extend(list(job.aliased_names()))
        return aliases

    def compile_aliases(self):
        aliases = {}
        for job in self.jobs:
            if is_ci_object(job):
                aliases.update(job.compile_aliases())
        return aliases

    def compile(self) -> List[dict]:
        return [(job.compile() if is_ci_object(job) else job) for job in self.jobs]


class Pipeline:
    def __init__(
        self, name: str, stages: List[Stage], pipeline_params=None, stage_order=STAGE_ORDER
    ):
        self._name = name
        self.stage_order = stage_order
        self.stages = sort_stages(stages)
        self.pipeline_params = dict() if pipeline_params is None else pipeline_params

    def __repr__(self):
        from mltemplate.ci.writers import yaml_as_string

        stages = {s.name: s.compile() for s in self.stages}
        text = yaml_as_string(stages, aliases_names=self.aliased_names())
        return f"{self.__class__.__name__}:\n{text}"

    @property
    def name(self) -> str:
        return self._name

    @property
    def stage_names(self):
        return [s.name for s in self.stages]

    def aliased_names(self):
        aliases = []
        for stage in self.stages:
            aliases.extend(stage.aliased_names())
        return aliases

    def compile_aliases(self):
        aliases = dict()
        for stage in self.stages:
            if is_ci_object(stage):
                aliases.update(stage.compile_aliases())
        return aliases

    def compile_jobs_dict(self, aliased=None):
        return {job.name: job.compile(aliased) for stage in self.stages for job in stage.jobs}

    def compile_stages(self, as_jobs: bool = False):
        compiled = [stage.compile() for stage in self.stages]
        if as_jobs:
            return [job for stage in compiled for job in stage]
        return compiled
