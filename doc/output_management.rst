.. _output_management:

==================
Output Management
==================

The ``lw_pipeline`` package provides a comprehensive output management system that handles saving various output types (figures, tables, arrays, etc.) with consistent file paths, automatic sidecar metadata, and flexible overwrite control.

Overview
========

The output management system consists of three main components:

1. **OutputManager**: Central class for saving outputs with automatic path generation and metadata
2. **Output Registration**: Decorator-based system to mark methods as optional outputs
3. **CLI Integration**: Command-line support for selective output generation

Key Features
============

* **Consistent Output Paths**: Automatic BIDS-compliant or custom path generation
* **Automatic Sidecar JSON**: Provenance metadata with pipeline version, timestamps, and custom fields
* **Multiple Overwrite Modes**: ``always``, ``never``, ``ask``, or ``ifnewer`` (timestamp-based)
* **Performance Profiling**: Optional timing and file size tracking
* **Selective Generation**: Generate only requested outputs via CLI or config
* **Wildcard Support**: Pattern matching for batch output selection (``*``, ``plot*``, etc.)
* **Multi-modal Support**: Built-in handlers for figures, tables, MNE objects, arrays, JSON, and text

Basic Usage
===========

Accessing the Output Manager
-----------------------------

Every ``Pipeline_Step`` has an ``output_manager`` property:

.. code-block:: python

    from lw_pipeline import Pipeline_Step

    class MyStep(Pipeline_Step):
        def step(self, data):
            # Save a matplotlib figure
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3], [1, 4, 9])
            
            self.output_manager.save_figure(
                fig, 
                name="my_plot",
                format="pdf",
                suffix="plot"
            )
            
            return data

Saving Different Output Types
------------------------------

**Matplotlib Figures**

.. code-block:: python

    self.output_manager.save_figure(
        fig,
        name="channel_plot",
        format="pdf",  # or "png", "svg", etc.
        suffix="plot",
        metadata={"PlotType": "Timeseries"},
        dpi=300,
        bbox_inches="tight"
    )

**Pandas DataFrames**

.. code-block:: python

    self.output_manager.save_dataframe(
        df,
        name="results",
        format="csv",  # or "tsv", "xlsx"
        suffix="table",
        metadata={"Description": "Analysis results"}
    )

**MNE Objects**

.. code-block:: python

    self.output_manager.save_mne_object(
        raw,  # or epochs, evoked, etc.
        name="preprocessed",
        suffix="eeg",  # auto-detected if not specified
        subject="01",
        session="01"
    )

**Numpy Arrays**

.. code-block:: python

    self.output_manager.save_numpy(
        arr,
        name="features",
        format="npy",  # or "txt"
        suffix="array"
    )

**JSON Data**

.. code-block:: python

    self.output_manager.save_json(
        {"accuracy": 0.95, "n_samples": 100},
        name="metrics",
        suffix="stats"
    )

**Text Files**

.. code-block:: python

    self.output_manager.save_text(
        "Processing log:\n...",
        name="log",
        suffix="log",
        extension=".txt"
    )

Output Registration and Selective Generation
=============================================

Registering Outputs
-------------------

Use the ``@register_output`` decorator to mark methods as optional outputs:

.. code-block:: python

    from lw_pipeline import Pipeline_Step, register_output

    class Analysis(Pipeline_Step):
        
        @register_output("summary_plot", "Quick overview plot", enabled_by_default=True)
        def create_summary_plot(self):
            if not self.should_generate_output("summary_plot"):
                return
            
            # ... generate plot ...
            self.output_manager.save_figure(fig, "summary")
        
        @register_output("detailed_analysis", "Expensive analysis", enabled_by_default=False)
        def create_detailed_analysis(self):
            if not self.should_generate_output("detailed_analysis"):
                return
            
            # This expensive operation only runs when explicitly requested
            # ... complex computation ...

The ``@register_output`` decorator parameters:

* ``name`` (str): Output identifier for CLI selection
* ``description`` (str, optional): Human-readable description
* ``enabled_by_default`` (bool, optional): Whether to generate by default (default: True)
* ``group`` (str, optional): Optional grouping (reserved for future use)

Conditional Generation
----------------------

Use ``should_generate_output()`` to check if an output should be generated:

.. code-block:: python

    def step(self, data):
        # Always check before expensive operations
        if self.should_generate_output("expensive_plot"):
            # This code only runs when the output is requested
            result = expensive_computation()
            self.output_manager.save_figure(result, "expensive")
        
        return data

This allows skipping time-consuming analyses when their outputs aren't needed.

CLI Usage
=========

Selecting Outputs from Command Line
------------------------------------

**Generate all enabled outputs (default)**::

    python -m lw_pipeline -c config.py --run

