"""MNE helpers."""

# Authors: The Lightweight Pipeline developers
# SPDX-License-Identifier: BSD-3-Clause

import warnings

import mne
from mne_bids import BIDSPath, find_matching_paths, read_raw_bids


def raw_from_source(source, n_jobs = 1, suppress_runtime_warning=True, **kwargs):
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
            print("Resampling to: ", min_sfreq)
            for raw in raws:
                if raw.info["sfreq"] != min_sfreq:
                    print("Resampling:", raw.info["file_id"])
                    raw.resample(min_sfreq, n_jobs=n_jobs) 
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


def find_ch(identifier, ch_names, return_identifiers=False, error_level="ignore"):
    """
    Find actual channel name by identifier (e.g. Fp1 for "EEG Fp1").

    Parameters
    ----------
    identifier : str | list of str
        The identifier to search for (e.g. "Fp1") or list of identifiers.
    ch_names : list of str
        The list of channel names to search in.
    return_identifiers : bool
        Whether to return the identifiers of found channels. Only used if identifier
        is a list.
    error_level : str
        The error level to use if the channel is not found. Can be "ignore", "warn",
        or "raise".

    Returns
    -------
    ch_name : str | None
        The actual channel name if found, else None.
    """
    if type(identifier) is list:
        return find_chs(identifier, ch_names, return_identifiers, error_level)
    elif not isinstance(identifier, str):
        raise ValueError("Identifier must be a string or list of strings.")

    for ch in ch_names:
        if identifier.lower() in ch.lower():
            return ch

    if error_level == "warn":
        warnings.warn(f"Channel {identifier} not found in {ch_names}.")
    elif error_level == "raise":
        raise ValueError(f"Channel {identifier} not found in {ch_names}.")

    return None

def find_chs(identifiers, ch_names, return_identifiers=False, error_level="ignore"):
    """
    Find actual channel names by identifiers (e.g. Fp1 for "EEG Fp1").

    Parameters
    ----------
    identifiers : list of str
        The identifiers to search for (e.g. ["Fp1", "Fp2"]).
    ch_names : list of str
        The list of channel names to search in.
    return_identifiers : bool
        Whether to return the identifiers of found channels.
    error_level : str
        The error level to use if a channel is not found. Can be "ignore", "warn",
        or "raise".

    Returns
    -------
    ch_names : list of str | None
        The actual channel names if found, else None.
    """
    found_identifiers = []
    found_ch_names = []
    for identifier in identifiers:
        ch_name = find_ch(identifier, ch_names, error_level=error_level)
        if ch_name is not None:
            found_ch_names.append(ch_name)
            found_identifiers.append(identifier)
        elif error_level == "raise":
            raise ValueError(f"Channel {identifier} not found in {ch_names}.")

    if return_identifiers:
        return found_ch_names, found_identifiers
    return found_ch_names


def find_assoc_deriv_bidspath(
    bids_path, description, suffix=None, extension=None, alt_description=None
):
    """
    Get bids path for derivative file based on an associated bids path and description.

    Use find_matching_paths based on subject, session, task, run and specify separately
    description, suffix and extension.

    Parameters
    ----------
    bids_path : mne_bids.BIDSPath
        BIDSPath object with the path to the raw data file.
    description : str
        Description of the derivative file.
    suffix : str
        Suffix of the derivative file.
    extension : str
        Extension of the derivative file.
    alt_description : str
        If the first one is not found, allow to specify an alternative.

    Returns
    -------
    bids_path : mne_bids.BIDSPath
        BIDSPath object with the path to the derivative file.
    """
    if suffix is None:
        suffix = bids_path.suffix
    if extension is None:
        extension = bids_path.extension

    derivative_bids_path = find_matching_paths(
        subjects=bids_path.subject,
        sessions=bids_path.session,
        tasks=bids_path.task,
        runs=bids_path.run,
        descriptions=description,
        suffixes=suffix,
        extensions=extension,
        root=bids_path.root,
    )

    if len(derivative_bids_path) == 1:
        return derivative_bids_path[0]
    else:
        if alt_description:
            return find_assoc_deriv_bidspath(bids_path, alt_description, suffix, extension)
        raise ValueError(
            f"No derivative file found for desc {description} and subject "
            f"{bids_path.subject} session {bids_path.session} task "
            f"{bids_path.task} run {bids_path.run}"
        )


# def save_assoc_deriv(
#     bids_path, description, suffix="eeg", extension=".fif", overwrite=False, **kwargs
# ):
#     """
#     Save a derivative file associated with a BIDSPath.

#     Parameters
#     ----------
#     bids_path : mne_bids.BIDSPath
#         BIDSPath object with the path to the raw data file.
#     description : str
#         Description of the derivative file.
#     suffix : str
#         Suffix of the derivative file.
#     extension : str
#         Extension of the derivative file.
#     overwrite : bool
#         Whether to overwrite existing files.
#     kwargs : dict
#         Additional keyword arguments to pass to bids_path.copy().

#     Returns
#     -------
#     deriv_bids_path : mne_bids.BIDSPath
#         BIDSPath object with the path to the saved derivative file.
#     """
#     deriv_bids_path = bids_path.copy(
#         suffix=suffix,
#         description=description,
#         extension=extension,
#         **kwargs,
#     )
#     if 
#     return deriv_bids_path


def add_annotation_prefix(
    annotations, prefix="BAD ", regex="(Active Stimulation)|(Buffer Stimulation)"
):
    """
    Add a prefix to annotation descriptions with descriptions matching a regex.

    Operates in-place.

    Parameters
    ----------
    annotations : mne.Annotations
        The annotations object containing the descriptions to modify.
    prefix : str
        The prefix to add to the annotation descriptions.
    regex : str
        The regex to match the annotation descriptions.

    Returns
    -------
    annotations : mne.Annotations
        The annotations object with updated descriptions.
    """
    from re import match

    for i, annot in enumerate(annotations):
        if match(regex, annot["description"]):
            annotations.description[i] = prefix + annotations.description[i]

    return annotations
