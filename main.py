
import argparse
import sys
import model.pipeline_element as pe
import os
import importlib

from model.config import Config

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--version", action="version", version="0.1"
    )

    parser.add_argument(
        "--run", action="store_true", help="Run the entire pipeline"
    )

    parser.add_argument('tasks', metavar='TT', type=str, nargs='*',
                        help='List of tasks to run, separated by commas (only specify 00-99)')

    parser.add_argument(
        "-c", "--config", help="Path to the configuration file"
    )

    parser.add_argument(
        "--list", action="store_true", help="List all tasks in the task directory"
    )

    options = parser.parse_args()

    config = Config(options.config)

   
    print(config.data_dir)

    if options.run:
        # retrieve all tasks files
        task_files = get_all_tasks()
        if not options.tasks:
            print("Running entire pipeline")
        else:
            # filter tasks files based on the tasks specified in the command line argument
            task_files = [task_file for task_file in task_files if any(task_file.startswith(task) for task in options.tasks)]
            print("Running the tasks:", ", ".join(task_files))
        run_pipeline(config) 
    elif options.list:
        print("Tasks:".center(80, '-'))
        print("\n".join(get_all_tasks()))

def run_pipeline(tasks_files, config):

    pos = 1

    # Loop through the task files and import the modules
    for task_file in task_files:
        # Remove the file extension to get the module name
        module_name = os.path.splitext(task_file)[0]

        # print the number/name of task
        print(f"Task {pos}: {module_name}".center(80, '-'))
        pos = pos+1
        
        # Import the module
        module = importlib.import_module(f'tasks.{module_name}')
        
        # Get the subclasses of PipelineElement defined in the module
        pipeline_elements = [
            cls for cls in module.__dict__.values()
            if isinstance(cls, type) and issubclass(cls, pe.PipelineElement)
        ]

        data = None
        
        # Loop through the pipeline elements and invoke them
        for pipeline_element_cls in pipeline_elements:
            elt = pipeline_element_cls()
            print(elt.description)
            data = elt.process(data, config)

    print(f"Pipeline output {data}")

def get_all_tasks():
    # Get the path to the tasks directory
    tasks_dir = os.path.join(os.path.dirname(__file__), 'tasks')

    # Get a list of all Python files in the tasks directory
    task_files = [f for f in os.listdir(tasks_dir) if f.endswith('.py')]

    # Sort the task files alphabetically
    task_files.sort()

    return task_files

if __name__ == "__main__":
    main()