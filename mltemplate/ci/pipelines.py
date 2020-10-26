from mltemplate.ci.core import Pipeline
from mltemplate.ci.yaml_order import TRAVIS_ORDER


class TravisPipeline(Pipeline):
    def sort_ci_config(self, config: dict):
        # Default items included between "before_install" and "matrix"
        sorted_keys = sorted(config.keys(), key=lambda k: TRAVIS_ORDER.get(k, 15))
        return {k: config[k] for k in sorted_keys}

    def compile(self):
        compiled_stages = []
        for s in self.stages:
            comp = s.compile()
            comp = comp if isinstance(comp, list) else [comp]
            compiled_stages.extend(comp)
        common_travis = {
            "language": "python",
            "sudo": True,
            "dist": "bionic",
            "services": ["docker"],
            "cache": "pip",
            "before_cache": ["chown -R travis:travis $HOME/.cache/pip"],
            "stages": self.stage_names,
            "before_install": ["env"],
            "matrix": dict(fast_finish=True, include=compiled_stages),
            "notifications": {"email": False},
        }
        common_travis.update(self.pipeline_params)
        common_travis.update(self.compile_aliases())
        common_travis = self.sort_ci_config(common_travis)
        return common_travis
