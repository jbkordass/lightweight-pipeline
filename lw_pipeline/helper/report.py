"""Create a report of the pipeline's derivatives."""

# Authors: The Lightweight Pipeline developers
# SPDX-License-Identifier: BSD-3-Clause

import importlib
import inspect
import os
import sys

import pandas as pd
from mne_bids import BIDSPath, get_entity_vals, print_dir_tree, find_matching_paths

from lw_pipeline.pipeline_step import Pipeline_Step


def generate_report(config, store_report = False, full_report = False):
    """Create a report of the pipeline's derivatives."""
    # check if config.bids_root exists
    if not os.path.exists(config.bids_root):
        print(f"Error: BIDS root directory {config.bids_root} does not exist.")
    else:

        print("Bids".center(80, '-'))
        
        if full_report:
            print_dir_tree(config.bids_root, max_depth=4)
            print("".center(80, '-'))

        df_bids_report = _df_report_for_directory(config, config.bids_root, full_report)
        print(df_bids_report)

        if store_report:
            df_bids_report.to_csv(os.path.join(config.deriv_root, 'pipeline_report_deriv_dir.tsv'), sep='\t')
        
        # if ipython is available, use display to show the dataframes
        try:
            from IPython.display import display

            df_styler = df_bids_report.style.set_caption("Bids directory contents overview")
            display(df_styler)

        except ImportError:
            print("Error getting ipython")
            pass

    # check if config.deriv_root exists
    if not os.path.exists(config.deriv_root):
        print("Error: Derivatives root directory does not exist.")
    else:
        
        print("Derivatives".center(80, '-'))
        
        if full_report:
            print_dir_tree(config.deriv_root, max_depth=4)
            print("".center(80, '-'))

        df_deriv_report = _df_report_for_directory(config, config.deriv_root, full_report)
        print(df_deriv_report)
        
        if store_report:
            df_deriv_report.to_csv(os.path.join(config.deriv_root, 'pipeline_report_bids_dir.tsv'), sep='\t')

        # if ipython is available, use display to show the dataframes
        try:
            from IPython.display import display
            df_styler = df_deriv_report.style.set_caption("Derivatives directory contents overview")

            # find columns after the "runs" column, if there are any
            derivatives_columns = df_deriv_report.columns[df_deriv_report.columns.get_loc('runs')+1:]
            dc_subset = pd.IndexSlice[:, derivatives_columns]

            if len(derivatives_columns) > 0:
                df_styler = df_styler.map(_highlight_derivatives, subset=dc_subset)
            display(df_styler)

        except ImportError:
            print("Error getting ipython")
            pass

def _highlight_derivatives(val):
    color = {
        False: 'red', 
        True: 'yellowgreen', 
    }
    return f'background-color: {color[val]}; color: white'


def _df_report_for_directory(config, root_dir, full_report = False):

    root_path = BIDSPath(root=root_dir)

    # find all subjects, sessions, tasks, runs in the derivatives directory
    subjects = get_entity_vals(root_dir, 'subject')
    sessions = get_entity_vals(root_dir, 'session')
    tasks = get_entity_vals(root_dir, 'task')
    runs = get_entity_vals(root_dir, 'run')
    descriptions = get_entity_vals(root_dir, 'description')

    if not full_report:
        # intersect with subjects, sessions, tasks from config
        if config.subjects:
            subjects = list(set(subjects) & set(config.subjects))
        if config.sessions:
            sessions = list(set(sessions) & set(config.sessions))
        if config.tasks:
            tasks = list(set(tasks) & set(config.tasks))

    print("Subjects:", subjects)
    print("Sessions:", sessions)
    print("Tasks:", tasks)
    print("Runs:", runs)
    print("Descriptions:", descriptions)

    # print line
    print("-".center(80, '-'))
    
    # create a pandas dataframe with row for each subject, session, task and columns for each description
    # fill the dataframe with the file paths of the derivatives
    df = pd.DataFrame(index=pd.MultiIndex.from_product([subjects, sessions, tasks], names=['subject', 'session', 'task']), columns=['runs'] + descriptions)

    for subject in subjects:
        for session in sessions:
            for task in tasks:
                # find all files for the subject, session, task matching the description
                for description in descriptions:
                    # files = root_path.copy().update(subject=subject, session=session, task=task, description=description).match(check=True)
                    files = find_matching_paths(subjects=subject, sessions=session, tasks=task, descriptions=description, root=root_dir, check=True)
                    df.loc[(subject, session, task), description] = (not len(files) == 0)
                # find runs (removing duplicates)
                # run_files = root_path.copy().update(subject=subject, session=session, task=task).match(check=True)
                run_files = find_matching_paths(subjects=subject, sessions=session, tasks=task, root=root_dir, check=True)
                run_list = list(set([file.run for file in run_files]))
                run_list.sort()
                df.loc[(subject, session, task), 'runs'] = ', '.join(run_list)

    
    # sort the dataframe by subject, session, task
    df.sort_index(inplace=True)

    # remove rows where runs is empty and all descriptions are False
    if descriptions:
        df = df.dropna(subset=descriptions, how='all')
    df = df[df.runs != '']

    return df

def find_steps_derivatives(step_files, config):
    """
    Find possible derivatives from pipeline steps using inspect.

    Import the pipeline steps and find methods with signature "(source, bids_path)", this takes a while..
    """
    # Set module name to the name of the steps directory
    module_name = os.path.basename(config.steps_dir)

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

            print(f"{pipeline_step_class.__module__} {pipeline_step_class.__name__}: {step.description}")

            # use inspect to find methods in step of signature (self, source_file, subject, session, task, run)
            methods = inspect.getmembers(step, predicate=inspect.ismethod)
            for method in methods:
                # print signature of method
                if str(inspect.signature(method[1])) == "(source, bids_path)":
                    print(f"\t↳ {step.short_id}{method[0].capitalize()}")