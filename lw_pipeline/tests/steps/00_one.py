"""Tests for the Pipeline_Step class."""

from lw_pipeline.pipeline_step import Pipeline_Step


class Step_One(Pipeline_Step):
    """A concrete implementation of Pipeline_Step for testing purposes."""

    def __init__(self, config):
        super().__init__("Step One", config)

    def step(self, data):
        """Step method returning the input data."""
        return data