**Generate specific outputs**::

    python -m lw_pipeline -c config.py --run --outputs summary_plot,statistics

**Generate all outputs (including disabled ones)**::

    python -m lw_pipeline -c config.py --run --outputs "*"

**Use wildcards**::

    python -m lw_pipeline -c config.py --run --outputs "*plot*"  # All outputs containing "plot"
    python -m lw_pipeline -c config.py --run --outputs "plot*"   # All outputs starting with "plot"

**Step-scoped selection**::

    # Generate only plots from step 00
    python -m lw_pipeline -c config.py --run --outputs "00:*plot*"
    
    # Generate specific outputs from multiple steps
    python -m lw_pipeline -c config.py --run --outputs "00:summary,01:statistics"
    
    # Generate all outputs from step 01
    python -m lw_pipeline -c config.py --run --outputs "01:*"
    
    # Apply pattern to all steps
    python -m lw_pipeline -c config.py --run --outputs "*:plot"

Configuration
=============

Add these variables to your ``config.py`` file:

Overwrite Mode
--------------

.. code-block:: python

    overwrite_mode = "never"  # Default

Options:

* ``"never"``: Skip existing files (default)
* ``"always"``: Always overwrite existing files
* ``"ask"``: Prompt user for each file
* ``"ifnewer"``: Overwrite only if source file is newer than output

Outputs to Generate
-------------------

.. code-block:: python

    # Generate all enabled outputs (default)
    outputs_to_generate = None
    
    # Generate specific outputs globally
    outputs_to_generate = ["plot", "stats"]
    
    # Use wildcards
    outputs_to_generate = ["*plot*", "summary*"]
    
    # Step-specific configuration
    outputs_to_generate = {
        "00": ["plot", "table"],  # Only these from step 00
        "01": ["*"],              # All outputs from step 01
        "*": ["summary*"]         # Pattern applying to all other steps
    }

Other Settings
--------------

.. code-block:: python

    # Directory for non-BIDS outputs (defaults to deriv_root)
    output_root = "/path/to/outputs"
    
    # Disable automatic sidecar JSON generation
    sidecar_auto_generate = False
    
    # Enable performance profiling (timing & file size in sidecar)
    output_profiling = True

Output Paths
============

BIDS Structure (Default)
-------------------------

By default, outputs use BIDS-compliant paths:

.. code-block:: python

    self.output_manager.save_figure(
        fig,
        name="analysis",
        suffix="plot",
        extension=".pdf",
        subject="01",
        session="01",
        task="rest",
        run="01"
    )

Generates::

    derivatives/sub-01/ses-01/eeg/
        sub-01_ses-01_task-rest_run-01_desc-00_analysis_plot.pdf

Custom Paths
------------

Use ``use_bids_structure=False`` for simpler paths:

.. code-block:: python

    self.output_manager.save_figure(
        fig,
        name="summary",
        suffix="plot",
        extension=".pdf",
        use_bids_structure=False
    )

Generates::

    derivatives/desc-00_summary_plot.pdf

Custom Directory
----------------

Override the output directory:

.. code-block:: python

    self.output_manager.save_figure(
        fig,
        name="report",
        custom_dir="/path/to/reports"
    )

Step ID Prefixing
-----------------

Output names are automatically prefixed with the step ID:

* Input: ``name="plot"`` in step ``00``
* Output filename includes: ``desc-00_plot``

This ensures unique output names across steps.

Sidecar Metadata
================

Automatic Metadata
------------------

Every output automatically gets a sidecar JSON with:

.. code-block:: json

    {
        "Pipeline": {
            "Version": "git-abc123",
            "Step": "00",
            "StepDescription": "Analysis step",
            "OutputFile": "desc-00_plot.pdf",
            "GeneratedAt": "2025-12-11T10:30:45.123456"
        }
    }

With Profiling Enabled
----------------------

When ``output_profiling = True``:

.. code-block:: json

    {
        "Pipeline": { ... },
        "Performance": {
            "Duration": "1.234s",
            "Timestamp": "2025-12-11T10:30:45.123456",
            "FileSizeBytes": 123456
        }
    }

Custom Metadata
---------------

Add custom fields via the ``metadata`` parameter:

.. code-block:: python

    self.output_manager.save_figure(
        fig,
        name="analysis",
        metadata={
            "PlotType": "Timeseries",
            "ChannelCount": 64,
            "FilterSettings": {
                "highpass": 0.1,
                "lowpass": 40
            }
        }
    )

Results in:

.. code-block:: json

    {
        "Pipeline": { ... },
        "Performance": { ... },
        "PlotType": "Timeseries",
        "ChannelCount": 64,
        "FilterSettings": {
            "highpass": 0.1,
            "lowpass": 40
        }
    }

Advanced Features
=================

Source File Comparison
----------------------

