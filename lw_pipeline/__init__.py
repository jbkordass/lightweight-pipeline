"""Lightweight MNE Pipeline using MNE-Python and MNE-BIDS."""

__version__ = "0.1.0"

from lw_pipeline.pipeline_step import Pipeline_Step, Pipeline_Exception

from lw_pipeline.config import Config

from lw_pipeline.pipeline_data import Pipeline_Data

# import mne bids data class, if MNE and MNE-BIDS are installed
try:
    from lw_pipeline.pipeline_mne_bids_data import Pipeline_MNE_BIDS_Data
except ImportError:
    pass

import lw_pipeline.__main__
