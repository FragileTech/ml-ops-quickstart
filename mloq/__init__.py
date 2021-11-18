"""Package for initializing ML projects following ML Ops best practices."""
from datetime import date
import logging

import flogging
from omegaconf import OmegaConf


flogging.setup()
_logger = logging.getLogger("mloq")
OmegaConf.register_new_resolver("current_year", lambda: date.today().year)
