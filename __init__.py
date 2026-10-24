"""TSPI-15 programming language."""

__version__ = "0.1.0"

from .interpreter import TSPIError, run_source

__all__ = ["TSPIError", "run_source", "__version__"]
