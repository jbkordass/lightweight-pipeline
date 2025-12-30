"""Main pipeline class to abstract from pipeline steps."""

# Authors: The Lightweight Pipeline developers
# SPDX-License-Identifier: BSD-3-Clause

import logging
from abc import ABC, abstractmethod

from lw_pipeline.helper.naming import guess_short_id
from lw_pipeline.output_manager import Output_Manager
from lw_pipeline.output_registration import Output_Registry


class Pipeline_Step(ABC):
    """Abstract class for a pipeline step."""

    def __init__(self, description, config, short_id=""):
        self.description = description

        if short_id:
            self._short_id = short_id
        else:
            self._short_id = guess_short_id(self.__class__.__module__)

        self._config = config

        # Initialize output management
        self._output_manager = None
        self._output_registry = None
        
        # Initialize logger for this step
        self._logger = None

    @property
    def logger(self):
        """
        Get a logger for this pipeline step.

        Returns
        -------
        logging.Logger
            Logger instance named after this step.
        """
        if self._logger is None:
            self._logger = logging.getLogger(f"lw_pipeline.step.{self.short_id}")
        return self._logger

    @property
    def config(self):
        """Configuration of the pipeline step."""
        return self._config

    @property
    def short_id(self):
        """Short id of the pipeline step."""
        return self._short_id

    @property
    def output_manager(self):
        """
        Get the Output_Manager for this step.

        Returns
        -------
        Output_Manager
            Manager for saving outputs with consistent paths and metadata.
        """
        if self._output_manager is None:
            self._output_manager = Output_Manager(
                self.config, self.short_id, self.description
            )
        return self._output_manager

    @property
    def output_registry(self):
        """
        Get the Output_Registry for this step.

        Returns
        -------
        Output_Registry
            Registry of registered outputs for this step.
        """
        if self._output_registry is None:
            self._output_registry = Output_Registry(self)
        return self._output_registry

    def get_output_path(self, name, suffix=None, extension=None,
                       use_bids_structure=False, custom_dir=None, **bids_params):
        """
        Get an output file path for this step.

        This is a convenience wrapper around output_manager.get_output_path().

        Parameters
        ----------
        name : str
            Output name (will be prefixed with step_id).
        suffix : str, optional
            BIDS suffix.
        extension : str, optional
            File extension.
        use_bids_structure : bool, optional
            Use BIDS directory structure. Default is False.
        custom_dir : str or Path, optional
            Custom output directory.
        **bids_params : dict
            BIDS parameters (subject, session, task, run, datatype).

        Returns
        -------
        Path
            Output file path.
        """
        return self.output_manager.get_output_path(
            name, suffix=suffix, extension=extension,
            use_bids_structure=use_bids_structure,
            custom_dir=custom_dir, **bids_params
        )

    def should_generate_output(self, name):
        """
        Check if a specific output should be generated.

        This method checks the configuration and registered outputs to
        determine if the output matching the given name should be generated.
        Use this in methods decorated with @register_output to conditionally
        skip expensive computations.

        Parameters
        ----------
        name : str
            Name of the output to check.

        Returns
        -------
        bool
            True if the output should be generated.

        Examples
        --------
        >>> @register_output("expensive_plot", enabled_by_default=False)
        >>> def create_plot(self):
        ...     if not self.should_generate_output("expensive_plot"):
        ...         return
        ...     # ... expensive plotting code ...
        """
        return self.output_registry.should_generate(name, self.config)

    @abstractmethod
    def step(self, data):
        """Abstract method to be implemented by the pipeline step."""
        pass


class Pipeline_Exception(Exception):
    """Exception class for the pipeline."""

    pass
