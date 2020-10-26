import copy
from ruamel.yaml import YAML as RuamelYAML
from ruamel.yaml.compat import StringIO

from mltemplate.ci.yaml_order import sort_dict, sort_stages, ALL_ORDERS


class StringYAML(RuamelYAML):
    def dump(self, data, stream=None, **kw):
        inefficient = False
        if stream is None:
            inefficient = True
            stream = StringIO()
        RuamelYAML.dump(self, data, stream, **kw)
        if inefficient:
            return stream.getvalue()


def replace_alias(text, name):
    alias_def_src = f"'&_{name}&'"
    alias_def_tgt = f"_{name}: &_{name}"
    alias_call_src = f"'*`_{name}`*'"
    alias_call_tgt = f"*_{name}"
    text = text.replace(alias_def_src, alias_def_tgt)
    return text.replace(alias_call_src, alias_call_tgt)


def format_aliases(s, aliases_names):
    for n in aliases_names:
        s = replace_alias(s, n)
    return s


def format_output_yaml(aliases_names=None, params=None):
    aliases_names = [] if aliases_names is None else aliases_names

    def clean_yaml(s):
        s = format_aliases(s, aliases_names)
        s = fill_in_template(s, params)
        return s

    return clean_yaml


def fill_in_template(text, params=None):
    if params is not None:
        for k, v in params.items():
            key = "{%s}" % k
            text = text.replace(key, v)
    return text


def export_travis_config(path, params, aliases_names=None, template_params=None, **kwargs):
    yaml = RuamelYAML()
    yaml.indent(sequence=4, offset=2)
    with open(path, "w") as f:
        yaml.dump(
            params, f, transform=format_output_yaml(aliases_names, template_params), **kwargs
        )


def yaml_as_string(params, aliases_names=None, script_params=None):
    yaml = StringYAML()
    yaml.indent(sequence=4, offset=2)
    return yaml.dump(params, transform=format_output_yaml(aliases_names, script_params))


def gen_dict_extract(key, var):
    if hasattr(var, "iteritems"):
        for k, v in var.iteritems():
            if k == key:
                yield v
            if isinstance(v, dict):
                for result in gen_dict_extract(key, v):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in gen_dict_extract(key, d):
                        yield result


def replace_one_key(yaml: dict, old_key, new_key):
    if old_key in yaml:
        yaml[new_key] = yaml.pop(old_key)


def swap_dictionary_key(yaml: dict, key, new_key):

    for k, v in copy.deepcopy(yaml).items():
        if k == key:
            replace_one_key(yaml, key, new_key)
        if isinstance(v, dict):
            if k in yaml:
                yaml[k] = swap_dictionary_key(yaml[k], key, new_key)
        elif isinstance(v, list) and k in yaml:
            for i, d in enumerate(yaml[k]):
                if isinstance(d, dict):
                    yaml[k][i] = swap_dictionary_key(yaml[k][i], key, new_key)
    return yaml


def swap_dictionary_value(yaml: dict, key, function):
    for k, v in copy.deepcopy(yaml).items():
        if k == key:
            function(yaml, key)
        if isinstance(v, dict):
            if k in yaml:
                yaml[k] = swap_dictionary_value(yaml[k], key, function)
        elif isinstance(v, list) and k in yaml:
            for i, d in enumerate(yaml[k]):
                if isinstance(d, dict):
                    yaml[k][i] = swap_dictionary_value(yaml[k][i], key, function)
    return yaml


