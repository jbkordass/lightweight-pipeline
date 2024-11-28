from abc import ABC, abstractmethod
from controller.config import Config

class PipelineStep(ABC):

    def __init__(self, description, config, short_id = ""):
        self.description = description

        if not short_id:
            short_id = ""
            # get the module name and cook up some naming
            module_name = self.__class__.__module__.split(".")[-1].split("_")
            for i, word in enumerate(module_name):
                # check if word is just numbers
                if word.isdigit():
                    short_id += word
                else:
                    # if we do not get enough numbers in the beginning, use first letters
                    if len(short_id) < 2:
                        short_id += word[0].lower()
        self.short_id = short_id

        self._config = config

    @property
    def config(self):
        return self._config

    @abstractmethod
    def step(self, data):
        pass


class PipelineException(Exception):
    pass
