from lw_pipeline import Pipeline_Step


class A_First_Start_Pipeline_Step(Pipeline_Step):
    def __init__(self, config):
        super().__init__("This is a description of a first step.", config)

    def step(self, data):
        print(f"Here data is '{data}', we set it to variable_a from the config.")
        data = self.config.variable_a
        return data


class A_Second_Start_Pipeline_Step(Pipeline_Step):
    def __init__(self, config):
        super().__init__("This is a description of a second step.", config)

    def step(self, data):
        print(f"Here data is '{data}'. We will add 1 to it.")
        data += 1
        return data
