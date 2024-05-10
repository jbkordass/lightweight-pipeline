from abc import ABC, abstractmethod

class PipelineElement(ABC):

    def __init__(self, description):
        self.description = description

    @abstractmethod
    def process(self, data):
        pass
