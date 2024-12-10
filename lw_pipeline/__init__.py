"""Lightweight MNE Pipeline using MNE-Python and MNE-BIDS."""

__version__ = "0.1.0"

from lw_pipeline.pipeline_step import (
    PipelineStep,
    PipelineException
)
from lw_pipeline.pipeline_data import PipelineData

import lw_pipeline.main