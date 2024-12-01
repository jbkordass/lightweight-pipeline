from abc import ABC, abstractmethod
from controller.config import Config

from helper.naming import guess_short_id

class PipelineStep(ABC):

    def __init__(self, description, config, short_id = ""):
        self.description = description

        if short_id:
            self._short_id = short_id 
        else:
            self._short_id = guess_short_id(self.__class__.__module__)

        self._config = config

    @property
    def config(self):
        return self._config
    
    @property
    def short_id(self):
        return self._short_id

    @abstractmethod
    def step(self, data):
        pass

class PipelineException(Exception):
    pass
