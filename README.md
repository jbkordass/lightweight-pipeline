# About the Lightweight Pipeline
As the name suggests - a lightweight, easy to modify pipeline. Initially built for EEG analysis using MNE python and MNE-BIDS.

Main design criterion is to keep the controller part minimal.

## Table of Contents

- [Goals](#goals)
- [Usage: rough idea and trivial example](#usage-rough-idea-and-trivial-example)
- [Minimal example (to use with MNE-BIDS)](#minimal-example-to-use-with-mne-bids)
- [Installation](#installation)
- [Contributing](#contributing)
- [License](#license)
- [Comparison](#comparison)

## Goals
- Provide a scheme to model concrete pipeline steps after.
- Take care of a configuration file handling and saving/loading to some extend.
- Decouple the content of a pipeline, i.e. its processing logic, from the organizatorial part.


## Usage: rough idea and trivial example

Start by creating a project folder containing:

`steps/__init__.py`: empty

`steps/00_steps.py`:
```python
from lw_pipeline import Pipeline_Step

class A_First_Pipeline_Step(Pipeline_Step):
    def __init__(self, config):
        super().__init__("This is a description of a first step.", config)

    def step(self, data):
        print(f"Here data is '{data}'.")
        data = self.config.variable_a
        return data

class A_Second_Pipeline_Step(Pipeline_Step):
    def __init__(self, config):
        super().__init__("This is a description of a second step.", config)

    def step(self, data):
        print(f"Here data is '{data}'.")
        return data
```

`config.py`:
```python
steps_dir = "steps/"

variable_a = 1
```

Now run the following command in the project directory to list the steps detected
```shell
lw_pipeline -c config.py --list
```
while
```shell
lw_pipeline -c config.py --run
```
runs the pipeline entirely. Use `--help` for further parameter info.
You can find a similar example in [examples/trivial/](examples/trivial/).

In a more interesting case, one would pass a data object, e.g. a subclass of `Pipeline_Data`, through the pipeline. As of now, the pipeline comes with a data container class for processing eeg/meg data utilizing `MNE-BIDS`.


## Minimal example (to use with MNE-BIDS)

For a more interesting example demonstrating eeg/meg processing, we refer to a [minimal example](examples/minimal_example.md).


## Installation
To install, clone the github repository, navigate to the folder and execute (for an editable install)
```shell
pip install -e ".[dev]"
```

## Contributing

Contributions are welcome! Please fork the repository, create a feature branch, and submit a pull request.


## License

This project is licensed under the BSD 3-Clause License. See the [LICENSE](LICENSE) file for details.


## Comparison

- The [MNE-BIDS-Pipeline](https://github.com/mne-tools/mne-bids-pipeline) provides an actual eeg/meg processing pipeline that bundles logic and content.