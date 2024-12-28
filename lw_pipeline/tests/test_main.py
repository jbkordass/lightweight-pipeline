"""Tests for the __main__.py module."""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

from lw_pipeline.__main__ import find_all_steps, main, run_pipeline

# get path of this script
script_path = os.path.realpath(__file__)
# get config path
config_path = os.path.join(os.path.dirname(script_path), "config.py")

def test_run_pipeline_command(capfd):
    """Integration test running the pipeline with test config and with a steps dir."""
    # invoke main function with argv
    sys.argv = ["__main__.py", "--run", "--config", config_path]
    main()

    # assert printed output
    out, err = capfd.readouterr()

    # both descriptions
    assert "Step One" in out
    assert "Step Two" in out
    # and the output of step two should be printed
    assert "Data from Step Two" in out


@pytest.fixture
def mock_config():
    """Fixture to mock the Config class."""
    with patch('lw_pipeline.__main__.Config') as MockConfig:
        mock_config = MockConfig.return_value
        mock_config.steps_dir = "mock_steps_dir"
        mock_config.data_dir = "mock_data_dir"
        yield mock_config

@pytest.fixture
def mock_find_all_steps():
    """Fixture to mock the find_all_steps function."""
    with patch('lw_pipeline.__main__.find_all_steps') as mock_find:
        yield mock_find

@pytest.fixture
def mock_generate_report():
    """Fixture to mock the generate_report function."""
    with patch('lw_pipeline.__main__.generate_report') as mock_report:
        yield mock_report

def test_main_run(mock_config, mock_find_all_steps):
    """Test the main function with the --run option."""
    mock_find_all_steps.return_value = ["step1.py", "step2.py"]
    sys.argv = ["__main__.py", "--run", "--config", "mock_config_path"]

    with patch('lw_pipeline.__main__.run_pipeline') as mock_run_pipeline:
        main()
        mock_run_pipeline.assert_called_once_with(["step1.py", "step2.py"], mock_config)

def test_main_list(mock_config, mock_find_all_steps):
    """Test the main function with the --list option."""
    mock_find_all_steps.return_value = ["step1.py", "step2.py"]
    sys.argv = ["__main__.py", "--list", "--config", "mock_config_path"]

    with patch('builtins.print') as mock_print:
        main()
        mock_print.assert_any_call("Steps:".center(80, '-'))
        mock_print.assert_any_call("step1.py\nstep2.py")

def test_main_list_derivatives(mock_config, mock_find_all_steps):
    """Test the main function with the --list-derivatives option."""
    mock_find_all_steps.return_value = ["step1.py", "step2.py"]
    sys.argv = ["__main__.py", "--list-derivatives", "--config", "mock_config_path"]

    with patch('lw_pipeline.__main__.find_steps_derivatives') as mock_find_steps_derivatives:
        main()
        mock_find_steps_derivatives.assert_called_once_with(["step1.py", "step2.py"], mock_config)

def test_main_report(mock_config, mock_generate_report):
    """Test the main function with the --report option."""
    sys.argv = ["__main__.py", "--report", "--config", "mock_config_path"]

    with patch('builtins.print') as mock_print:
        main()
        mock_print.assert_any_call("Generating limited report")
        mock_generate_report.assert_called_once_with(mock_config, False, False)

def test_main_store_report(mock_config, mock_generate_report):
    """Test the main function with the --store-report option."""
    sys.argv = ["__main__.py", "--store-report", "--config", "mock_config_path"]

    with patch('builtins.print') as mock_print:
        main()
        mock_print.assert_any_call("Generating limited report")
        mock_generate_report.assert_called_once_with(mock_config, True, False)

def test_main_full_report(mock_config, mock_generate_report):
    """Test the main function with the --full-report option."""
    sys.argv = ["__main__.py", "--full-report", "--config", "mock_config_path"]

    with patch('builtins.print') as mock_print:
        main()
        mock_print.assert_any_call("Generating full report")
        mock_generate_report.assert_called_once_with(mock_config, False, True)

def test_find_all_steps():
    """Test the find_all_steps function."""
    with patch('os.listdir') as mock_listdir:
        mock_listdir.return_value = ["step1.py", "step2.py", "__init__.py"]
        result = find_all_steps("mock_steps_dir")
        assert result == ["step1.py", "step2.py"]

