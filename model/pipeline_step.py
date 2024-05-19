from abc import ABC, abstractmethod
import model.config

class PipelineStep(ABC):

    def __init__(self, description):
        self.description = description

    @abstractmethod
    def process(self, data, config):
        pass
