"""Tests for the Pipeline_Step class."""

from lw_pipeline.pipeline_step import Pipeline_Step


class Step_Two(Pipeline_Step):
    """A concrete implementation of Pipeline_Step for testing purposes."""

    def __init__(self, config):
        super().__init__("Step Two", config)

    def step(self, data):
        """Step method returning a string."""
        return "Data from Step Two"