For ``ifnewer`` mode, specify a source file:

.. code-block:: python

    self.output_manager.save_figure(
        fig,
        name="derived_plot",
        source_file="/path/to/raw_data.fif"
    )

The output is only generated if the source file is newer than the existing output.

Getting Paths Without Saving
-----------------------------

Use ``get_output_path()`` to construct paths without saving:

.. code-block:: python

    # Get the path that would be used
    output_path = self.output_manager.get_output_path(
        name="analysis",
        suffix="plot",
        extension=".pdf"
    )
    
    # Check if it exists
    if output_path.exists():
        print(f"Output already exists: {output_path}")

Or use the convenience method on the step:

.. code-block:: python

    output_path = self.get_output_path(
        name="analysis",
        suffix="plot",
        extension=".pdf",
        subject="01"
    )

Generic Save Function
---------------------

For custom output types, use ``save_generic()``:

.. code-block:: python

    def save_my_format(obj, path, **kwargs):
        # Custom save logic
        with open(path, 'w') as f:
            f.write(str(obj))
    
    self.output_manager.save_generic(
        my_object,
        name="custom",
        save_func=save_my_format,
        suffix="data",
        extension=".custom",
        metadata={"Format": "Custom"}
    )

Migration from Manual Saves
============================

Before: Manual File Handling
-----------------------------

.. code-block:: python

    import os
    from pathlib import Path

    class OldStep(Pipeline_Step):
        def step(self, data):
            fig = create_plot()
            
            # Manual path construction
            output_dir = Path(self.config.deriv_root) / "plots"
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"step{self.short_id}_plot.pdf"
            
            # Manual overwrite check
            if not self.config.overwrite and output_path.exists():
                print(f"Skipping {output_path}")
                return data
            
            # Manual save
            fig.savefig(output_path, dpi=300)
            
            # Manual metadata
            import json
            sidecar = {
                "GeneratedAt": str(datetime.now()),
                "Step": self.short_id
            }
            with open(str(output_path) + ".json", 'w') as f:
                json.dump(sidecar, f)
            
            return data

After: Using Output Manager
----------------------------

.. code-block:: python

    class NewStep(Pipeline_Step):
        def step(self, data):
            fig = create_plot()
            
            # Everything handled automatically
            self.output_manager.save_figure(
                fig,
                name="plot",
                format="pdf",
                dpi=300
            )
            
            return data

Benefits:

* Automatic path generation
* Automatic overwrite checking
* Automatic sidecar metadata
* Consistent file naming
* Less boilerplate code

Best Practices
==============

1. **Use ``@register_output``** for any output that might be expensive or optional
2. **Always check ``should_generate_output()``** before expensive computations
3. **Provide meaningful output names** that describe the content (``channel_analysis`` not ``plot1``)
4. **Add custom metadata** to document analysis parameters and settings
5. **Use BIDS structure** for outputs that correspond to specific subjects/sessions
6. **Use custom paths** for summary outputs that aggregate across subjects
7. **Enable profiling during development** to identify slow outputs
8. **Document your outputs** with good descriptions in ``@register_output``

Examples
========

See the complete example in ``examples/output_management/`` which demonstrates:

* Multiple output types
* Conditional generation
* Custom metadata
* CLI usage
* Different overwrite modes
* Performance profiling

API Reference
=============

For detailed API documentation, see:

* :class:`lw_pipeline.OutputManager`
* :func:`lw_pipeline.register_output`
* :class:`lw_pipeline.OutputRegistry`
* :class:`lw_pipeline.Pipeline_Step` (output-related methods)

Common Issues
=============

Outputs Not Generated
----------------------

**Problem**: Outputs marked with ``@register_output`` aren't being created.

**Solution**: Check that:

1. The method is actually called in your ``step()`` method
2. ``should_generate_output()`` returns ``True``
3. The output is enabled by default or requested via CLI
4. No exceptions are raised in the output generation code

Overwrite Not Working
---------------------

**Problem**: Files aren't being overwritten even with ``overwrite_mode = "always"``.

**Solution**: 

* The ``overwrite_mode`` setting in the OutputManager is separate from the old ``config.overwrite`` setting
* Make sure you're using ``overwrite_mode``, not ``overwrite``
* For MNE objects, the ``overwrite`` parameter is passed internally

Path Issues
-----------

**Problem**: Outputs saved to unexpected locations.

**Solution**:

* Check ``output_root`` in config (defaults to ``deriv_root``)
* Use ``get_output_path()`` to preview paths before saving
* Set ``use_bids_structure=False`` if BIDS structure isn't needed
* Use ``custom_dir`` parameter to override the output directory

See Also
========

* :ref:`quickstart`
* :ref:`minimal_example`
* ``examples/output_management/`` for complete working example
