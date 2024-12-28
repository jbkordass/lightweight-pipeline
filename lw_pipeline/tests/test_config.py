"""Tests for the Config class."""

import os

import pytest

from lw_pipeline.config import Config

# get path of this script
script_path = os.path.realpath(__file__)
# get config path
config_path = os.path.join(os.path.dirname(script_path), "config.py")

def test_config_initialization():
    """Test the initialization of the Config class."""
    config = Config(config_path)
    assert config._config_file_path == config_path

def test_config_data_dir():
    """Test the data_dir property of the Config class."""
    config = Config(config_path)
    assert config.data_dir == os.path.join(os.path.dirname(config_path), "data")