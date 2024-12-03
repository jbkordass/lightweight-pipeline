
import mne 

from mne_bids import BIDSPath

def raw_from_source(source, **kwargs):
    """
    Helper to produce an mne raw object from a number of different sources that could be passed through the pipeline.
    """

    # check if the source_file is an instance of BidsPath
    if isinstance(source, BIDSPath):
        try:
            raw = mne.io.read_raw(source, **kwargs)
        except Exception as e:
            raw = mne.io.read_raw(source, encoding="latin1", **kwargs)
    # check if it is a list of bids paths
    elif isinstance(source, list) and all([isinstance(fpath, BIDSPath) for fpath in source]):
        try:
            raws = [mne.io.read_raw(fpath, **kwargs)
                    for fpath in source]
        except Exception as e:
            raws = [mne.io.read_raw(fpath, encoding="latin1", **kwargs)
                    for fpath in source]
        raw = mne.io.concatenate_raws(raws)
    elif isinstance(source, mne.io.BaseRaw):
        raw = source
    elif isinstance(source, list) and all([isinstance(raw, mne.io.BaseRaw) for raw in source]):
        raw = mne.io.concatenate_raws(source)
    else:
        raise ValueError(f"Unknown source type {type(source)}.")
    
    return raw