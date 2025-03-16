---
marp: true
theme: default
class: invert
paginate: true
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

# Applying processing to data

Main function of `Pipeline_MNE_BIDS_Data`is `apply()`. Given

```python
class Some_Pipeline_Step(Pipeline_Step):

    def some_processing(self, source, bids_path):
        
        # apply processing to the source

        return source
```

this function can be applied to all 'sources' in `data` via

```python
data.apply(self.some_processing)
```


---

# Saving data

By default, `apply` tries to save what is returned from the passed function as a derivative at the location specified in `bids_path`.

- works for subclasses of MNE classes `BaseRaw`, `BaseRaw` or MNE `Annotations`

- BIDS description for derivative is constructed from module identifier and function name, e.g.
  - module `01_some_pipeline_step.py` → `01`
  - function `some_processing` → `SomeProcessing`
    (BIDS doesn't allow underscores...)

- can be disabled by passing `save=False`



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

# Docs (with sphinx)

Use docstrings: `"""..."""` for documentation within the code.

```python
class Some_Pipeline_Step(Pipeline_Step):
    """
    A short description of Some_Pipeline_Step.

    More detailed description of Some_Pipeline_Step.

    Attributes:
        attr1 (type): Description of `attr1`.

    Relevant config variables:
    - some_variable_1
    """
```

cf. [Sphinx documentation](https://www.sphinx-doc.org/en/master/).

---

# `run.ipynb`

<style scoped>
table {
    font-size: 0.9em;
    margin-top: 1.5em;
}
table th {
    display: none;
}
</style>

Run the pipeline interactively (ipython).

```python
%run $pipeline_path -c config.py -r 
```


|                    |                                                  |
|--------------------|--------------------------------------------------|
| `-c`               | Path to the configuration file                   |
| `-l`               | List pipeline steps (found in the config)        |
| `-r`               | Run the pipeline                                 |
| `-r 01 02`         | Run pipeline steps 01 and 02                     |
| `--report`         | Print a report of pipeline derivatives           | 
| `--help`           | Show help message (with further explanations)    |

---

# Demonstrating sth.

<style scoped>
div.columns { columns: 2; }
</style>

1. Create a jupyter notebook in the main folder
2. Load Config file (as above)

    ```python
    from lw_pipeline.config import Config
    config = Config("config.py")
    ```
3. Load raw file identified via BIDS
    
    ```python
    bids_path = find_matching_paths(
                        subjects="1001",
                        sessions="session1",
                        descriptions="01Preprocessing",
                        extensions=".fif", 
                        root=config.deriv_root)[0]
    ```

---

4. Load raw file
    
    ```python
    raw = mne.io.read_raw(bids_path.fpath, preload=True)
    ```

5. Load step usng importlib (necessary because of leading digits..)

    ```python
    import importlib
    step_c = importlib.import_module('steps.02_continue').Continue_With_More_Data_Analysis(config)

    annotations = step_c.annotate(raw, None)

    raw.set_annotations(annotations)
    ```

6. Continue demonstrating sth.