
import os
import sys
import importlib


class Config:
    """
    A class representing the configuration settings.
    """

    def __init__(self, config_file_path=None):
        """
        Initialize the Config object.

        Args:
            config_file_path (str): The path to the configuration file. If provided, the configuration settings will be
                updated based on the variables defined in the file.
        """
        if config_file_path:
            config_file = os.path.abspath(config_file_path)
            if os.path.isfile(config_file):
                config_dir = os.path.dirname(config_file)
                sys.path.insert(0, config_dir)  # add the config directory to the module search path

                module_name = os.path.splitext(os.path.basename(config_file))[0]
                config_module = importlib.import_module(module_name)
            
                # Update the current variables in the this class with the ones from the specified configuration file
                vars(self).update({k: v for k, v in vars(config_module).items() if not k.startswith("_")} )
            
                print(f"Using configuration file: {config_file_path}, assuming it's a python file")
            else:
                print(f"Error: Configuration file {config_file_path} does not exist; using default configuration.")
        else:
            print("Using default configuration file.")


    # default data directory
    data_dir = os.path.join(os.path.expanduser('~'), 'data')

    # default variables bids conversion ...

    # path to the eeg data which should be converted to BIDS
    # structure: subject -> condition -> task -> list of edf files
    eeg_path = {}

    # EEG information that should be included in the BIDS file
    eeg_acquisition = "eeg"
    eeg_file_extension = ".edf"

    # subjects that should be included in the pipeline processing
    # if empty list, include all subjects
    subjects = []

    # default variables preprocessing ...

    # default values analysis ...