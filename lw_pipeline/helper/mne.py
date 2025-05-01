"""MNE helpers."""

# Authors: The Lightweight Pipeline developers
# SPDX-License-Identifier: BSD-3-Clause

import mne
from mne_bids import BIDSPath, read_raw_bids


def raw_from_source(source, **kwargs):
    """
    Produce an mne raw object from different sources.

    Possible sources: (lists will be concatenated)

    - BIDSPath
    - list of BIDSPath
    - mne.io.BaseRaw
    - list of mne.io.BaseRaw

    Parameters
    ----------
    source : BIDSPath | list of BIDSPath | mne.io.BaseRaw | list of mne.io.BaseRaw
        The source to read the raw data from.
    kwargs : dict
        Additional keyword arguments to pass to mne.io.read_raw.

    Returns
    -------
    raw : mne.io.BaseRaw
        The raw data object.

    Raises
    ------
    ValueError
        If the source is not a BIDSPath, list of BIDSPath, mne.io.BaseRaw, or list of
        mne.io.BaseRaw.
    """
    # check if the source_file is an instance of BidsPath
    if isinstance(source, BIDSPath):
        try:
            raw = read_raw_bids(source, **kwargs)
        except Exception:
            raw = mne.io.read_raw(source, encoding="latin1", **kwargs)
    # check if it is a list of bids paths
    elif isinstance(source, list) and all(
        [isinstance(fpath, BIDSPath) for fpath in source]
    ):
        try:
            raws = [read_raw_bids(fpath, **kwargs) for fpath in source]
        except Exception:
            raws = [
                mne.io.read_raw(fpath, encoding="latin1", **kwargs) for fpath in source
            ]
        raw = mne.io.concatenate_raws(raws)
    elif isinstance(source, mne.io.BaseRaw):
        raw = source
    elif isinstance(source, list) and all(
        [isinstance(raw, mne.io.BaseRaw) for raw in source]
    ):
        raw = mne.io.concatenate_raws(source)
    else:
        raise ValueError(f"Unknown source type {type(source)}.")

    return raw
