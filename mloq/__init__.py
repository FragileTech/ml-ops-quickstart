"""Package for initializing ML projects following ML Ops best practices."""
import flogging


flogging.setup()
_logger = flogging.getLogger("mloq")
