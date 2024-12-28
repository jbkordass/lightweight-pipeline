"""Tests for the Pipeline_Data class."""

import os

import pytest

from lw_pipeline.config import Config
from lw_pipeline.pipeline_data import Pipeline_Data


class Some_Pipeline_Data(Pipeline_Data):
    """A concrete implementation of Pipeline_Data for testing purposes."""

    def __init__(self, config):
        super().__init__(config)

# get path of this script
script_path = os.path.realpath(__file__)
# get config path
config_path = os.path.join(os.path.dirname(script_path), "config.py")

def test_pipeline_data_initialization():
    """Test the initialization of the Pipeline_Data class."""
    config = Config(config_path)
    pipeline_data = Some_Pipeline_Data(config)
    assert pipeline_data.config == config
