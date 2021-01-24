"""Package for initializing ML projects following ML Ops best practices."""
import logging

import flogging


flogging.setup()
_logger = logging.getLogger("mloq")
