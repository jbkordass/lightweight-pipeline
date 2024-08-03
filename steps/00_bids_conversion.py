from controller.pipeline_step import PipelineStep, PipelineException
from controller.pipeline_data import PipelineData
import os
import shutil

import mne
from mne_bids import (
    BIDSPath,
    write_raw_bids,
    print_dir_tree,
)

class Bids_Conversion(PipelineStep):
    def __init__(self, config):
        super().__init__("Preprocessing data", config)

    def step(self, data):

        config = self.config

        # There is the root directory for where we will write our data.
        bids_root = config.bids_root

        # Delete to make sure it is empty
        if os.path.exists(bids_root):
            if self.ask_permission(f"Delete existing bids_root directory? ({bids_root})"):
                shutil.rmtree(bids_root)
            else:
                raise PipelineException("Please delete existing bids_root directory by hand (or run with --ignore-warnings).")

        # this is step 0, so create new data object
        data = PipelineData(config)

        # write the data to BIDS
        data.apply(self.write_to_bids, subjects = config.subjects)                          

        # check directory tree where the files should have been written to
        try:
            print_dir_tree(bids_root)
        except:
            print("Could not print directory tree")

        return data
    
    def write_to_bids(self, source_file, subject, session, task, run):
        config = self.config

        bids_path = PipelineData.get_bids_path(self, source_file, subject, session, task, run)
        raw = mne.io.read_raw(config.data_dir + os.path.sep + source_file)

        # set channel types correctly according to channel names 
        set_types = {}
        for channel in raw.ch_names:
            
            if "EMG" in channel:
                t="emg"
            elif "EKG" in channel:
                t="ecg"
            elif "EOG" in channel:
                t="eog"
            elif "EEG" in channel:
                t="eeg"
            elif "Nase" in channel:
                t="eeg"
            else:
                t="seeg"      
            set_types[channel] = t

        raw.set_channel_types(set_types)

        write_raw_bids(
            raw, 
            bids_path, 
            anonymize=dict(daysback=40000),
            overwrite=True
        )
        print("Wrote bids", subject, session, task, run, source_file)

        return bids_path