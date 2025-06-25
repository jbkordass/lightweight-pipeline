"""MNE helpers."""

# Authors: The Lightweight Pipeline developers
# SPDX-License-Identifier: BSD-3-Clause

import mne
from mne_bids import BIDSPath, read_raw_bids
import warnings


def raw_from_source(source, suppress_runtime_warning=True, **kwargs):
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
    suppress_runtime_warning : bool
        If True, suppresses RuntimeWarning when reading raw data.
        This is useful when reading raw data from BIDSPath, as it may raise a
        RuntimeWarning if coordsystem/electrode data, etc. is not found.
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
    # check if the source_file is an instance of BIDSPath
    if isinstance(source, BIDSPath):
        try:
            if suppress_runtime_warning:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", RuntimeWarning)
                    raw = read_raw_bids(source, **kwargs)
            else:
                raw = read_raw_bids(source, **kwargs)
        except Exception:
            raw = read_raw_bids(source, {"encoding": "latin1"})
    # check if it is a list of bids paths
    elif isinstance(source, list) and all(
        [isinstance(fpath, BIDSPath) for fpath in source]
    ):
        try:
            if suppress_runtime_warning:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", RuntimeWarning)
                    raws = [read_raw_bids(fpath, **kwargs) for fpath in source]
            else:
                raws = [read_raw_bids(fpath, **kwargs) for fpath in source]
        except Exception:
            raws = [read_raw_bids(fpath, {"encoding": "latin1"}) for fpath in source]
        # Check if all raws have the same sampling frequency
        sfreqs = [raw.info["sfreq"] for raw in raws]
        if len(set(sfreqs)) > 1:
            # If sampling frequencies differ, resample to the lowest frequency
            min_sfreq = min(sfreqs)
            raws = [
                raw.resample(min_sfreq) if raw.info["sfreq"] != min_sfreq else raw
                for raw in raws
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
