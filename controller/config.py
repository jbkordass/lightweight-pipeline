
import os
import sys
import importlib

class Config:
    """
    A class representing the configuration settings.
    """

    _config_file_path = None
    """The path to an external configuration file."""

    def __init__(self, config_file_path=None):
        """
        Initialize the Config object.

        Args:
            config_file_path (str): The path to the configuration file. If provided, the configuration settings will be
                updated based on the variables defined in the file.
        """
        if config_file_path:
            self._config_file_path = config_file_path
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

    def ask(self, message, default = "n"):
        """
        Ask to do something, e.g. before potentially deleting data, etc.

        Make sure to specify options, e.g. (y/n), in the message.
        """
        if self.auto_response == "off":
            try:
                response = input(f"\u26A0 Question: {message}: ")
            except EOFError:
                # e.g. if not run interactively
                raise PipelineException(f"Could not obtain response to question: ({message}). \
                        Make sure to specify auto_response in the config, or run with --ignore-questions to use the default response")
            return response
        elif self.auto_response == "default":
            return default
        else:
            return self.auto_response

    def set_variable_and_write_to_config_file(self, variable, value):
        """
        Set a variable in this class and if it does not exist in the the configuration file,
        then add a line with the specified value.

        Args:
            variable (str): The name of the variable to update.
            value (mixed): The value to set the variable to.
        """
        if hasattr(self, variable) and getattr(self, variable):
            print("Error: Cannot overwrite already set variable in configuration file.")
            return
        
        if not self._config_file_path:
            print("Error: No configuration file specified. Cannot update default configuration file.")
            return

        setattr(self, variable, value)
        with open(self._config_file_path, "a") as f:
            f.write(f"\n{variable} = {value}\n")
        print(f"Configuration file updated: {self._config_file_path}")

    def get_version(self):
        """
        Get the version of the pipeline by getting the last commit hash from the git repository.
        """
        try:
            import subprocess
            # make sure to execute git commands in the root directory of the repository
            root_dir = os.path.dirname(os.path.abspath(__file__))
            git_hash = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=root_dir).strip().decode("utf-8")
            version = f"git-{git_hash}"
        except:
            version = "unknown"
        return version


    # general default variables
    # -------------------------

    steps_dir = os.path.join(os.path.dirname(__file__), '../steps')
    """Steps directory, can also be chosen outside of the default location!"""

    auto_response = "off"
    """Decide how questions are answered (off/y/n/default)"""

    data_dir = os.path.join(os.path.expanduser('~'), 'data')
    """Default data directory"""

    bids_root = os.path.join(data_dir, 'bids')
    """Root directory for BIDS formatted data"""

    subjects = []
    """List of subjects to include in the pipeline processing. If empty list, include all subjects"""

    sessions = []
    """List of sessions to include in the pipeline processing. If empty list, include all sessions"""

    tasks = []
    """List of tasks to include in the pipeline processing. If empty list, include all tasks"""

    # variables for PipelineData class
    # --------------------------------

    deriv_root = os.path.join(data_dir, 'derivatives')
    """Root directory for derivatives"""

    overwrite = False
    """Overwrite existing derivative files, if False they are skipped"""
    
    eeg_path = {}
    """Path to the eeg data which should be converted to BIDS

    Structure: subject -> condition -> task -> list of eeg files (runs)
    File names expected relative to data_dir"""

    bids_acquisition = None
    """EEG information that should be included in the BIDS file"""

    bids_datatype = "eeg"
    """BIDS datatype of the data created as derivatives in the pipeline"""

    bids_extension = ".edf"
    """Extension of the BIDS files in the bids root directory"""

    n_jobs = 1
    """Number of parallel jobs to run"""

    # default variables for conversion ...

    # default variables preprocessing ...

    # default values analysis ...