# Output Management Example

This example demonstrates the output management system in `lw_pipeline`.

## Overview

The output management system provides:
- Automatic path generation and file naming
- Metadata tracking in sidecar JSON files
- Flexible overwrite control
- Selective output generation via CLI or config
- Support for multiple output types (figures, tables, arrays, etc.)

## Running the Example

### List Available Outputs

```bash
python -m lw_pipeline -c config.py --list-outputs
```

Shows all registered outputs with their descriptions and default status.

### Run with Default Outputs

```bash
python -m lw_pipeline -c config.py --run
```

Generates all outputs marked as enabled by default.

### Generate Specific Outputs

```bash
# Generate only summary and plot
python -m lw_pipeline -c config.py --run --outputs "summary,plot"

# Generate all outputs containing "plot"
python -m lw_pipeline -c config.py --run --outputs "*plot*"

# Generate all outputs from step 00
python -m lw_pipeline -c config.py --run --outputs "00:*"
```

### Skip Outputs

```bash
# Skip expensive outputs
python -m lw_pipeline -c config.py --run --skip-outputs "expensive_*"

# Skip specific output from specific step
python -m lw_pipeline -c config.py --run --skip-outputs "00:detailed_analysis"
```

## Configuration Options

In `config.py`, you can set:

```python
# Output directory (defaults to deriv_root)
output_root = "/path/to/outputs"

# Overwrite behavior: "never", "always", "ask", or "ifnewer"
overwrite_mode = "never"

# Select outputs to generate
outputs_to_generate = ["summary", "plot"]  # or ["*plot*"] for wildcards

# Skip specific outputs (takes precedence)
outputs_to_skip = ["expensive_*", "debug_*"]

# Enable performance profiling
output_profiling = True

# Disable automatic sidecar JSON
sidecar_auto_generate = False
```

### Step-Scoped Configuration

```python
# Generate different outputs per step
outputs_to_generate = {
    "00": ["summary", "plot"],  # Only these from step 00
    "01": ["*"],                # All outputs from step 01
    "*": ["*plot*"]             # Pattern for all other steps
}

# Skip outputs per step
outputs_to_skip = {
    "00": ["detailed"],         # Skip only in step 00
    "*": ["debug_*"]            # Skip in all steps
}
```

## Code Examples

### Basic Output Saving

```python
from lw_pipeline import Pipeline_Step

class MyStep(Pipeline_Step):
    def step(self, data):
        # Save a figure
        fig, ax = plt.subplots()
        ax.plot(data)
        self.output_manager.save_figure(fig, "my_plot", format="pdf")
        
        # Save a dataframe
        df = pd.DataFrame(data)
        self.output_manager.save_dataframe(df, "results", format="csv")
        
        return data
```

### Registered Outputs

```python
from lw_pipeline import Pipeline_Step, register_output

class MyStep(Pipeline_Step):
    
    @register_output("quick_plot", "Fast overview plot")
    def create_quick_plot(self):
        if not self.should_generate_output("quick_plot"):
            return
        
        fig = self._make_plot()
        self.output_manager.save_figure(fig, "quick")
    
    @register_output("detailed", "Expensive analysis", enabled_by_default=False)
    def detailed_analysis(self):
        if not self.should_generate_output("detailed"):
            return
        
        # Only runs when requested
        result = expensive_computation()
        self.output_manager.save_dataframe(result, "detailed")
    
    def step(self, data):
        # Call the registered output methods
        self.create_quick_plot()
        self.detailed_analysis()
        return data
```

### BIDS Paths

```python
from mne_bids import BIDSPath

def step(self, data):
    # For MNE-BIDS workflows
    bids_path = BIDSPath(
        subject="01",
        session="01",
        task="rest",
        run="01",
        root="/data/bids"
    )
    
    self.output_manager.save_figure(
        fig,
        name="channel_analysis",
        bids_path=bids_path,
        suffix="plot",
        extension=".pdf"
    )
```

### Custom Metadata

```python
def step(self, data):
    metadata = {
        "AnalysisParameters": {
            "threshold": 0.05,
            "method": "bootstrapping"
        },
        "Software": "custom_v1.0"
    }
    
    self.output_manager.save_figure(
        fig, "analysis",
        metadata=metadata,
        format="pdf"
    )
```

## Output Structure

Default (non-BIDS) outputs are saved as:
```
output_root/
├── 00_summary.csv
├── 00_summary.csv.json
├── 00_plot.pdf
├── 00_plot.pdf.json
└── ...
```

With BIDS structure:
```
output_root/
└── sub-01/
    └── ses-01/
        └── eeg/
            ├── sub-01_ses-01_task-rest_desc-00Analysis_plot.pdf
            ├── sub-01_ses-01_task-rest_desc-00Analysis_plot.pdf.json
            └── ...
```

## Files in This Example

- `config.py` - Configuration file
- `steps/00_analysis.py` - Example step with registered outputs
- `test_output_management.py` - Unit tests
- `README.md` - This file
- `USAGE_EXAMPLES.md` - Detailed usage examples (deprecated, see above)

## See Also

- Main documentation: `doc/output_management.rst`
- API reference: `doc/api.rst`
- Quickstart guide: `doc/quickstart.rst`
