"""Configuration settings to pass throught the pipeline."""

# Authors: The Lightweight Pipeline developers
# SPDX-License-Identifier: BSD-3-Clause

import importlib
import os
import sys

from lw_pipeline import Pipeline_Exception


class Config:
    """A class representing the configuration settings."""

    config_file_path = None
    """The path to an external configuration file."""

    def __init__(self, config_file_path=None, verbose=False):
        """
        Initialize the Config object.

        Parameters
        ----------
        config_file_path : str, optional
            The path to the configuration file. If provided, the configuration
            settings will be updated based on the variables defined in the file.
        verbose : bool, optional
            If True, print messages about the configuration file being used.
            Default is False.
        """
        if config_file_path:
            self.config_file_path = config_file_path
            config_file = os.path.abspath(config_file_path)
            if os.path.isfile(config_file):
                config_dir = os.path.dirname(config_file)
                sys.path.insert(
                    0, config_dir
                )  # add the config directory to the module search path

                self._load_file_to_variables(
                    config_file, verbose=verbose
                )

                # check for a local version of the config file
                config_basename, config_ext = os.path.splitext(
                    os.path.basename(config_file)
                )
                local_config_file = os.path.join(
                    config_dir, f"{config_basename}_local{config_ext}"
                )
                if os.path.isfile(local_config_file):
                    self._load_file_to_variables(local_config_file, verbose=verbose)

            else:
                raise FileNotFoundError(
                    f"Specified configuration file not found: {config_file_path}."
                )
        else:
            if verbose:
                print("Using default configuration file.")

    def _load_file_to_variables(self, file_path, verbose=False):
        """Load variables from a specified configuration file into the current class."""
        module_name = os.path.splitext(os.path.basename(file_path))[0]
        config_module = importlib.import_module(module_name)

        # Update the current variables in the this class with the ones from
        # the specified configuration file
        vars(self).update(
            {
                k: v
                for k, v in vars(config_module).items()
                if not k.startswith("_")
            }
        )
        self.check_steps_dir()

        if verbose:
            print(f"Using configuration file: {file_path}.")

    def check_steps_dir(self):
        """
        Make sure steps dir is absolute.

        Notes
        -----
        - If `config_file_path` is not `None`, the relative `steps_dir` is
          resolved relative to the directory containing the configuration file.
        - If `config_file_path` is `None`, the relative `steps_dir` is resolved
          relative to the current working directory.

        Parameters
        ----------
        steps_dir : str
            The directory path for steps, which will be converted to an absolute path.
        config_file_path : str or None
            The path to the configuration file, used to resolve relative paths.
        """
        value = self.steps_dir
        # check if steps dir is relative in that case make it relative to config file
        # or the current working directory
        if not os.path.isabs(value):
            # check if there is an externatl config file or if default config is used
            if self.config_file_path is not None:
                value = os.path.join(os.path.dirname(self.config_file_path), value)
            else:
                value = os.path.join(os.getcwd(), value)

        # make steps dir absolute
        value = os.path.abspath(value)

        self.steps_dir = value

    def ask(self, message, default="n"):
        """
        Ask to do something, e.g. before potentially deleting data, etc.

        Make sure to specify options, e.g. (y/n), in the message.
        """
        if self.auto_response == "off":
            try:
                response = input(f"\u26a0 Question: {message}: ")
            except EOFError:
                # e.g. if not run interactively
                raise Pipeline_Exception(
                    f"Could not obtain response to question: ({message}). "
                    "Make sure to specify auto_response in the config, or run "
                    "with --ignore-questions to use the default response."
                )
            return response
        elif self.auto_response == "default":
            return default
        else:
            return self.auto_response

    def set_variable_and_write_to_config_file(self, variable, value):
        """
        Set a variable in this class and write to config file, if not defined there.

        For safety, only allow to write variables that are not already set.

        Args:
            variable (str): The name of the variable to update.
            value (mixed): The value to set the variable to.
        """
        if hasattr(self, variable) and getattr(self, variable):
            raise Pipeline_Exception(
                "Cannot overwrite already set variable in configuration file."
            )
            return

        if not self.config_file_path:
            raise Pipeline_Exception("No configuration file specified .")
            return

        setattr(self, variable, value)
        with open(self.config_file_path, "a") as f:
            f.write(f"\n{variable} = {value}\n")
        print(f"Configuration file updated: {self.config_file_path}")

    def get_version(self):
        """
        Get a version of the pipeline by getting last commit hash from the git.

        Cave: This only works if the pipeline is in a git repository.
        If not, it will return "unknown".
        """
        try:
            import subprocess

            # make sure to execute git commands in the root directory of the repository
            root_dir = os.path.dirname(os.path.abspath(__file__))
            git_hash = (
                subprocess.check_output(
                    ["git", "rev-parse", "--short", "HEAD"], cwd=root_dir
                )
                .strip()
                .decode("utf-8")
            )
            version = f"git-{git_hash}"
        except Exception:
            version = "unknown"
        return version

    # general default variables
    # -------------------------

    steps_dir = "steps/"
    """Steps directory relative to config file or current working directory if no """
    """external config file is used."""

    auto_response = "off"
    """Decide how questions are answered (off/y/n/default)"""

    data_dir = os.path.join(os.path.expanduser("~"), "data")
    """Default data directory"""

    bids_root = os.path.join(data_dir, "bids")
    """Root directory for BIDS formatted data"""

    subjects = []
    """List of subjects to include in the pipeline processing. If empty list, \
        include all subjects"""

    sessions = []
    """List of sessions to include in the pipeline processing. If empty list, \
        include all sessions"""

    tasks = []
    """List of tasks to include in the pipeline processing. If empty list, \
        include all tasks"""

    # variables for PipelineData class
    # --------------------------------

    deriv_root = os.path.join(data_dir, "derivatives")
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
