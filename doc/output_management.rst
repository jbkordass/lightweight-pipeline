.. _output_management:

==================
Output Management
==================

The output management system provides consistent saving of pipeline outputs with automatic path generation, metadata, and flexible control.

Quick Start
===========

Save outputs using the ``output_manager`` available in every ``Pipeline_Step``:

.. code-block:: python

    from lw_pipeline import Pipeline_Step

    class MyStep(Pipeline_Step):
        def step(self, data):
            # Create a plot
            fig, ax = plt.subplots()
            ax.plot(data)
            
            # Save it
            self.output_manager.save_figure(fig, "analysis_plot", format="pdf")
            
            return data

The output manager handles path generation, overwrite checking, and creates sidecar metadata automatically.


Core Components
===============

Output_Manager
--------------

The :class:`~lw_pipeline.Output_Manager` class handles saving various output types:

* **Figures**: ``save_figure(fig, name, format="pdf", ...)``
* **DataFrames**: ``save_dataframe(df, name, format="csv", ...)``
* **Arrays**: ``save_numpy(arr, name, format="npy", ...)``
* **JSON**: ``save_json(data, name, ...)``
* **Text**: ``save_text(text, name, ...)``
* **MNE objects**: ``save_mne_object(raw, name, ...)``

All methods automatically:

- Prefix filenames with the step ID
- Check overwrite settings
- Create sidecar JSON with provenance metadata
- Handle directory creation

Output Registration
-------------------

Use ``@register_output`` to mark methods as optional outputs:

.. code-block:: python

    from lw_pipeline import Pipeline_Step, register_output

    class Analysis(Pipeline_Step):
        
        @register_output("quick_plot", "Overview visualization")
        def create_plot(self):
            if not self.should_generate_output("quick_plot"):
                return
            
            fig = self._make_plot()
            self.output_manager.save_figure(fig, "overview")
        
        @register_output("detailed", "Expensive analysis", enabled_by_default=False)
        def detailed_analysis(self):
            if not self.should_generate_output("detailed"):
                return
            
            # Only runs when explicitly requested
            result = expensive_computation()
            self.output_manager.save_dataframe(result, "detailed_results")

Call these methods in your ``step()`` function. They'll only execute when their outputs are requested.


Configuration
=============

Add to your ``config.py``:

.. code-block:: python

    # Where to save outputs (defaults to deriv_root)
    output_root = "/path/to/outputs"
    
    # Overwrite behavior: "never", "always", "ask", or "ifnewer"
    overwrite_mode = "never"
    
    # Select which outputs to generate
    outputs_to_generate = ["plot", "stats"]  # or use wildcards: ["*plot*"]
    
    # Skip specific outputs
    outputs_to_skip = ["expensive_*"]  # Takes precedence over outputs_to_generate
    
    # Optional: enable performance tracking
    output_profiling = True
    
    # Optional: disable automatic sidecar JSON
    sidecar_auto_generate = False


Command Line Usage
==================

List available outputs::

    python -m lw_pipeline -c config.py --list-outputs

Generate specific outputs::

    # Specific outputs
    python -m lw_pipeline -c config.py --run --outputs "plot,stats"
    
    # Wildcards
    python -m lw_pipeline -c config.py --run --outputs "*plot*"
    
    # Step-scoped (only from step 01)
    python -m lw_pipeline -c config.py --run --outputs "01:*"

Skip outputs::

    python -m lw_pipeline -c config.py --run --skip-outputs "expensive_*"


BIDS Path Handling
===================

By default, outputs use simple paths. To use BIDS structure with MNE-BIDS:

.. code-block:: python

    from mne_bids import BIDSPath
    
    def step(self, data):
        # Assume data contains a BIDSPath
        bids_path = data.bids_path
        
        # Save with BIDS structure
        self.output_manager.save_figure(
            fig,
            name="channel_analysis",
            bids_path=bids_path,
            suffix="plot",
            extension=".pdf"
        )

The output will use MNE-BIDS to generate proper BIDS-compliant paths. The ``bids_path`` is updated with ``description``, ``suffix``, and ``extension`` parameters.


Examples
========

Saving Multiple Output Types
-----------------------------

.. code-block:: python

    def step(self, data):
        # Save figure
        self.output_manager.save_figure(fig, "analysis", format="pdf", dpi=300)
        
        # Save statistics table
        self.output_manager.save_dataframe(stats_df, "statistics", format="csv")
        
        # Save processed array
        self.output_manager.save_numpy(features, "features", format="npy")
        
        # Save metadata
        self.output_manager.save_json(params, "parameters")
        
        return data

Custom Metadata
---------------

.. code-block:: python

    metadata = {
        "FilterSettings": {"highpass": 1.0, "lowpass": 40.0},
        "Method": "Butterworth",
        "Order": 4
    }
    
    self.output_manager.save_figure(
        fig, "filtered_signal",
        metadata=metadata,
        format="pdf"
    )

Source File Tracking
--------------------

.. code-block:: python

    # Only regenerate if source is newer than output
    self.output_manager.save_figure(
        fig, "analysis",
        source_file="/path/to/source/data.fif",
        format="pdf"
    )

When ``overwrite_mode="ifnewer"``, output is only regenerated if the source file is newer.


See Also
========

* :ref:`api_documentation` - Full API reference
* :ref:`quickstart` - Getting started guide
* ``examples/output_management/`` - Complete working example
