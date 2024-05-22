from abc import ABC, abstractmethod
from model.config import Config

class PipelineStep(ABC):

    def __init__(self, description, config):
        self.description = description
        self._config = config

    @property
    def config(self):
        return self._config

    @abstractmethod
    def process(self, data):
        pass
