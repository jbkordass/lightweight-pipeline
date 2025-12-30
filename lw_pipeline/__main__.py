"""Run the pipeline from the command line."""

# Authors: The Lightweight Pipeline developers
# SPDX-License-Identifier: BSD-3-Clause

import argparse
import importlib.util
import os
import sys

from lw_pipeline import Config, Pipeline_Exception, Pipeline_Step
from lw_pipeline.helper.report import generate_report


def _parse_outputs_argument(outputs_str):
    """
    Parse the --outputs command line argument.

    Parameters
    ----------
    outputs_str : str
        Comma-separated output specifications, optionally with step scoping.

    Returns
    -------
    dict or list
        If step-scoped (e.g., "01:plot,02:stats"), returns dict mapping
        step IDs to lists of patterns. Otherwise, returns list of patterns.

    Examples
    --------
    >>> _parse_outputs_argument("plot,stats")
    ['plot', 'stats']
    >>> _parse_outputs_argument("01:plot,01:stats,02:*")
    {'01': ['plot', 'stats'], '02': ['*']}
    >>> _parse_outputs_argument("*:plot")
    {'*': ['plot']}
    """
    outputs = [o.strip() for o in outputs_str.split(",")]

    # Check if any output uses step-scoped syntax
    has_step_scope = any(":" in o for o in outputs)

    if has_step_scope:
        # Parse into dict mapping step_id -> [patterns]
        result = {}
        for output in outputs:
            if ":" in output:
                step_id, pattern = output.split(":", 1)
                step_id = step_id.strip()
                pattern = pattern.strip()

                if step_id not in result:
                    result[step_id] = []
                result[step_id].append(pattern)
            else:
                # No step scope specified, treat as global wildcard
                if "*" not in result:
                    result["*"] = []
                result["*"].append(output)
        return result
    else:
        # Return simple list of patterns
        return outputs