class PipelineToYAML:
    def __init__(
        self,
        pipeline,
        yaml_config: dict = None,
        order=ALL_ORDERS,
        template_params=None,
        default_phase_key: int = 99,
        default_stage_key: int = 3,
        default_root_key: int = 15,
    ):
        self.pipeline = pipeline
        self.template_params = template_params
        self.order = order
        self.yaml_config = yaml_config
        self.default_phase_key = default_phase_key
        self.default_stage_key = default_stage_key
        self.default_root_key = default_root_key

    def __repr__(self):
        text = yaml_as_string(self.compile(), aliases_names=self.pipeline.aliased_names())
        return f"{self.__class__.__name__}:\n{text}"

    @staticmethod
    def write_yaml(path, yaml: dict, aliases_names=None, template_params=None, **kwargs):
        return export_travis_config(
            path=path,
            params=yaml,
            aliases_names=aliases_names,
            template_params=template_params,
            **kwargs
        )

    def dump(self, path, template_params=None, **kwargs):
        template_params = self.template_params if template_params is None else template_params
        yaml = self.compile()
        return self.write_yaml(
            path=path,
            yaml=yaml,
            aliases_names=self.pipeline.aliased_names(),
            template_params=template_params,
            **kwargs
        )

    def compile_jobs(self):
        self.pipeline.stages = sort_stages(
            self.pipeline.stages, default_key=self.default_stage_key
        )
        compiled_jobs = self.pipeline.compile_stages(as_jobs=True)
        compiled_jobs = [self.format_job(job) for job in compiled_jobs]
        return compiled_jobs

    def format_job(self, job: dict):
        return sort_dict(job, default_key=self.default_phase_key)

    def compile_config(self, compiled_jobs):
        yaml = dict(self.yaml_config)
        yaml.update(self.pipeline.compile_aliases())
        return yaml

    def compile(self):
        compiled_jobs = self.compile_jobs()
        yaml = self.compile_config(compiled_jobs)
        return sort_dict(yaml, default_key=self.default_root_key)


class Travis(PipelineToYAML):
    def __init__(
        self,
        pipeline,
        yaml_config: dict = None,
        order=ALL_ORDERS,
        default_phase_key: int = 99,
        default_stage_key: int = 3,
        default_root_key: int = 15,
    ):
        yaml_config = (
            {
                "language": "python",
                "sudo": True,
                "dist": "bionic",
                "services": ["docker"],
                "cache": "pip",
                "before_cache": ["chown -R travis:travis $HOME/.cache/pip"],
                "stages": [],
                "before_install": ["env"],
                "matrix": dict(fast_finish=True, include=[]),
                "notifications": {"email": False},
            }
            if yaml_config is None
            else yaml_config
        )
        super(Travis, self).__init__(
            pipeline,
            order=order,
            default_phase_key=default_phase_key,
            default_stage_key=default_stage_key,
            default_root_key=default_root_key,
            yaml_config=yaml_config,
        )

    def compile_config(self, compiled_jobs):
        yaml = dict(self.yaml_config)
        yaml["stages"].extend(self.pipeline.stage_names)
        yaml["matrix"]["include"].extend(compiled_jobs)
        yaml.update(self.pipeline.compile_aliases())
        return yaml

    def format_job(self, job: dict):
        job = swap_dictionary_key(job, "condition", "if")
        job = swap_dictionary_key(job, "python_version", "python")
        return sort_dict(job, default_key=self.default_phase_key)


class GitLab(PipelineToYAML):
    def __init__(
        self,
        pipeline,
        yaml_config: dict = None,
        order=ALL_ORDERS,
        default_phase_key: int = 99,
        default_stage_key: int = 3,
        default_root_key: int = 15,
    ):
        default = {"image": "python:3.6", "services": ["docker", "pip"]}
        yaml_config = {"default": default, "stages": [],} if yaml_config is None else yaml_config
        super(GitLab, self).__init__(
            pipeline,
            order=order,
            default_phase_key=default_phase_key,
            default_stage_key=default_stage_key,
            default_root_key=default_root_key,
            yaml_config=yaml_config,
        )

    def compile_jobs(self):
        self.pipeline.stages = sort_stages(
            self.pipeline.stages, default_key=self.default_stage_key
        )
        compiled_jobs = self.pipeline.compile_jobs_dict()
        compiled_jobs = {k: self.format_job(job) for k, job in compiled_jobs.items()}
        return compiled_jobs

    def compile_config(self, compiled_jobs):
        yaml = dict(self.yaml_config)
        yaml["stages"].extend(self.pipeline.stage_names)
        yaml.update(self.pipeline.compile_aliases())
        yaml.update(compiled_jobs)
        return yaml

    @staticmethod
    def _format_python_version(yaml, key):
        version = float(yaml[key])
        del yaml[key]
        yaml["image"] = f"python:{version}"
        return yaml

    @staticmethod
    def _format_condition(yaml, key):
        del yaml[key]
        return yaml

    def format_job(self, job: dict):
        job = swap_dictionary_key(job, "install", "before_script")
        job = swap_dictionary_value(job, "python_version", self._format_python_version)
        job = swap_dictionary_value(job, "condition", self._format_condition)
        return sort_dict(job, default_key=self.default_phase_key)
