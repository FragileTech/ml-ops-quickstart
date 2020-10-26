import copy

STAGE_ORDER = {"style": 0, "style_check": 0, "build": 1, "test": 2, "deploy": 4}
PHASE_ORDER = {
    "stage": 0,
    "name": 1,
    "image": 1.5,
    "condition": 2,
    "if": 2,
    "python_version": 3,
    "python": 3,
    "install": 4,
    "before_script": 5,
    "after_script": 6,
}

TRAVIS_ORDER = {
    "language": 0,
    "sudo": 2,
    "dist": 4,
    "services": 6,
    "cache": 8,
    "before_cache": 10,
    "stages": 12,
    "before_install": 14,
    "matrix": 16,
    "notifications": 18,
}
ALL_ORDERS = dict(TRAVIS_ORDER)
ALL_ORDERS.update(STAGE_ORDER)
ALL_ORDERS.update(PHASE_ORDER)


def sort_dict(config, default_key: int = 99, order=ALL_ORDERS):
    sorted_keys = sorted(config.keys(), key=lambda x: order.get(x, default_key))
    return {k: config.get(k) for k in sorted_keys if config.get(k) is not None}


def sort_stages(stages, default_key: int = 3, order=STAGE_ORDER, as_jobs: bool = False):
    stages = list(sorted(stages, key=lambda k: order.get(k.name, default_key)))
    if as_jobs:
        return [job for stage in stages for job in stage]
    return stages


def sort_jobs(jobs, default_key, order=ALL_ORDERS):
    return [sort_dict(job, default_key=default_key, order=order) for job in jobs]
