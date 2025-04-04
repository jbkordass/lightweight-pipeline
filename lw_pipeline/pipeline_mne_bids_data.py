"""Pipeline data representation for eeg/ieeg/meg data using MNE-BIDS."""

# Authors: The Lightweight Pipeline developers
# SPDX-License-Identifier: BSD-3-Clause

import os
import sys
import time
import traceback

from mne.annotations import Annotations
from mne.epochs import BaseEpochs
from mne.io import BaseRaw
from mne_bids import BIDSPath, find_matching_paths, get_entity_vals, update_sidecar_json
from mne_bids.utils import _write_json
from mne_bids.write import _sidecar_json

from lw_pipeline import Pipeline_Data, Pipeline_Step
from lw_pipeline.helper.naming import guess_short_id


class Pipeline_MNE_BIDS_Data(Pipeline_Data):
    """
    Data representation of eeg/ieeg/meg files for the pipeline.

    Contains Path or BidsPath objects of files the pipeline should be applied to.
    """

    file_paths = None
    """
    Dictionary of file paths organized by subject, session, task, and run.
    """

    from_deriv = ""

    def __init__(
        self,
        config,
        from_bids=False,
        from_deriv="",
        from_deriv_dir="",
        concatenate_runs=False,
    ):
        """
        Initialize the PipelineData object.

        Parameters
        ----------
        config : Config
            Configuration object.
        from_bids : bool
            If True, the data is initialized from BIDS files located in the bids_root
            directory.
        from_deriv : str
            Find bids styled files in the derivatives directory with the description
            from_deriv.
        from_deriv_dir : str
            Ignore the variable config.eeg_path and construct file_paths from the
            derivatives directory. Requires bids styled files in the derivatives
            directory.
        """
        super().__init__(config)

        # use the eeg_path to create a stub of files organized by subject, session,
        # task, and run
        self.file_paths = config.eeg_path

        # filter the file_paths dictionary by the subjects, sessions, and tasks
        # specified in the config
        if config.subjects:
            self.file_paths = {
                k: v for k, v in self.file_paths.items() if k in config.subjects
            }
        if config.sessions:
            for subject, sessions in self.file_paths.items():
                self.file_paths[subject] = {
                    k: v for k, v in sessions.items() if k in config.sessions
                }
        if config.tasks:
            for subject, sessions in self.file_paths.items():
                for session, tasks in sessions.items():
                    self.file_paths[subject][session] = {
                        k: v for k, v in tasks.items() if k in config.tasks
                    }

        if concatenate_runs:
            self.concatenate_runs()

        if from_bids:
            self.apply(
                self.get_bids_path_from_bids_root, save=False, print_duration=False
            )
        elif from_deriv:
            self.from_deriv = from_deriv
            self.apply(self.get_raw_from_derivatives, save=False, print_duration=False)
        elif from_deriv_dir:
            self.get_raw_from_derivatives_dir(from_deriv_dir)

    def __str__(self):
        """Return a string representation of the PipelineData object."""
        if not self.file_paths:
            return "PipelineData object with no files."
        else:
            # print the file_paths variable of the object in a tree format
            tree = ""
            for subject, subject_info in self.file_paths.items():
                tree += f"| Subject {subject}\n"
                for session, session_info in subject_info.items():
                    tree += f"|--- Session {session}\n"
                    for task, task_info in session_info.items():
                        tree += f"|----- Task {task}\n"
                        for run, source_file in task_info.items():
                            tree += f"|------- Run {run}: {str(source_file)}\n"
            return f"PipelineData object handling the following files:\n{tree}"

    def get_bids_path(self, source, subject, session, task, run):
        """Create a BIDSPath without actually doing sth. with the source file."""
        if isinstance(source, str):
            extension = os.path.splitext(source)[1]
        else:
            extension = ".fif"
        return BIDSPath(
            subject=subject,
            session=session.replace("-", ""),
            task=task,
            run=run,
            acquisition=self.config.bids_acquisition,
            root=self.config.bids_root,
            extension=extension,
        )

    def get_bids_path_from_bids_root(self, source, bids_path):
        """Get BidsPath for raw data from the bids_root directory."""
        bids_path.update(
            root=self.config.bids_root,
            description=None,
            extension=self.config.bids_extension,
            datatype=self.config.bids_datatype,
            suffix=self.config.bids_datatype,
        )
        if not bids_path.match():
            raise ValueError(f"File {bids_path.fpath} not found in BIDS directory.")
        return bids_path

    def get_raw_from_derivatives(self, source, bids_path):
        """Get BidsPath for raw data from the derivatives directory."""
        match = find_matching_paths(
            self.config.deriv_root,
            subjects=[bids_path.subject],
            sessions=[bids_path.session],
            tasks=[bids_path.task],
            runs=[str(bids_path.run)],
            descriptions=self.from_deriv,
            datatypes=[self.config.bids_datatype],
            suffixes=["eeg"],  # not sure if this is optimal, "raw" not permitted though
            extensions=[".fif"],
        )
        if len(match) != 1:
            raise ValueError(
                f"Found {len(match)} matching files for subject {bids_path.subject}, "
                f"session {bids_path.session}, "
                f"task {bids_path.task}, "
                f"run {bids_path.run}, "
                f"description {self.from_deriv}"
            )
        return match[0]

    def get_raw_from_derivatives_dir(self, derivative_description):
        """
        Ignore the variable config.eeg_path and construct file_paths from deriv. dir.

        Requires bids styled files in the derivatives directory.
        """
        config = self.config

        root_dir = config.deriv_root
        root_path = BIDSPath(root=root_dir)

        # find all subjects, sessions, tasks, runs in the derivatives directory
        subjects = get_entity_vals(root_dir, "subject")
        sessions = get_entity_vals(root_dir, "session")
        tasks = get_entity_vals(root_dir, "task")

        # intersect with subjects, sessions, tasks from config
        if config.subjects:
            subjects = list(set(subjects) & set(config.subjects))
        if config.sessions:
            sessions = list(set(sessions) & set(config.sessions))
        if config.tasks:
            tasks = list(set(tasks) & set(config.tasks))

        # create a dict with file paths organized by subject, session, task, and run
        constructed_file_paths = {}
        for subject in subjects:
            for session in sessions:
                for task in tasks:
                    files = (
                        root_path.copy()
                        .update(
                            subject=subject,
                            session=session,
                            task=task,
                            description=derivative_description,
                        )
                        .match()
                    )
                    for file in files:
                        if subject not in constructed_file_paths.keys():
                            constructed_file_paths[subject] = {}
                        if session not in constructed_file_paths[subject].keys():
                            constructed_file_paths[subject][session] = {}
                        if task not in constructed_file_paths[subject][session].keys():
                            constructed_file_paths[subject][session][task] = {}
                        constructed_file_paths[subject][session][task][file.run] = file

        self.file_paths = constructed_file_paths

    def apply(
        self,
        function,
        subjects=None,
        sessions=None,
        tasks=None,
        save=True,
        print_duration=True,
        suffix="eeg",
        description="",
        bids_root=None,
    ):
        """
        Apply a function to each data file individually.

        Can also save the output to the derivatives directory.

        Parameters
        ----------
        function : function
            Function to apply to the data with the signature (source, bids_path).
        subjects : list
            List of subjects to apply the function to.
        sessions : list
            List of sessions to apply the function to.
        tasks : list
            List of tasks to apply the function to.
        save : bool
            Whether to save the output to the derivatives directory (in case function
            return a raw object, i.e. subclass of mne.io.BaseRaw or an mne.Annotations
            instance).
        print_duration : bool
            Whether to print the duration of the function.
        suffix : str
            Suffix of the output Bidspath. Default is "eeg". For Anntations one could
            use "markers". Only certain values allowed, cf. MNE-BIDS documentation
            (https://mne.tools/mne-bids/stable/generated/mne_bids.BIDSPath.html#mne_bids.BIDSPath).
            If suffix is not in ["meg", "eeg", "ieeg"], the output file path will not
            be updated in the file_paths dictionary. Annotations are saved, but not
            directly passed on to the next step.
        description : str
            Description of the output Bidspath for the derivative, if none specified
            use PipelineStep.short_id + function name instead.
        bids_root : str
            Root directory for the destination. If None, the bids derivatives
            directory from the config is used.
        """
        remove_from_file_paths = []

        # possibly cook up a discription by default, but allow None as well
        if description == "":
            # bit of a hack, but somehow obtain the class the function is defined in
            step_class = vars(sys.modules[function.__module__])[
                function.__qualname__.split(".")[0]
            ]
            if issubclass(step_class, Pipeline_Step):
                description = (
                    guess_short_id(function.__module__) + function.__name__.capitalize()
                )
            else:
                description = function.__name__
            description = description.replace("_", "")

        # if no subjects, sessions, or tasks are specified, use the ones from the config
        if not subjects:
            subjects = self.config.subjects
        if not sessions:
            sessions = self.config.sessions
        if not tasks:
            tasks = self.config.tasks

        if not bids_root:
            bids_root = self.config.deriv_root

        for subject, subject_info in self.file_paths.items():
            if subjects and subject not in subjects:
                continue
            for session, session_info in subject_info.items():
                if sessions and session not in sessions:
                    continue
                for task, task_info in session_info.items():
                    if tasks and task not in tasks:
                        continue
                    for run, source_data in task_info.items():
                        if not isinstance(source_data, BIDSPath):
                            output_bids_path = self.get_bids_path(
                                source_data, subject, session, task, run
                            )
                        else:
                            output_bids_path = source_data.copy()

                        output_bids_path.update(
                            root=bids_root,
                            description=description,
                            datatype=self.config.bids_datatype,
                            suffix=suffix,
                            extension=".fif",
                        )

                        # check if the functions output should be saved
                        if save:
                            # and if overwrite is False & the file already exists, skip
                            if (
                                not self.config.overwrite
                                and output_bids_path.fpath.exists()
                            ):
                                print(
                                    f"\u23e9 File {output_bids_path.fpath} already "
                                    "exists. Skipping. (To change this behaviour, set"
                                    "config variable 'overwrite = True'.)"
                                )

                                if suffix in ["meg", "eeg", "ieeg"]:
                                    self.file_paths[subject][session][task][run] = (
                                        output_bids_path
                                    )
                                continue

                        # Start the timer for the step
                        start_time = time.time()

                        try:
                            answer = function(source_data, output_bids_path)
                        except Exception:
                            print(
                                f"\u26a0 Something went wrong with {description} for "
                                f"{subject}, {session}, {task}, {run}. Removing from "
                                "processed files list to continue."
                            )
                            print(traceback.format_exc())
                            remove_from_file_paths.append((subject, session, task, run))
                            continue

                        # Print duration
                        duration = time.time() - start_time
                        if print_duration:
                            print(f"Step {description} took {duration:.2f} seconds.")

                        # check if answer has two varaiables
                        # the second one would be a dictionary with entries to update
                        # in the sidecar json
                        if isinstance(answer, tuple):
                            answer, sidecar_info_dict = answer
                            # print type of
                            print(f"Type of answer: {type(sidecar_info_dict)}")
                        else:
                            sidecar_info_dict = None

                        # if the function returns a raw object, consider automatic
                        # saving otherwise assume the answer is a path to the processed
                        # file, i.e. the source file for the next pipeline step
                        if (
                            issubclass(type(answer), BaseRaw)
                            or issubclass(type(answer), BaseEpochs)
                            or isinstance(answer, Annotations)
                        ):
                            if save:
                                # we already checked above that the source file is
                                # a BIDSPath object

                                # unfortunately write_raw_bids does work to save
                                # preloaded (modified) raw objects to a .fif file → we
                                # have to do some bids stuff by hand/internal mne_bids
                                # functions

                                output_bids_path.mkdir()

                                if isinstance(answer, Annotations):
                                    answer.save(
                                        os.path.join(
                                            output_bids_path.directory,
                                            output_bids_path.basename,
                                        ),
                                        overwrite=self.config.overwrite,
                                    )
                                else:
                                    answer.save(
                                        os.path.join(
                                            output_bids_path.directory,
                                            output_bids_path.basename,
                                        ),
                                        # split_naming='bids',
                                        overwrite=self.config.overwrite,
                                    )

                                # create a sidecar json file
                                sidecar_bids_path = output_bids_path.copy().update(
                                    extension=".json"
                                )
                                if suffix in ["meg", "eeg", "ieeg"]:
                                    _sidecar_json(
                                        answer,
                                        task=output_bids_path.task,
                                        fname=sidecar_bids_path.fpath,
                                        manufacturer="n/a",
                                        datatype=output_bids_path.datatype,
                                        overwrite=self.config.overwrite,
                                    )
                                else:
                                    # write an empty json file
                                    _write_json(
                                        sidecar_bids_path.fpath,
                                        {},
                                        overwrite=self.config.overwrite,
                                    )
                                pipeline_step_info = {
                                    "Pipeline": {
                                        "Version": self.config.get_version(),
                                        "LastStep": description,
                                        # "SourceFile": str(source_data.basename),
                                        "Duration": duration,
                                        "NJobs": self.config.n_jobs,
                                    },
                                }
                                if sidecar_info_dict:
                                    pipeline_step_info = (
                                        pipeline_step_info | sidecar_info_dict
                                    )
                                update_sidecar_json(
                                    sidecar_bids_path, pipeline_step_info
                                )

                                # only update file path, if the step produced eeg, meg,
                                # or ieeg data (not markers, etc.)
                                if suffix in ["meg", "eeg", "ieeg"]:
                                    # pass on the output bids path to the next step
                                    self.file_paths[subject][session][task][run] = (
                                        output_bids_path
                                    )
                            else:
                                # simply pass on the raw object to the next step
                                self.file_paths[subject][session][task][run] = answer
                        else:
                            # pass on the path (or whatever it is) to the next step
                            self.file_paths[subject][session][task][run] = answer

        # remove files that could not be processed for the next step
        for subject, session, task, run in remove_from_file_paths:
            try:
                del self.file_paths[subject][session][task][run]
            except KeyError:
                pass

    def concatenate_runs(self):
        """
        Concatenate runs of the same task for each subject and session.

        Creates a new run "99".
        """
        config = self.config

        # start by building a new data object for run concatenated files
        # we call a concatenated run now "99"
        file_paths_runs_concatenated = {}

        for subject, sessions in self.file_paths.items():
            if config.subjects and subject not in config.subjects:
                continue
            file_paths_runs_concatenated[subject] = {}
            for session, tasks in sessions.items():
                if config.sessions and session not in config.sessions:
                    continue
                file_paths_runs_concatenated[subject][session] = {}
                for task, runs in tasks.items():
                    if config.tasks and task not in config.tasks:
                        continue
                    file_paths_runs_concatenated[subject][session][task] = {
                        "99": list(runs.values())
                    }

        self.file_paths = file_paths_runs_concatenated

    def as_df(self):
        """
        Return the file_paths dictionary as a pandas DataFrame.

        Returns
        -------
        df : pd.DataFrame
            DataFrame with columns "Subject", "Session", "Task", "Run", "Source".
        """
        import pandas as pd

        data = []
        for subject, sessions in self.file_paths.items():
            for session, tasks in sessions.items():
                for task, runs in tasks.items():
                    for run, source in runs.items():
                        data.append(
                            {
                                "Subject": subject,
                                "Session": session,
                                "Task": task,
                                "Run": run,
                                "Source": source,
                            }
                        )

        return pd.DataFrame(data)
