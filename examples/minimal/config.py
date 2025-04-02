"""
Local configuration file.

Variables override the default values specified in variables of the Config class.
"""

import os.path

import numpy as np

# Pipeline Settings
# -----------------

steps_dir = os.path.join(os.path.dirname(__file__), "steps")
"""Directory containing the pipeline steps"""

data_dir = os.path.join(os.path.dirname(__file__), "data")
"""Directory containing the data"""

bids_root = data_dir + "/bids"
"""Bids root directory"""

deriv_root = data_dir + "/derivatives"
"""Bids derivatives directory"""


# MNE_BIDS Data Settings
# ----------------------

bids_datatype = "eeg"
eeg_acquisition = "eeg"
bids_extension = ".edf"

overwrite = False
"""Overwrite existing files"""

n_jobs = 20
"""Number of parallel jobs"""

subjects = []
sessions = []
tasks = []

# 01 Preprocessing Settings
# -------------------------

resample_freq = 100
"""Frequency to resample the data to"""

notch_filter = np.arange(50, 150, 50)
"""Notch filter to remove power line artifact"""

# Further Settings
# ----------------

eeg_path = {
    "1001": {
        "session1": {"task1": {"1": "raw\\1001_session1_task1.edf"}},
        "session2": {"task1": {"1": "raw\\1001_session2_task1.edf"}},
    }
}
