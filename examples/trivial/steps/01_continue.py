from lw_pipeline import Pipeline_Step, Pipeline_Exception

class A_Continued_Pipeline_Step(Pipeline_Step):
    def __init__(self, config):
        super().__init__("This is a description of a continued step.", config)

    def step(self, data):
        print(f"Here data is '{data}'. We will subtract 2.")
        if type(data) is not int:
            data = 0
        data -= 2
        return data
