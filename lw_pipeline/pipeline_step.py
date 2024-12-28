"""Main pipeline class to abstract from pipeline steps."""

# Authors: The Lightweight Pipeline developers
# SPDX-License-Identifier: BSD-3-Clause

from abc import ABC, abstractmethod

from lw_pipeline.helper.naming import guess_short_id


class Pipeline_Step(ABC):
    """Abstract class for a pipeline step."""

    def __init__(self, description, config, short_id = ""):
        self.description = description

        if short_id:
            self._short_id = short_id 
        else:
            self._short_id = guess_short_id(self.__class__.__module__)

        self._config = config

    @property
    def config(self):
        """Configuration of the pipeline step."""
        return self._config

    @property
    def short_id(self):
        """Short id of the pipeline step."""
        return self._short_id

    @abstractmethod
    def step(self, data):
        """Abstract method to be implemented by the pipeline step."""
        pass

class Pipeline_Exception(Exception):
    """Exception class for the pipeline."""

    pass
