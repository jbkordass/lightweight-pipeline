import model.pipeline_element as pe

class Analysis(pe.PipelineElement):
    def __init__(self):
        super().__init__("Data analysis")

    def process(self, data):
        # Add your preprocessing logic here
        
        pass