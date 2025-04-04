"""Conversion Step to Bids format."""

import os
import re
import shutil
from os import listdir
from os.path import join

import mne
import numpy as np
from mne_bids import (
    print_dir_tree,
    write_raw_bids,
)

from lw_pipeline import Pipeline_MNE_BIDS_Data, Pipeline_Step


class Conversion(Pipeline_Step):
    """
    Conversion Step to Bids format.

    For the sake of example, create a folder directory structure with random data as
    follows:

        * data/
            * raw/
                * session1/
                * session2/
                * ...

    Files in .edf format.

    Then convert this data to BIDS format in data/bids directory.
    """

    def __init__(self, config):
        super().__init__("Generate example data, then convert to BIDS format", config)

    def step(self, data):
        """
        Pipeline step.

        Generate example data, then convert to BIDS format.
        """
        config = self.config

        # check if config.data_dir has a raw directory and empty it
        raw_dir = join(config.data_dir, "raw")
        if os.path.exists(raw_dir):
            shutil.rmtree(raw_dir)
        os.makedirs(raw_dir, exist_ok=True)

        # generate random raw files
        for i in range(2):
            self._generate_random_raws(join(raw_dir, f"1001_session{i + 1}_task1.edf"))

        if config.eeg_path:
            print("EEG path already exists in config, skipping construction of one.")
        else:
            # construct a eeg_path dictionary from data dir structure
            eeg_path = {}

            filelist = listdir(raw_dir)  # get list of all files in raw directory

            for file in filelist:
                # find out subject id (4 digits) and session from file name
                match = re.search(
                    "(?P<subject>\\d{4})_(?P<session>session\\d{1})_task1.edf", file
                )
                if not match:
                    continue
                subject = match.group("subject")
                session = match.group("session")
                task = "task1"

                if eeg_path.get(subject) is None:
                    eeg_path[subject] = {}

                if eeg_path[subject].get(session) is None:
                    eeg_path[subject][session] = {}

                if eeg_path[subject][session].get(task) is None:
                    eeg_path[subject][session][task] = {}

                # run = '1' for all files currently..
                eeg_path[subject][session][task]["1"] = join("raw", file)

            # write the newly constructed eeg_path to the config
            config.set_variable_and_write_to_config_file("eeg_path", eeg_path)

        # Delete to make sure it is empty
        if os.path.exists(config.bids_root):
            shutil.rmtree(config.bids_root)
        os.makedirs(config.bids_root, exist_ok=True)

        if os.path.exists(config.deriv_root):
            shutil.rmtree(config.deriv_root)

        os.makedirs(config.deriv_root, exist_ok=True)

        # this is step 0, so create new data object
        data = Pipeline_MNE_BIDS_Data(config)

        # write the data to BIDS
        data.apply(
            self.write_converted,
            bids_root=config.bids_root,  # save to bids root instead of derivatives dir
            description=None,
            suffix="eeg",
            save=False,
        )

        # check directory tree where the files should have been written to
        try:
            print_dir_tree(config.bids_root)
        except Exception:
            print("Could not print directory tree")

        return data

    def write_converted(self, source, bids_path):
        """
        Write source (path) to bids_path using MNE BIDS package.

        Does an overwrite check before.
        """
        config = self.config

        if (
            not config.overwrite
            and bids_path.directory.exists()
            and bids_path.fpath.exists()
        ):
            print(
                f"\u26a0 File {bids_path.fpath} already exists. Skipping. "
                "(To change this behaviour, set config variable 'overwrite = True'.)"
            )
        else:
            try:
                raw = mne.io.read_raw(join(config.data_dir, source))

                write_raw_bids(
                    raw,
                    bids_path,
                    anonymize=dict(daysback=4000),
                    overwrite=config.overwrite,
                )

                # set extension using source extension
                bids_path.update(extension=source.split(".")[-1])

                print(
                    "Wrote bids",
                    bids_path.subject,
                    bids_path.session,
                    bids_path.task,
                    bids_path.run,
                    source,
                )
            except NotImplementedError:
                print(
                    "Having a problem writing to bids in ",
                    bids_path.subject,
                    bids_path.session,
                    bids_path.task,
                    bids_path.run,
                    source,
                )

        return bids_path

    def _generate_random_raws(self, file_name):
        from mne import create_info
        from mne.io import RawArray

        # Define parameters
        n_channels = 2
        n_seconds = 10
        sampling_rate = 500  # Hz

        # Generate random data
        data = np.random.randn(n_channels, n_seconds * sampling_rate)

        # Create channel labels
        channel_labels = [f"Channel {i + 1}" for i in range(n_channels)]

        # Create MNE info structure
        info = create_info(ch_names=channel_labels, sfreq=sampling_rate, ch_types="eeg")

        # Create Raw object
        raw = RawArray(data, info)

        # Write the data to an EDF file
        raw.export(file_name, fmt="edf")
