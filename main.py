
import argparse
import sys
from model.pipeline_step import PipelineStep
import os
import importlib

from model.config import Config

def main():

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

    options = parser.parse_args()

    config = Config(options.config)

   
    print(config.data_dir)

    if options.run:
        # retrieve all steps script file names
        step_files = find_all_steps()
        if not options.steps:
            print("Running entire pipeline")
        else:
            # filter step files based on the steps specified in the command line argument
            step_files = [step_file for step_file in step_files if any(step_file.startswith(step) for step in options.steps)]
            print("Running the steps:", ", ".join(step_files))
        run_pipeline(step_files, config) 
    elif options.list:
        print("Steps:".center(80, '-'))
        print("\n".join(find_all_steps()))
    else:
        print("No action specified. Add --run or --list (or check --help for more options)")

def run_pipeline(step_files, config):
    '''
    Run the pipeline through all steps given by PipelineStep classes contained in the 
    step_files list
    '''

    # counter for executed steps/position in the pipeline
    pos = 1

    # Loop through the step files and import the modules
    for step_file in step_files:
        # Remove the file extension to get the module name
        module_name = os.path.splitext(step_file)[0]

        # print the number/name of the step
        print(f"Step {pos}: {module_name}".center(80, '-'))
        pos = pos+1
        
        # Import the module
        module = importlib.import_module(f'steps.{module_name}')
        
        # Get the subclasses of PipelineStep defined in the module
        pipeline_step_classes = [
            cls for cls in module.__dict__.values()
            if isinstance(cls, type) and issubclass(cls, PipelineStep) and cls != PipelineStep
        ]

        data = None
        
        # Loop through the pipeline elements and invoke them
        for pipeline_step_class in pipeline_step_classes:
            step = pipeline_step_class()
            print(step.description)
            data = step.process(data, config)

    print(f"Pipeline output {data}")

def find_all_steps():
    '''
    Function to find all the .py files in the steps directory
    '''
    # Get the path to the steps directory
    steps_dir = os.path.join(os.path.dirname(__file__), 'steps')

    # Get a list of all python files in the steps directory
    step_files = [f for f in os.listdir(steps_dir) if f.endswith('.py')]

    # Sort the step files alphabetically
    step_files.sort()

    return step_files

if __name__ == "__main__":
    main()