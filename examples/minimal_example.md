---
marp: true
class: invert
---

# Minimal MNE processing example using `lw_pipeline`

Folder content:

- `data/`
- `doc/`
- `steps/`
- `config.py` ← specify directories (data, steps) & variables
- `Makefile`
- `run.ipynb` ← run the pipeline interactively
---


# Classes

The package defines the following classes relevant here:

## `Pipeline_Step` 
Abstract class controlling a step.

## `Pipeline_Data` 
Abstract class for data.

- `Pipeline_MNE_BIDS_Data` subclass, handles data in bids format and takes care of saving/loading derivatives


---

# Step `Pipeline_Step`

Define subclasses (of the abstract class) `lw_pipeline.Pipeline_Step` in seperate files.
Use first digits to indicate order.

`steps/`
- `00_conversion.py` contains class `Conversion`
- `01_preprocessing.py`
- `02_continue.py`

---

## Conversion class

```python
class Conversion(Pipeline_Step):
    """
    Conversion Step to Bids format.
    
    Further explanations..
    """

    def __init__(self, config):
        """Initialize with a discription that is printed when run"""
        super().__init__("Convert to Bids format", config)

    def step(self, data):

        # ...

        return data
```

---

# BIDS (Brain Imaging Data Structure)

- for organizing, describing neuroimaging and electrophysiological data
- ensures consistent dataset structure for easier sharing, analysis, and reproducibility

### Key Features:
- **Consistent Directory Structure**: Predefined folder hierarchy
- **Standardized File Naming**: Specific naming conventions for clarity
- **Comprehensive Metadata**: Detailed metadata files for data and acquisition parameters

cf. [BIDS website](https://bids.neuroimaging.io/) and [Bids Documenation](https://bids-specification.readthedocs.io/en/stable/).

---

# MNE-BIDS

```python
from mne_bids import BIDSPath

bids_path = BIDSPath(
    subject='1001',                 run='01', 
    session='session1',             datatype='eeg',
    task='task1',                   root='path/to/bids/dataset'
    )
```

yields
- `bids_path.directory` → `path/to/bids/dataset/sub-1001/ses-session1/eeg`
- `bids_path.basename` → `sub-1001_ses-session1_task-task1_run-01`

cf. [MNE-BIDS Documentation](https://mne.tools/mne-bids) and [GitHub Repository](https://github.com/mne-tools/mne-bids)

---

# MNE-BIDS

Use `bids_path.match()` to find a fitting actually existing file, or alternatively:

```python
from mne_bids import find_matching_paths

bids_paths = find_matching_paths(
                        subjects="1001",
                        sessions="session1",
                        descriptions="01Preprocessing",
                        suffixes="eeg", 
                        extensions=".fif", 
                        root="path/to/bids/derivatives")
```

---

# MNE data: `Pipeline_MNE_BIDS_Data`

Book keeping device to manage a dictionary of the form

```python
{
    "1001": {
        "session1": {
            "task1": {
                "01": DATA_RUN_1,
                "02": DATA_RUN_2,
                # ...
            }
        }
    }
}
```

where `DATA_RUN_1`, `DATA_RUN_2`, etc. are paths to the files or data objects.

---

# Loading data

## From bids conform dataset
```python
data = Pipeline_MNE_BIDS_Data(config, from_bids=True)
```

## From derivatives
Derivatives file name containing `desc-01Preprocessing` (BIDS description)
```python
data = Pipeline_MNE_BIDS_Data(config, 
            from_deriv="01Preprocessing", 
            concatenate_runs=True)
```
(Concatenate runs replaces seperate runs by a run "99", containig the data of all runs as a list.)

---

# Config

`config.py` (some lines)
```python
data_dir = os.path.join(os.path.dirname(__file__), 'data')
"""Directory containing the data"""

bids_root = data_dir + "/bids"
"""Bids root directory"""
```

All variables set in the `config.py` file are translated into class attributes.
```python
from lw_pipeline.config import Config
config = Config("config.py")

config.bids_root
```

---

# Docs