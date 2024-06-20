from model.pipeline_step import PipelineStep
from model.pipeline_data import PipelineData
import os

from mne_bids import (
    BIDSPath,
    read_raw_bids
)

from mne.io import read_raw

class Preprocessing(PipelineStep):
    def __init__(self, config):
        super().__init__("Preprocessing data", config)

    def step(self, data):

        config = self.config

        if data is None:
            print("No data object found, creating new one")
            data = PipelineData(config, from_bids=True)
        
        data.apply(self.preprocessing)

        return data
    
    def preprocessing(self, source_file, subject, session, task, run):
        config = self.config

        # check if the source_file is an instance of BidsPath
        if isinstance(source_file, BIDSPath):
            source_file = source_file.fpath 

        raw = read_raw(source_file)
        raw_data = raw.get_data()

        info = raw.info
        channels =raw.ch_names
        annotations = raw.annotations

        set_types = {}
        for channel in channels:
            
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

        # events = mne.events_from_annotations(raw)
        raw = raw.resample(300) #, events=events)

        return raw