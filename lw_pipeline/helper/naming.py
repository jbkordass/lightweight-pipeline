"""Naming helpers"""

# Authors: The Lightweight Pipeline developers
# SPDX-License-Identifier: BSD-3-Clause

def guess_short_id(module):
    """
    Obtain a short id (used for a PipelineStep) to obtain a short id from the module name.

    E.g. 00, 01, 02, etc. for files 00_start, 01_continue_1, 02_continue_2, etc. containing the PipelineStep classes.
    """
    module_name = module.split(".")[-1].split("_")
    short_id = ""
    for i, word in enumerate(module_name):
        # check if word is just numbers
        if word.isdigit():
            short_id += word
        else:
            # if we do not get enough numbers in the beginning, use first letters
            if len(short_id) < 2:
                short_id += word[0].lower()
    return short_id