from mne_bids import (
    BIDSPath,
    read_raw_bids, 
    write_raw_bids,
    find_matching_paths
)

from mne.io import BaseRaw

import os

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
            self.apply(self.get_bids_path, subjects=config.subjects, save=False)
        if from_deriv:
            self.from_deriv = from_deriv
            self.apply(self.get_raw_from_derivatives, subjects=config.subjects, save=False)
    
    def __str__(self):
        if not self.file_paths:
            return "PipelineData object with no files."
        else:
            return f"PipelineData object handling the following files: {self.file_paths}"

    def get_bids_path(self, source_file, subject, session, task, run):
        """
        Create a BIDSPath without actually doing sth. with the source file.
        """
        bids_path = BIDSPath(
            subject=subject, 
            session=session.replace("-",""), 
            task=task, 
            run=run, 
            acquisition=self.config.eeg_acquisition, 
            root=self.config.bids_root,
            extension=os.path.splitext(source_file)[1]
        )
        return bids_path
    
    def get_raw_from_derivatives(self, source_file, subject, session, task, run):
        match = find_matching_paths(self.config.deriv_root, 
            subjects=[subject],
            sessions=[session],
            tasks=[task],
            runs=["0" + str(run)],
            descriptions=self.from_deriv)
        if len(match) != 1:
            raise ValueError("Found {} matching files for subject {} session {} task {} run {} description {}".format(len(match), subject, session, task, run, self.from_deriv))
        return match[0]

    def apply(self, function, subjects = None, sessions = None, tasks = None, save=True):
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
            Whether to save the output to the derivatives directory (in case function return a raw object).
        """
        for subject, subject_info in self.config.eeg_path.items():
            if subjects and subject not in subjects:
                continue
            for session, session_info in subject_info.items():
                if sessions and session not in sessions:
                    continue
                for task, task_info in session_info.items():
                    if tasks and task not in tasks:
                        continue
                    run = 0
                    for source_file in self.file_paths[subject][session][task]: 
                        run += 1

                        # check if the functions output should be saved
                        if save:
                            output_bids_path = source_file.copy().update(
                                    root=self.config.deriv_root, 
                                    description=function.__name__,
                                    suffix="eeg", # not sure if this is optimal, "raw" not permitted though
                                    extension=".fif")

                            # and if the file already exists, skip
                            if not self.config.overwrite and output_bids_path.fpath.exists():
                                print(f"\u26A0 File {output_bids_path.fpath} already exists. Skipping. (To change this behaviour, set config variable 'overwrite = True'.)")
                                self.file_paths[subject][session][task][run-1] = output_bids_path
                                continue

                        answer = function(source_file, subject, session, task, run)

                        # if the function returns a raw object, consider automatic saving
                        # otherwise assume the answer is a path to the processed file,
                        # i.e. the source file for the next pipeline step
                        if issubclass(type(answer), BaseRaw):
                            if save:
                                if not isinstance(source_file, BIDSPath):
                                    # throw exception save requires a BIDSPath object as a sourcefile
                                    raise ValueError("Saving requires a BIDSPath object as a source file.")
                                
                                output_bids_path.mkdir()
                                answer.save(os.path.join(output_bids_path.directory, output_bids_path.basename), overwrite=True)

                                # pass on the output bids path to the next step
                                self.file_paths[subject][session][task][run-1] = output_bids_path
                            else:
                                # simply pass on the raw object to the next step
                                self.file_paths[subject][session][task][run-1] = answer
                        else: 
                            # pass on the path (or whatever it is) to the next step
                            self.file_paths[subject][session][task][run-1] = answer

                        