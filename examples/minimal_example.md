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

# Output Management

- **Output Registration**: Mark methods as optional outputs
- **Selective Generation**: Choose which outputs to generate via CLI or config
- **Automatic Metadata**: with sidecar JSON files
- **Overwrite Control**: Multiple modes (never, always, ask, ifnewer)

`Pipeline_Step` class now has a `output_manager` attribute used for saving.

---

# Registering Outputs

Use `@register_output` decorator to mark methods as optional outputs:

```python
from lw_pipeline import Pipeline_Step, register_output

class MyStep(Pipeline_Step):
    
    @register_output("summary_plot", "Summary visualization", 
                     enabled_by_default=True)
    def generate_summary(self):
        if not self.should_generate_output("summary_plot"):
            return
        
        fig, ax = plt.subplots()
        # ... create plot ...
        self.output_manager.save_figure(fig, "summary")
```

---

# Output Manager API

Common save methods:

```python
# Save figures
self.output_manager.save_figure(fig, "plot_name", formats=['png', 'pdf'])

# Save dataframes
self.output_manager.save_dataframe(df, "table_name", format='csv')

# Save JSON
self.output_manager.save_json(data_dict, "data_name")

# Save numpy arrays
self.output_manager.save_numpy(array, "array_name")
```

All methods automatically create sidecar JSON with metadata.

---

# CLI: List Outputs

```bash
python -m lw_pipeline -c config.py --list-outputs
```

Example output:
```
00 - Conversion:
  Convert to BIDS format
  Outputs:
    ✓ data_summary - Summary statistics
    ○ debug_info - Debugging information (disabled by default)

01 - Preprocessing:
  Preprocess data
  Outputs:
    ✓ quality_plot - Data quality visualization
```

✓ enabled by default, ○ disabled by default

---

# CLI: Selective Generation

### Generate specific outputs globally
```bash
# Generate only plots
python -m lw_pipeline -c config.py --run --outputs "*plot*"
```
- specific outputs ` --outputs "summary_plot,results_table"`
- all outputs (including disabled ones) ` --outputs "*"`
- outputs from specific step ` --outputs "01:*plot*"`
- etc.

---

# CLI: Skip Outputs

Skip expensive or debug outputs:

```bash
# Skip specific outputs
python -m lw_pipeline -c config.py --run --skip-outputs "detailed_analysis"

# Combine with --outputs
python -m lw_pipeline -c config.py --run --outputs "*plot*" --skip-outputs "expensive_*"
```

Note: `--skip-outputs` takes precedence over `--outputs`

---

# Config: Output Selection

Control outputs via configuration file: `config.py`

```python
# Generate specific outputs
outputs_to_generate = ["results_table", "*plot*"]

# Step-scoped configuration
outputs_to_generate = {
    "00": ["data_summary"],           # Specific outputs from step 00
    "01": ["*"],                      # All outputs from step 01
    "*": ["*plot*"]                   # All plots from other steps
}

# skip expensive outputs
outputs_to_skip = ["detailed_analysis", "expensive_*"]
```

---

# Overwrite Modes

Control file overwriting behavior:

```python
# config.py

overwrite_mode = "never"    # Skip existing files (default)
overwrite_mode = "always"   # Always overwrite
overwrite_mode = "ask"      # Prompt for each file
overwrite_mode = "ifnewer"  # Overwrite if source is newer
```

Example output when `overwrite_mode="never"`:
```
⏩ File output/desc-01_summary_plot.png already exists. 
   Skipping (overwrite_mode='never').
```

---

# Output Metadata

Each output file gets a sidecar JSON with provenance:

<small>

```json
{
    "Pipeline": {
        "Version": "git-abc123",
        "Step": "01",
        "StepDescription": "Preprocessing",
        "OutputFile": "desc-01_summary_plot.png",
        "GeneratedAt": "2025-12-12T10:30:45.123456"
    },
    "Performance": {
        "Duration": "0.234s",
        "FileSizeBytes": 12345
    },
    "PlotType": "Summary",
    "Description": "Data quality overview"
}
```
</small>

Add custom metadata via `metadata` parameter.

---

# Best Practices

### Mark expensive operations as disabled by default
```python
@register_output("expensive_plot", 
                 "Expensive plot doing some analysis",  
                 enabled_by_default=False)
def create_detailed_analysis(self):
    if not self.should_generate_output("detailed_analysis"):
        return
```

### Check before expensive operations
```python
if not self.should_generate_output("expensive_plot"):
    return  # Skip early, before loading data
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