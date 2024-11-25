from mne_bids import (
    BIDSPath,
    read_raw_bids, 
    write_raw_bids,
    find_matching_paths,
    update_sidecar_json,
)
from mne_bids.write import _sidecar_json
from mne_bids.utils import _write_json

from mne.io import BaseRaw
from mne.epochs import BaseEpochs
from mne.annotations import Annotations

import os
import time

import traceback

class PipelineData():
    """
    Data representation of EEG files for the pipeline.

    Contains Path or BidsPath objects of files the pipeline should be applied to.
    """

    config = None
    
    file_paths = None
    """
    Dictionary of file paths organized by subject, session, task, and run.
    """

    from_deriv = ""

    def __init__(self, config, from_bids=False, from_deriv=""):
        """
        Parameters
        ----------
        config : Config
            Configuration object.
        from_bids : bool
            If True, the data is initialized from BIDS files located in the bids_root directory.
        from_deriv : str
            Find bids styled files in the derivatives directory with the description from_deriv. 
        """
        self.config = config

        # use the eeg_path to create a stub of files organized by subject, session, task, and run
        self.file_paths = config.eeg_path

        if from_bids:
            self.apply(self.get_bids_path, subjects=config.subjects, sessions=config.sessions, tasks=config.tasks, save=False, print_duration = False)
        if from_deriv:
            self.from_deriv = from_deriv
            self.apply(self.get_raw_from_derivatives, subjects=config.subjects, sessions=config.sessions, tasks=config.tasks, save=False, print_duration = False)
    
    def __str__(self):
        if not self.file_paths:
            return "PipelineData object with no files."
        else:
            return f"PipelineData object handling the following files: {self.file_paths}"

    def get_bids_path(self, source_file, subject, session, task, run):
        """
        Create a BIDSPath without actually doing sth. with the source file.
        """
        return BIDSPath(
            subject=subject, 
            session=session.replace("-",""), 
            task=task, 
            run=run, 
            acquisition=self.config.eeg_acquisition, 
            root=self.config.bids_root,
            extension=os.path.splitext(source_file)[1]
        )
    
    def get_raw_from_derivatives(self, source_file, subject, session, task, run):
        match = find_matching_paths(self.config.deriv_root, 
            subjects=[subject],
            sessions=[session],
            tasks=[task],
            runs=[str(run)],
            descriptions=self.from_deriv,
            datatypes = [self.config.bids_datatype],
            suffixes=["eeg"], # not sure if this is optimal, "raw" not permitted though
            extensions=[".fif"])
        if len(match) != 1:
            raise ValueError(f"Found {len(match)} matching files for subject {subject} session {session} task {task} run {run} description {self.from_deriv}")
        return match[0]

    def apply(self, function, subjects = None, sessions = None, tasks = None, save=True, print_duration=True, suffix = "eeg", description = ""):
        """
        Apply a function to each data file individually. 
        Can also save the output to the derivatives directory.

        Parameters
        ----------
        function : function
            Function to apply to the data with the signature (source_file, subject, session, task, run).
        subjects : list
            List of subjects to apply the function to.
        sessions : list
            List of sessions to apply the function to.
        tasks : list
            List of tasks to apply the function to.
        save : bool
            Whether to save the output to the derivatives directory (in case function return a raw object, i.e. subclass of mne.io.BaseRaw or 
            an mne.Annotations instance).
        print_duration : bool
            Whether to print the duration of the function.
        suffix : str
            Suffix of the output Bidspath. Default is "eeg". For Anntations one could use "markers".
            Only certain values allowed, cf. MNE-BIDS documentation (https://mne.tools/mne-bids/stable/generated/mne_bids.BIDSPath.html#mne_bids.BIDSPath).
            If suffix is not in ["meg", "eeg", "ieeg"], the output file path will not be updated in the file_paths dictionary.
            Annotations are saved, but not directly passed on to the next step.
        description : str
            Description of the output Bidspath for the derivative, if none specified use the function name instead.
        """
        remove_from_file_paths = []

        step_description = function.__name__ if not description else description

        for subject, subject_info in self.file_paths.items():
            if subjects and subject not in subjects:
                continue
            for session, session_info in subject_info.items():
                if sessions and session not in sessions:
                    continue
                for task, task_info in session_info.items():
                    if tasks and task not in tasks:
                        continue
                    for run, source_file in task_info.items(): 

                        # check if the functions output should be saved
                        if save:
                            if not isinstance(source_file, BIDSPath):
                                # throw exception save requires a BIDSPath object as a sourcefile
                                raise ValueError("Saving requires a BIDSPath object as a source file.")
                            else:
                                output_bids_path = source_file.copy().update(
                                    root=self.config.deriv_root, 
                                    description=step_description,
                                    datatype = self.config.bids_datatype,
                                    suffix=suffix, # not sure if this is optimal, "raw/annot" not permitted though
                                    extension=".fif")
                            
                            # and if overwrite is False and the file already exists, skip
                            if not self.config.overwrite and output_bids_path.fpath.exists():
                                print(f"\u26A0 File {output_bids_path.fpath} already exists. Skipping. (To change this behaviour, set config variable 'overwrite = True'.)")
                                
                                if suffix in ["meg", "eeg", "ieeg"]:
                                    self.file_paths[subject][session][task][run] = output_bids_path
                                continue

                        # Start the timer for the step
                        start_time = time.time()

                        try:
                            answer = function(source_file, subject, session, task, run)
                        except Exception as e:
                            print(f"\u26A0 Something went wrong with {step_description} for {subject}, {session}, {task}, {run}. Removing from processed files list to continue.")
                            print(traceback.format_exc())
                            remove_from_file_paths.append((subject, session, task, run))
                            continue

                        # Print duration
                        duration = time.time() - start_time
                        if print_duration:
                            print(f"Step {step_description} took {duration:.2f} seconds.")

                        # check if answer has two varaiables
                        # the second one would be a dictionary with entries to update in the sidecar json
                        if isinstance(answer, tuple):
                            answer, sidecar_info_dict = answer
                            # print type of 
                            print(f"Type of answer: {type(sidecar_info_dict)}")
                        else:
                            sidecar_info_dict = None

                        # if the function returns a raw object, consider automatic saving
                        # otherwise assume the answer is a path to the processed file,
                        # i.e. the source file for the next pipeline step
                        if issubclass(type(answer), BaseRaw) or issubclass(type(answer), BaseEpochs) or isinstance(answer, Annotations):
                            if save:
                                # we already checked above that the source file is a BIDSPath object
                                
                                # unfortunately write_raw_bids does work to save preloaded (modified) raw objects
                                # to a .fif file → we have to do some bids stuff by hand/internal mne_bids functions

                                output_bids_path.mkdir()

                                answer.save(os.path.join(output_bids_path.directory, output_bids_path.basename), overwrite=self.config.overwrite)

                                # create a sidecar json file
                                sidecar_bids_path = output_bids_path.copy().update(extension=".json")
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
                                    _write_json(sidecar_bids_path.fpath, {}, overwrite=self.config.overwrite)
                                pipeline_step_info = {
                                    "Pipeline": {
                                        "Version": self.config.get_version(),
                                        "LastStep": step_description,
                                        "SourceFile": str(source_file.basename),
                                        "Duration": duration,
                                        "NJobs": self.config.n_jobs,
                                    },
                                }
                                if sidecar_info_dict:
                                    pipeline_step_info = pipeline_step_info | sidecar_info_dict
                                update_sidecar_json(sidecar_bids_path, pipeline_step_info)
                                    
                                # only update file path, if the step produced eeg, meg, or ieeg data (not markers, etc.)
                                if suffix in ["meg", "eeg", "ieeg"]:
                                    # pass on the output bids path to the next step
                                    self.file_paths[subject][session][task][run] = output_bids_path
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

                        