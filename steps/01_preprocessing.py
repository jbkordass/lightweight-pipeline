from controller.pipeline_step import PipelineStep
from controller.pipeline_data import PipelineData
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

        # events = mne.events_from_annotations(raw)
        raw = raw.resample(300) #, events=events)

        # write some information to the sidecar json
        sidecar_updated_info = {
            "Preprocessing": {
                "ResampleFreq": 300,
            }
        }

        return raw, sidecar_updated_info