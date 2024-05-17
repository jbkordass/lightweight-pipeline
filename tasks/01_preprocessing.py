import model.pipeline_element as pe

class Preprocessing(pe.PipelineElement):
    def __init__(self):
        super().__init__("Preprocessing data")

    def process(self, data, config):
        # Add your preprocessing logic here

        return data