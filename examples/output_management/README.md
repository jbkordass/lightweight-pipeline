# Output Management Example

This example demonstrates the comprehensive output management system in `lw_pipeline`.

## Features Demonstrated

1. **Output Registration**: Using `@register_output` decorator to mark methods as optional outputs
2. **Conditional Generation**: Using `should_generate_output()` to skip expensive operations
3. **Multiple Output Types**: Saving figures, tables, JSON, and numpy arrays
4. **Custom Metadata**: Adding custom metadata to sidecar JSON files
5. **Overwrite Modes**: Respecting different overwrite behaviors
6. **Performance Profiling**: Tracking timing and file size in metadata
7. **CLI Control**: Selective output generation via command line

## Running the Example

### Generate All Enabled Outputs (Default)

```bash
cd examples/output_management
python -m lw_pipeline -c config.py --run
```

This generates:
- `data_table` ✓ (enabled by default)
- `summary_plot` ✓ (enabled by default)
- `detailed_plot` ✗ (disabled by default)
- `statistics` ✓ (enabled by default)
- `numpy_array` ✗ (disabled by default)

### Generate Specific Outputs

```bash
# Generate only plots
python -m lw_pipeline -c config.py --run --outputs summary_plot,detailed_plot

# Generate all outputs (including disabled ones)
python -m lw_pipeline -c config.py --run --outputs "*"

# Generate outputs matching a pattern
python -m lw_pipeline -c config.py --run --outputs "*plot*"

# Generate specific outputs for specific steps (step-scoped)
python -m lw_pipeline -c config.py --run --outputs "00:summary_plot,00:statistics"
```

### With Different Overwrite Modes

Edit `config.py` and change `overwrite_mode`:

```python
overwrite_mode = "always"   # Always overwrite
overwrite_mode = "never"    # Skip existing files (default)
overwrite_mode = "ask"      # Prompt for each file
overwrite_mode = "ifnewer"  # Overwrite if source is newer
```

## Output Structure

Outputs are saved to the `output_root` directory (defaults to `deriv_root`):

```
~/data/output_example/derivatives/
├── desc-00_raw_data_table.csv
├── desc-00_raw_data_table.csv.json         # Sidecar metadata
├── desc-00_raw_data_table.tsv
├── desc-00_raw_data_table.tsv.json
├── desc-00_summary_plot.pdf
├── desc-00_summary_plot.pdf.json
├── desc-00_summary_plot.png
├── desc-00_summary_plot.png.json
├── desc-00_summary_stats_stats.json
├── desc-00_summary_stats_stats.json.json
├── desc-00_detailed_analysis_plot.pdf      # Only if requested
├── desc-00_detailed_analysis_plot.pdf.json
├── desc-00_processed_data_array.npy        # Only if requested
└── desc-00_processed_data_array.npy.json
```

## Sidecar JSON Example

Each output file gets a sidecar JSON with provenance and profiling info:

```json
{
    "Pipeline": {
        "Version": "git-abc123",
        "Step": "00",
        "StepDescription": "Demonstrate output management...",
        "OutputFile": "desc-00_summary_plot.pdf",
        "GeneratedAt": "2025-12-11T10:30:45.123456"
    },
    "Performance": {
        "Duration": "0.234s",
        "Timestamp": "2025-12-11T10:30:45.123456",
        "FileSizeBytes": 12345
    },
    "PlotType": "Summary",
    "Description": "Overview of synthetic signal"
}
```

## Advanced Usage

### In Your Step Class

```python
from lw_pipeline import Pipeline_Step, register_output

class MyStep(Pipeline_Step):
    
    @register_output("expensive_plot", "Time-consuming plot", enabled_by_default=False)
    def create_plot(self):
        # Check if this output should be generated
        if not self.should_generate_output("expensive_plot"):
            return
        
        # ... expensive computation ...
        fig = create_expensive_plot()
        
        # Save with custom metadata
        self.output_manager.save_figure(
            fig, 
            name="analysis", 
            format="pdf",
            metadata={"AnalysisType": "Comprehensive"},
            subject="01",  # BIDS parameters
            session="01",
            dpi=300
        )
```

### Programmatic Configuration

```python
from lw_pipeline import Config

config = Config("config.py")

# Generate specific outputs
config.outputs_to_generate = ["summary_plot", "statistics"]

# Or use step-scoped patterns
config.outputs_to_generate = {
    "00": ["*plot*"],  # All plots from step 00
    "01": ["*"],       # All outputs from step 01
}

# Change overwrite mode
config.overwrite_mode = "ifnewer"

# Enable profiling
config.output_profiling = True
```

## Next Steps

- See `doc/output_management.rst` for complete API documentation
- Explore other examples in `examples/`
- Check the main `lw_pipeline` documentation for integration with MNE-BIDS data
