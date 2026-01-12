"""Step discovery and dynamic loading utilities."""

# Authors: The Lightweight Pipeline developers
# SPDX-License-Identifier: BSD-3-Clause

import importlib.util
import os
import sys

from lw_pipeline.pipeline_step import Pipeline_Step


def find_all_step_files(steps_dir):
    """
    Find all .py files in the steps directory.

    Scans the specified directory for Python files that can contain
    pipeline step definitions. Excludes special files like __init__.py.

    Parameters
    ----------
    steps_dir : str
        Path to the directory containing step files.

    Returns
    -------
    list of str
        Sorted list of Python filenames (without path) found in the directory.
        Files starting with '__' are excluded.

    Examples
    --------
    >>> find_all_step_files("steps/")
    ['00_preprocessing.py', '01_analysis.py', '02_visualization.py']
    """
    step_files = []
    for file in os.listdir(steps_dir):
        if file.endswith(".py") and not file.startswith("__"):
            step_files.append(file)
    return sorted(step_files)


def find_all_step_classes(step_files, config):
    """
    Find and instantiate all Pipeline_Step classes from step files.

    Dynamically imports Python modules from the specified step files,
    searches for Pipeline_Step subclasses, and instantiates them with
    the provided configuration.

    Parameters
    ----------
    step_files : list of str
        List of Python filenames containing step definitions.
        Files should be in the directory specified by config.steps_dir.
    config : Config
        Configuration object to pass to step constructors.

    Returns
    -------
    list of Pipeline_Step
        List of instantiated Pipeline_Step objects ready for execution.

    Notes
    -----
    - The function automatically discovers all Pipeline_Step subclasses
      in each module (excluding the base Pipeline_Step class itself).
    - Each class is instantiated with the provided config object.
    - Module names are derived from the steps_dir basename.

    Examples
    --------
    >>> from lw_pipeline import Config
    >>> config = Config("config.py")
    >>> step_files = find_all_step_files(config.steps_dir)
    >>> steps = find_all_step_classes(step_files, config)
    >>> len(steps)
    3
    """
    steps_dir = config.steps_dir
    step_classes = []

    # Set module name to the name of the steps directory
    module_name = os.path.basename(steps_dir)

    # Import the steps package
    spec = importlib.util.spec_from_file_location(
        module_name,
        os.path.join(steps_dir, "__init__.py"),
        submodule_search_locations=[steps_dir],
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    # Loop through step files and import modules
    for step_file in step_files:
        # Skip special files
        if step_file.startswith("__"):
            continue

        # Remove file extension to get module name
        step_name = os.path.splitext(step_file)[0]

        # Import the submodule
        module = importlib.import_module(f"{module_name}.{step_name}")

        # Get Pipeline_Step subclasses defined in the module
        pipeline_step_classes = [
            cls
            for cls in module.__dict__.values()
            if isinstance(cls, type)
            and issubclass(cls, Pipeline_Step)
            and cls != Pipeline_Step
        ]

        # Instantiate each step class with the config
        for pipeline_step_class in pipeline_step_classes:
            step_classes.append(pipeline_step_class(config))

    return step_classes


def list_all_outputs(config):
    """
    List all registered outputs in pipeline steps.

    Discovers all pipeline steps and displays their registered outputs
    in a formatted table, showing which outputs are enabled by default.

    Parameters
    ----------
    config : Config
        Configuration object containing steps_dir.

    Notes
    -----
    Outputs are marked with:
    - ✓ : Enabled by default
    - ○ : Disabled by default

    Examples
    --------
    >>> from lw_pipeline import Config
    >>> config = Config("config.py")
    >>> list_all_outputs(config)

    00 - Preprocessing:
      Preprocess raw data
      Outputs:
        ✓ cleaned_data - Cleaned EEG data
        ○ debug_plot - Debug visualization (disabled by default)
    """
    step_files = find_all_step_files(config.steps_dir)
    steps = find_all_step_classes(step_files, config)

    for step in steps:
        print(f"\n{step.short_id} - {step.__class__.__name__}:")
        print(f"  {step.description}")

        outputs = step.output_registry.list_outputs(include_disabled=True)
        if outputs:
            print("  Outputs:")
            for name, description, enabled in outputs:
                marker = "✓" if enabled else "○"
                suffix = "" if enabled else " (disabled by default)"
                print(f"    {marker} {name} - {description}{suffix}")
        else:
            print("  No registered outputs")
