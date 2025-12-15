"""Configuration for output management example."""

# Authors: The Lightweight Pipeline developers
# SPDX-License-Identifier: BSD-3-Clause

import os

# Directory configuration
data_dir = os.path.join(os.path.expanduser("~"), "data", "output_example")
bids_root = os.path.join(data_dir, "bids")
deriv_root = os.path.join(data_dir, "derivatives")
output_root = deriv_root  # Can be different from deriv_root if desired

# Steps directory
steps_dir = "steps/"

# Output management configuration
overwrite_mode = "never"  # Options: "always", "never", "ask", "ifnewer"
sidecar_auto_generate = True
output_profiling = True  # Include timing and file size in sidecar

# Specify which outputs to generate
# None = all enabled outputs (default)
# List = patterns for all steps, e.g., ["plot", "stats*"]
# Dict = step-specific, e.g., {"00": ["plot"], "01": ["*"]}
outputs_to_generate = None  # Can be overridden by --outputs CLI argument

# BIDS configuration
bids_datatype = "eeg"
subjects = ["01", "02"]
sessions = ["01"]
tasks = ["rest"]

# Processing configuration
n_jobs = 1
