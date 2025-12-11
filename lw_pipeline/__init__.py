"""Lightweight MNE Pipeline using MNE-Python and MNE-BIDS."""

__version__ = "0.1.0"

from lw_pipeline.pipeline_step import Pipeline_Step, Pipeline_Exception

from lw_pipeline.config import Config

from lw_pipeline.pipeline_data import Pipeline_Data

from lw_pipeline.output_manager import OutputManager

from lw_pipeline.output_registration import register_output, OutputRegistry

# import mne bids data class, if MNE and MNE-BIDS are installed
try:
    from lw_pipeline.pipeline_mne_bids_data import Pipeline_MNE_BIDS_Data
except ImportError:
    pass

from lw_pipeline.__main__ import Pipeline

import lw_pipeline.__main__
