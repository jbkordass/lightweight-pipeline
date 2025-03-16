import mne
import numpy as np
from mne_bids import find_matching_paths

from lw_pipeline import Pipeline_MNE_BIDS_Data, Pipeline_Step
from lw_pipeline.helper.mne import raw_from_source


class Continue_With_More_Data_Analysis(Pipeline_Step):
    """
    Continue with more data analysis.

    Annotate the data with markers every 1 second and plot the first channel of the raw data.

    Relevant config variables:
    - None
    """

    def __init__(self, config):
        super().__init__("Data analysis or something..", config)

    def step(self, data):
        config = self.config

        if data is None:
            print("No data object found, try to find in derivatives files after preprocessing")
            data = Pipeline_MNE_BIDS_Data(config, from_deriv="01Preprocessing")
        
        # generate some annotations and save them
        data.apply(self.annotate, suffix="markers", save=True)

        # do save .fif file, but save plot as pdf manually
        data.apply(self.analysis, save=False)

        return data
    
    def annotate(self, source, bids_path):

        raw = raw_from_source(source, preload=True)

        # create annotations every 1 second in the data
        onset = np.arange(0, raw.times[-1], 1)
        duration = np.ones_like(onset)
        description = ['Marker'] * len(onset)
        annotations = mne.Annotations(onset, duration, description)

        return annotations
    
    def analysis(self, source, bids_path):

        config = self.config

        raw = raw_from_source(source, preload=True)

        bids_path_annotate = find_matching_paths(subjects=bids_path.subject, 
                               sessions=bids_path.session, 
                               tasks=bids_path.task, 
                               runs=bids_path.run, 
                               descriptions=self.short_id + "Annotate",
                               suffixes="markers", 
                               extensions=".fif", 
                               root=config.deriv_root)
        
        annots = mne.read_annotations(bids_path_annotate[0].fpath)

        raw.set_annotations(annots)

        import matplotlib.pyplot as plt

        # plot the first channel of the raw data using matplotlib
        fig, ax = plt.subplots()
        ax.plot(raw.times, raw.get_data(picks=[0]).T)
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Amplitude')
        ax.set_title('First Channel Data')

        # add markers to the plot
        for ann in raw.annotations:
            ax.axvline(ann['onset'], color='r', linestyle='--', alpha=0.5)

        plt.show()

        # save the plot, use short_id to have the same prefix as derivaties from this step
        bids_path_plot = bids_path.copy().update(
                    extension=".pdf",
                    description=self.short_id + "FirstChannelPlot")
        
        fig.savefig(bids_path_plot.fpath)
    
        return raw
    