"""Run the pipeline from the command line."""

# Authors: The Lightweight Pipeline developers
# SPDX-License-Identifier: BSD-3-Clause

import argparse
import importlib.util
import os
import sys

from lw_pipeline import Config, Pipeline_Exception, Pipeline_Step
from lw_pipeline.helper.report import find_steps_derivatives, generate_report


def main():
    """Run pipeline from command line."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v", "--version", action="version", version="0.1"
    )

    parser.add_argument(
        "-r", "--run", action="store_true", help="Run the pipeline"
    )

    parser.add_argument('steps', metavar='TT', type=str, nargs='*',
                        help='List of steps to run, separated by commas (only necessary to specify 00-99)')

    parser.add_argument(
        "-c", "--config", help="Path to the configuration file"
    )

    parser.add_argument(
        "-l", "--list", action="store_true", help="List all steps in the step directory"
    )

    parser.add_argument(
        "--list-derivatives", action="store_true", help="List methods in steps that could be used to produce derivatives."
    )

    parser.add_argument(
        "--ignore-questions", action="store_true", help="Ignore questions, i.e. always respond with default answer to a question."
    )

    parser.add_argument(
        "--report", action="store_true", help="Generate a report of the pipeline's derivatives."
    )

    parser.add_argument(
        "--store-report", action="store_true", help="Store the report tables in .tsv files in the derivatives dir (pipeline_report_bids_dir.tsv, pipeline_report_deriv_dir.tsv)."
    )

    parser.add_argument(
        "--full-report", action="store_true", help="Generate a full report (do not limit to subj, ses, task specification in the config) of the pipeline's derivatives."
    )

    options = parser.parse_args()

    config = Config(options.config)
    if options.ignore_questions:
        config.auto_response = "default"

    if options.run:
        # retrieve all steps script file names
        step_files = find_all_steps(config.steps_dir)
        if not options.steps:
            print("Running entire pipeline")
        else:
            # filter step files based on the steps specified in the command line argument
            step_files = [step_file for step_file in step_files if any(step_file.startswith(step) for step in options.steps)]
            print("Running the steps:", ", ".join(step_files))
        run_pipeline(step_files, config) 
    elif options.list:
        print("Steps:".center(80, '-'))
        print("\n".join(find_all_steps(config.steps_dir)))
    elif options.list_derivatives:
        print("Derivatives:".center(80, '-'))
        find_steps_derivatives(find_all_steps(config.steps_dir), config)
    elif options.report or options.store_report or options.full_report:
        print(f"Generating {'limited ' if not options.full_report else 'full '}report")
        generate_report(config, options.store_report, options.full_report)
    else:
        print("No action specified. Add --run or --list (or check --help for more options)")


def run_pipeline(step_files, config):
    """Run the pipeline through all steps given by PipelineStep classes contained in the step_files list."""
    # counter for executed steps/position in the pipeline
    pos = 1

    data = None

    steps_dir = config.steps_dir

    # check if steps dir is relative in that case make it relative to the config file or the current working directory
    if not os.path.isabs(steps_dir):
        # check if there is an externatl config file or if default config is used
        if config.config_file_path is not None:
            steps_dir = os.path.join(os.path.dirname(config.config_file_path), steps_dir)
        else:
            steps_dir = os.path.join(os.getcwd(), steps_dir)
    
    # make steps dir absolute
    steps_dir = os.path.abspath(steps_dir)

    # Set module name to the name of the steps directory
    module_name = os.path.basename(steps_dir)

    # Import the module
    spec = importlib.util.spec_from_file_location(module_name, 
                                                    os.path.join(config.steps_dir, "__init__.py"), 
                                                    submodule_search_locations=[config.steps_dir])
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

        # print the number/name of the step
        print(f"Step {pos}: {step_name}".center(80, '-'))
        pos = pos+1

        # import the submodule
        module = importlib.import_module(f'{module_name}.{step_name}')
        
        # Get the subclasses of PipelineStep defined in the module
        pipeline_step_classes = [
            cls for cls in module.__dict__.values()
            if isinstance(cls, type) and issubclass(cls, Pipeline_Step) and cls != Pipeline_Step
        ]
        
        # Loop through the pipeline elements and invoke them
        for pipeline_step_class in pipeline_step_classes:
            step = pipeline_step_class(config)
            print(step.description)
            try:
                data = step.step(data)
            except Pipeline_Exception as e:
                print(f"Error in {step.description}: {e}")
                sys.exit(1)

    print(f"Pipeline finished with following output:".center(80, '-'))
    print(data)

def find_all_steps(steps_dir):
    """Find all the .py files in the steps directory."""
    # Get a list of all python files in the steps directory
    step_files = [f for f in os.listdir(steps_dir) if f.endswith('.py') and not f.startswith("__")]

    # Sort the step files alphabetically
    step_files.sort()

    return step_files

if __name__ == "__main__":
    main()