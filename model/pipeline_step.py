from abc import ABC, abstractmethod
from model.config import Config

class PipelineStep(ABC):

    def __init__(self, description, config):
        self.description = description
        self._config = config

    @property
    def config(self):
        return self._config

    def ask_permission(self, message):
        """
        Ask for permission to do something potentially deleting data, etc.
        """
        response = self.config.auto_response
        # default value is "n", so only ask in this case
        if response == "n":
            try:
                response = input(f"\u26A0 Warning: {message} (y/n): ")
            except EOFError:
                # e.g. if not run interactively
                print("Using config value for auto_response")
        return response.lower() == "y"

    @abstractmethod
    def step(self, data):
        pass


class PipelineException(Exception):
    pass
