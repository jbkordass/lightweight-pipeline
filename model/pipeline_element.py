from abc import ABC, abstractmethod
import model.config

class PipelineElement(ABC):

    def __init__(self, description):
        self.description = description

    @abstractmethod
    def process(self, data, config):
        pass
