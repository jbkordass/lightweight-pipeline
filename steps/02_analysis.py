from controller.pipeline_step import PipelineStep
from controller.pipeline_data import PipelineData

from mne_bids import (
    BIDSPath
)

from mne.io import read_raw

class Analysis(PipelineStep):
    def __init__(self, config):
        super().__init__("Data analysis", config)

    def step(self, data):
        config = self.config

        if data is None:
            print("No data object found, try to find in derivatives files after preprocessing")
            data = PipelineData(config, from_deriv="preprocessing")
        
        data.apply(self.analysis)

        return data
    
    def analysis(self, source_file, subject, session, task, run):
        config = self.config

        print(source_file.directory, source_file.basename)

        # check if the source_file is an instance of BidsPath
        if isinstance(source_file, BIDSPath):
            source_file = source_file.fpath 

        raw = read_raw(source_file)
        raw_data = raw.get_data()

        return raw