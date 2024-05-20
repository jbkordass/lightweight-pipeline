from model.pipeline_step import PipelineStep

class Preprocessing(PipelineStep):
    def __init__(self):
        super().__init__("Preprocessing data")

    def process(self, data, config):
        # Add your preprocessing logic here

        return data