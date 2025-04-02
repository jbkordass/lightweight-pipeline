"""Test configuration file."""

import os

# get config path
data_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")

# set data path to testdata
data_dir = str(data_path)

# set steps path
steps_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "steps")
