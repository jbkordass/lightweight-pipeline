"""Steps and configuration for the minimal example pipeline."""

# make sure lw_pipeline is in the path
from os.path import dirname, abspath, join
import sys

sys.path.insert(
    0, abspath(join(dirname(__file__), "..", "..", "pipeline"))
)  # Source code dir relative to this file

# import steps to make them visible in the sphinx documentation
from importlib import import_module
from os import listdir

for path in listdir(dirname(__file__)):
    if path.endswith(".py") and not path.startswith("__"):
        m = import_module(f"steps.{path[:-3]}")
        # get all attributes from the module
        try:
            attrlist = m.__all__
        except AttributeError:
            attrlist = dir(m)
        for attr in attrlist:
            globals()[attr] = getattr(m, attr)
