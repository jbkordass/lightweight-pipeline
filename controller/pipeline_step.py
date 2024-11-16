from abc import ABC, abstractmethod
from controller.config import Config

class PipelineStep(ABC):

    def __init__(self, description, config, short_id = ""):
        self.description = description
        if short_id:
            self.short_id = short_id
        else:
            # cook up sth by using first letters in description
            ''.join([w[0].lower() for w in description.split()])
        self._config = config

    @property
    def config(self):
        return self._config

    @abstractmethod
    def step(self, data):
        pass


class PipelineException(Exception):
    pass