def main():
    """Run pipeline from command line."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version", action="version", version="0.1")

    parser.add_argument("-r", "--run", action="store_true", help="Run the pipeline")

    parser.add_argument(
        "steps",
        metavar="TT",
        type=str,
        nargs="*",
        help="List of steps to run, separated by commas (only necessary to "
        "specify 00-99)",
    )

    parser.add_argument("-c", "--config", help="Path to the configuration file")

    parser.add_argument(
        "-l", "--list", action="store_true", help="List all steps in the step directory"
    )

    parser.add_argument(
        "--ignore-questions",
        action="store_true",
        help="Ignore questions, i.e. always respond with default answer to a question.",
    )

    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate a report of the pipeline's derivatives.",
    )

    parser.add_argument(
        "--store-report",
        action="store_true",
        help="Store the report tables in .tsv files in the derivatives dir "
        "(pipeline_report_bids_dir.tsv, pipeline_report_deriv_dir.tsv).",
    )

    parser.add_argument(
        "--full-report",
        action="store_true",
        help="Generate a full report (do not limit to subj, ses, task specification in"
        " the config) of the pipeline's derivatives.",
    )

    parser.add_argument(
        "--outputs",
        type=str,
        help="Comma-separated list of outputs to generate. "
        "Supports wildcards (e.g., 'plot*') and step-scoped syntax "
        "(e.g., '01:plot,02:*'). If not specified, all enabled outputs are generated.",
    )

    parser.add_argument(
        "--skip-outputs",
        type=str,
        help="Comma-separated list of outputs to skip. "
        "Supports wildcards (e.g., 'plot*') and step-scoped syntax "
        "(e.g., '01:plot,02:*'). Takes precedence over --outputs.",
    )

    parser.add_argument(
        "--list-outputs",
        action="store_true",
        help="List all registered outputs in the pipeline steps.",
    )

    options = parser.parse_args()

    config = Config(options.config, verbose=True)
    if options.ignore_questions:
        config.auto_response = "default"

    # Parse --outputs argument
    if options.outputs:
        config.outputs_to_generate = _parse_outputs_argument(options.outputs)

    # Parse --skip-outputs argument
    if options.skip_outputs:
        config.outputs_to_skip = _parse_outputs_argument(options.skip_outputs)

    if options.list_outputs:
        print("Registered Outputs:".center(80, "-"))
        list_all_outputs(config)
    elif options.run:
        # retrieve all steps script file names
        step_files = find_all_step_files(config.steps_dir)
        if not options.steps:
            print("Running entire pipeline")
        else:
            # filter step files based on steps specified in the command line argument
            step_files_specified = []
            for step_identifier in options.steps:
                step = [
                    step_file
                    for step_file in step_files
                    if step_file.startswith(step_identifier)
                ]
                if not step:
                    print(f"Error: Step file '{step_identifier}' not found.")
                    sys.exit(1)
                if len(step) > 1:
                    print(f"Error: Step file '{step_identifier}' is ambiguous.")
                    sys.exit(1)
                step_files_specified.append(step[0])
            step_files = step_files_specified
            print("Running the steps:", ", ".join(step_files))
        pipeline = Pipeline(step_files, config)
        # run the pipeline
        pipeline.run()
    elif options.list:
        print("Steps:".center(80, "-"))
        print("\n".join(find_all_step_files(config.steps_dir)))
    elif options.report or options.store_report or options.full_report:
        print(f"Generating {'limited ' if not options.full_report else 'full '}report")
        generate_report(config, options.store_report, options.full_report)
    else:
        # if no arguments implying actions are given, print help
        parser.print_help()


def find_all_step_files(steps_dir):
    """Find all the .py files in the steps directory."""
    # Get a list of all python files in the steps directory
    step_files = [
        f for f in os.listdir(steps_dir) if f.endswith(".py") and not f.startswith("__")
    ]

    # Sort the step files alphabetically
    step_files.sort()

    return step_files


def list_all_outputs(config):
    """List all registered outputs in pipeline steps."""
    step_files = find_all_step_files(config.steps_dir)
    step_classes = find_all_step_classes(step_files, config)
    
    if not step_classes:
        print("No steps found.")
        return
    
    for step in step_classes:
        # Get the step ID from the module name (e.g., "00" from "00_start")
        module_name = step.__class__.__module__.split(".")[-1]
        step_id = module_name.split("_")[0] if "_" in module_name else module_name
        
        # Get registered outputs
        outputs = step.output_registry.list_outputs(include_disabled=True)
        
        if outputs:
            print(f"\n{step_id} - {step.__class__.__name__}:")
            print(f"  {step.description}")
            print("  Outputs:")
            for name, description, enabled in outputs:
                status = "✓" if enabled else "○"
                desc_text = f" - {description}" if description else ""
                print(f"    {status} {name}{desc_text}")
        else:
            print(f"\n{step_id} - {step.__class__.__name__}: No registered outputs")


def find_all_step_classes(step_files, config):
    """Find all the Pipeline_Step classes in the given step files."""
    steps_dir = config.steps_dir

    step_classes = []

    # Set module name to the name of the steps directory
    module_name = os.path.basename(steps_dir)

    # Import the module
    spec = importlib.util.spec_from_file_location(
        module_name,
        os.path.join(config.steps_dir, "__init__.py"),
        submodule_search_locations=[config.steps_dir],
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    # Loop through the step files and import the modules
    for step_file in step_files:
        # Skip files like __init__.py, etc.
        if step_file.startswith("__"):
            continue

        # Remove the file extension to get the module name
        step_name = os.path.splitext(step_file)[0]

        # import the submodule
        module = importlib.import_module(f"{module_name}.{step_name}")

        # Get the subclasses of PipelineStep defined in the module
        pipeline_step_classes = [
            cls
            for cls in module.__dict__.values()
            if isinstance(cls, type)
            and issubclass(cls, Pipeline_Step)
            and cls != Pipeline_Step
        ]

        # Loop through the pipeline elements and invoke them
        for pipeline_step_class in pipeline_step_classes:
            step_classes.append(pipeline_step_class(config))

    return step_classes


class Pipeline:
    """Pipeline class to run the pipeline steps."""

    def __init__(self, steps, config=None):
        """
        Initialize the Pipeline.

        Parameters
        ----------
        steps : list
            A list of step file names or a list of Pipeline_Step instances.
        config : Config, optional
            An instance of Config class, required only if steps are file names
        """
        if all(isinstance(step, str) for step in steps):
            if config is None:
                raise ValueError("Config must be provided if steps are file names.")
            self.pipeline_steps = find_all_step_classes(steps, config)
        elif all(isinstance(step, Pipeline_Step) for step in steps):
            self.pipeline_steps = steps
        else:
            raise ValueError(
                "Steps must be either a list of file names or Pipeline_Step instances."
            )

    def run(self, data=None):
        """
        Run the pipeline.

        Include all Pipeline_Step classes contained in the step_files list.

        Parameters
        ----------
        data : object, optional
            Optional input data to be passed to the first step.

        Returns
        -------
        data : object
            The output data after processing through all pipeline steps.
        """
        # counter for executed steps/position in the pipeline
        pos = 1

        if data is not None:
            print("Pipeline starts with following input:".center(80, "-"))
            print(data)

        for step in self.pipeline_steps:
            # print the number/name of the step
            print(
                f"Step {pos}: {step.__class__.__module__} / "
                f"{step.__class__.__name__}".center(80, "-")
            )
            pos = pos + 1

            print("ℹ " + step.description)
            try:
                data = step.step(data)
            except Pipeline_Exception as e:
                print(f"Error in {step.description}: {e}")
                sys.exit(1)

        print("Pipeline finished with following output:".center(80, "-"))
        print(data)

        return data


if __name__ == "__main__":
    main()
