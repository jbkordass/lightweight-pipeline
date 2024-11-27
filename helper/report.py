
import os
import pandas as pd

from mne_bids import (
    BIDSPath,
    print_dir_tree,
    get_entity_vals
)

def generate_report(config, store_report = False, full_report = False):
    """
    Create a report of the pipeline's derivatives
    """

    # check if config.bids_root exists
    if not os.path.exists(config.bids_root):
        print(f"Error: BIDS root directory {config.bids_root} does not exist.")
        return
    
    print("Bids".center(80, '-'))
    
    print_dir_tree(config.bids_root, max_depth=4)

    df_bids_report = _df_report_for_directory(config, config.bids_root, full_report)
    print(df_bids_report)


    # check if config.deriv_root exists
    if not os.path.exists(config.deriv_root):
        print("Error: Derivatives root directory does not exist.")
        return
    
    print("Derivatives".center(80, '-'))

    print_dir_tree(config.deriv_root, max_depth=4)

    df_deriv_report = _df_report_for_directory(config, config.deriv_root, full_report)
    print(df_deriv_report)
    
    if store_report:
        df_deriv_report.to_csv(os.path.join(config.deriv_root, 'pipeline_report_bids_dir.csv'))
        df_bids_report.to_csv(os.path.join(config.deriv_root, 'pipeline_report_deriv_dir.csv'))

    # if ipython is available, use display to show the dataframes
    try:
        from IPython.display import display
        display(df_bids_report)
        display(df_deriv_report)
    except ImportError:
        print("Error getting ipython")
        pass


def _df_report_for_directory(config, root_dir, full_report = False):

    root_path = BIDSPath(root=root_dir)

    # print line
    print("-".center(80, '-'))

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
                    files = root_path.copy().update(subject=subject, session=session, task=task, description=description).match()
                    df.loc[(subject, session, task), description] = (not len(files) == 0)
                # find runs (removing duplicates)
                run_files = root_path.copy().update(subject=subject, session=session, task=task).match()
                df.loc[(subject, session, task), 'runs'] = ', '.join(list(set([file.run for file in run_files])))
    
    # sort the dataframe by subject, session, task
    df.sort_index(inplace=True)

    # remove rows where runs is empty and all descriptions are False
    df = df.dropna(subset=descriptions, how='all')
    df = df[df.runs != '']

    return df
