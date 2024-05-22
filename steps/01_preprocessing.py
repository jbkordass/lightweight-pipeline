from model.pipeline_step import PipelineStep

class Preprocessing(PipelineStep):
    def __init__(self, config):
        super().__init__("Preprocessing data", config)

    def process(self, data):
        # Add your preprocessing logic here

        return data