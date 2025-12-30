"""Tests for the __main__.py module."""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

from lw_pipeline.__main__ import find_all_step_files, main

# get path of this script
script_path = os.path.realpath(__file__)
# get config path
config_path = os.path.join(os.path.dirname(script_path), "config.py")


@pytest.fixture
def mock_config():
    """Fixture to mock the Config class."""
    with patch("lw_pipeline.__main__.Config") as MockConfig:
        mock_config = MockConfig.return_value
        mock_config.steps_dir = "mock_steps_dir"
        mock_config.data_dir = "mock_data_dir"
        yield mock_config


@pytest.fixture
def mock_find_all_step_files():
    """Fixture to mock the find_all_step_files function."""
    with patch("lw_pipeline.__main__.find_all_step_files") as mock_find:
        yield mock_find


@pytest.fixture
def mock_pipeline():
    """Fixture to mock the Pipeline class."""
    with patch("lw_pipeline.__main__.Pipeline", autospec=True) as MockPipeline:
        mock_pipeline = MockPipeline
        mock_pipeline.return_value.run = MagicMock()
        yield mock_pipeline


def test_main_run(mock_config, mock_find_all_step_files, mock_pipeline):
    """Test the main function with the --run option."""
    mock_find_all_step_files.return_value = ["step1.py", "step2.py"]
    sys.argv = ["__main__.py", "--run", "--config", "mock_config_path"]

    main()

    mock_find_all_step_files.assert_called_once_with(mock_config.steps_dir)
    mock_pipeline.return_value.run.assert_called_once()


def test_main_run_with_steps(mock_config, mock_find_all_step_files, mock_pipeline):
    """Test the main function with the --run option and specific steps."""
    mock_find_all_step_files.return_value = ["step1.py", "step2.py", "step3.py"]
    sys.argv = [
        "__main__.py",
        "--run",
        "--config",
        "mock_config_path",
        "step1",
        "step3",
    ]

    main()

    mock_pipeline.return_value.run.assert_called_once()
    assert mock_pipeline.call_args_list[0][0] == (["step1.py", "step3.py"], mock_config)


def test_main_list(mock_config, mock_find_all_step_files):
    """Test the main function with the --list option."""
    mock_find_all_step_files.return_value = ["step1.py", "step2.py"]
    sys.argv = ["__main__.py", "--list", "--config", "mock_config_path"]

    with patch("builtins.print") as mock_print:
        main()
        mock_print.assert_any_call("Steps:".center(80, "-"))
        mock_print.assert_any_call("step1.py\nstep2.py")

def test_main_report(mock_config):
    """Test the main function with the --report option."""
    sys.argv = ["__main__.py", "--report", "--config", "mock_config_path"]

    with (
        patch("builtins.print") as mock_print,
        patch("lw_pipeline.__main__.generate_report") as mock_generate_report,
    ):
        main()
        mock_print.assert_any_call("Generating limited report")
        mock_generate_report.assert_called_once_with(mock_config, False, False)


def test_main_store_report(mock_config):
    """Test the main function with the --store-report option."""
    sys.argv = ["__main__.py", "--store-report", "--config", "mock_config_path"]

    with (
        patch("builtins.print") as mock_print,
        patch("lw_pipeline.__main__.generate_report") as mock_generate_report,
    ):
        main()
        mock_print.assert_any_call("Generating limited report")
        mock_generate_report.assert_called_once_with(mock_config, True, False)


def test_main_full_report(mock_config):
    """Test the main function with the --full-report option."""
    sys.argv = ["__main__.py", "--full-report", "--config", "mock_config_path"]

    with (
        patch("builtins.print") as mock_print,
        patch("lw_pipeline.__main__.generate_report") as mock_generate_report,
    ):
        main()
        mock_print.assert_any_call("Generating full report")
        mock_generate_report.assert_called_once_with(mock_config, False, True)


def test_find_all_step_files():
    """Test the find_all_step_files function."""
    with patch("os.listdir") as mock_listdir:
        mock_listdir.return_value = ["step1.py", "step2.py", "__init__.py"]
        result = find_all_step_files("mock_steps_dir")
        assert result == ["step1.py", "step2.py"]


def test_main_with_outputs_option(mock_config, mock_find_all_step_files, mock_pipeline):
    """Test the main function with the --outputs option."""
    mock_find_all_step_files.return_value = ["step1.py"]
    sys.argv = ["__main__.py", "--run", "--outputs", "plot,stats", "--config", "mock_config_path"]

    main()

    # Verify outputs_to_generate was set correctly
    assert hasattr(mock_config, 'outputs_to_generate')
    assert mock_config.outputs_to_generate == ['plot', 'stats']


def test_main_with_skip_outputs_option(mock_config, mock_find_all_step_files, mock_pipeline):
    """Test the main function with the --skip-outputs option."""
    mock_find_all_step_files.return_value = ["step1.py"]
    sys.argv = ["__main__.py", "--run", "--skip-outputs", "expensive_plot", "--config", "mock_config_path"]

    main()

    # Verify outputs_to_skip was set correctly
    assert hasattr(mock_config, 'outputs_to_skip')
    assert mock_config.outputs_to_skip == ['expensive_plot']


def test_main_with_list_outputs(mock_config):
    """Test the main function with the --list-outputs option."""
    sys.argv = ["__main__.py", "--list-outputs", "--config", "mock_config_path"]

    with (
        patch("builtins.print") as mock_print,
        patch("lw_pipeline.__main__.list_all_outputs") as mock_list_outputs,
    ):
        main()
        mock_print.assert_any_call("Registered Outputs:".center(80, "-"))
        mock_list_outputs.assert_called_once_with(mock_config)


def test_parse_outputs_argument():
    """Test the _parse_outputs_argument function."""
    from lw_pipeline.__main__ import _parse_outputs_argument
    
    # Test simple list
    result = _parse_outputs_argument("plot,stats")
    assert result == ['plot', 'stats']
    
    # Test step-scoped syntax
    result = _parse_outputs_argument("01:plot,01:stats,02:*")
    assert result == {'01': ['plot', 'stats'], '02': ['*']}
    
    # Test wildcard step
    result = _parse_outputs_argument("*:plot")
    assert result == {'*': ['plot']}
