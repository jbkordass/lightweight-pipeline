"""Tests for the Pipeline_Step class."""

import pytest

from lw_pipeline.pipeline_step import Pipeline_Exception, Pipeline_Step


class Dummy_Pipeline_Step(Pipeline_Step):
    """A concrete implementation of Pipeline_Step for testing purposes."""

    def step(self, data):
        """Step method that simply returns the input data."""
        return data


def test_pipeline_step_initialization():
    """Test the initialization of the Pipeline_Step class."""
    description = "Test step"
    config = {"param": "value"}
    step = Dummy_Pipeline_Step(description, config)

    assert step.description == description
    assert step.config == config
    assert step.short_id is not None


def test_pipeline_step_short_id():
    """Test the short_id property of the Pipeline_Step class."""
    description = "Test step"
    config = {"param": "value"}
    short_id = "custom_id"
    step = Dummy_Pipeline_Step(description, config, short_id)

    assert step.short_id == short_id


def test_pipeline_step_method():
    """Test the step method of the Pipeline_Step class."""
    description = "Test step"
    config = {"param": "value"}
    step = Dummy_Pipeline_Step(description, config)
    data = {"key": "value"}

    result = step.step(data)
    assert result == data


def test_pipeline_exception():
    """Test the Pipeline_Exception class."""
    with pytest.raises(Pipeline_Exception):
        raise Pipeline_Exception("Test exception")
