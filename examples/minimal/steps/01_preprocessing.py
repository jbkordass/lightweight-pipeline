
from lw_pipeline import Pipeline_MNE_BIDS_Data, Pipeline_Step
from lw_pipeline.helper.mne import raw_from_source

class Preprocessing(Pipeline_Step):
    """
    Preprocessing Step to preprocess the data.
    
    Apply a notch filter to remove power line artifact and resample the data to a lower frequency.
    
    Relevant config variables:
    - notch_filter: Notch filter to remove power line artifact.
    - resample_freq: Frequency to resample the data to.
    - n_jobs: Number of parallel jobs.
    """

    def __init__(self, config):
        super().__init__("Preprocessing data.", config)

    def step(self, data):
        config = self.config

        if data is None:
            print("No data object found, creating new one")
            data = Pipeline_MNE_BIDS_Data(config, from_bids=True)
        
        data.apply(self.preprocessing)

        return data
    
    def preprocessing(self, source, bids_path):
        
        config = self.config

        raw = raw_from_source(source, preload=True)

        # apply a notch filter to remove power line artifact
        raw.notch_filter(config.notch_filter, n_jobs=config.n_jobs)

        # resample to lower frequency 
        raw.resample(config.resample_freq, n_jobs=config.n_jobs)

        # write some information to the sidecar json
        sidecar_updated_info = {
            "Preprocessing": {
                "NotchFilter": str(config.notch_filter),
                "ResampleFreq": config.resample_freq,
            }
        }

        return raw, sidecar_updated_info