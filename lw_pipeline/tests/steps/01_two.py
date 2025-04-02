"""Tests for the Pipeline_Step class."""

import pytest

from lw_pipeline.pipeline_step import Pipeline_Exception, Pipeline_Step


class Step_Two(Pipeline_Step):
    """A concrete implementation of Pipeline_Step for testing purposes."""

    def __init__(self, config):
        super().__init__("Step Two", config)

    def step(self, data):
        return "Data from Step Two"
