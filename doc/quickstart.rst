
Quickstart
----------

Rough idea:

#. Write a :file:`config.py` specifying the locations of steps, data, and other configurations.
#. Define the steps of a pipeline in separate :file:`.py` files and store them in a folder.
#. Pass the :file:`config.py` to the pipeline CLI, which will handle the execution order based on a naming convention.


Config
~~~~~~

The configuration class :class:`Config <lw_pipeline.Config>` is used to manage the configuration settings for your pipeline.
If passed a path to a file all defined variables in the file will be available as attributes of the :class:`Config <lw_pipeline.Config>` instance.

.. code-block:: python

    from lw_pipeline import Config

    config = Config("some/example/path")


Pipeline_Step
~~~~~~~~~~~~~

:class:`Pipeline_Step <lw_pipeline.Pipeline_Step>` is an abstract base class that you can subclass to define individual steps in your pipeline. 
Each step should implement the :func:`step() <lw_pipeline.Pipeline_Step.step>` method, which contains the processing logic for that step.

.. code-block:: python

    from lw_pipeline import Config, Pipeline_Step

    class Example_Step(Pipeline_Step):
        def __init__(self, config):
            super().__init__("This is an example step.", config)

        def step(self, data):
            # Processing logic for this step
            processed_data = data * 2  # Example operation
            return processed_data

    config = Config()
    step = Example_Step(config=config)
    
    input_data = 5
    output_data = step.step(input_data)
    print(f"Input: {input_data}, Output: {output_data}")

In practice, it is not necessarily meant to be instantiated except for demonstration or testing.
The CLI part of the pipeline aggregates all steps and handles running them.


Pipeline_Data
~~~~~~~~~~~~~

The abstract :class:`Pipeline_Data <lw_pipeline.Pipeline_Data>` class is used to manage the data that flows through the pipeline.
As of now, the pipeline comes with a :class:`Pipeline_MNE_BIDS_Data <lw_pipeline.Pipeline_MNE_BIDS_Data>` class that is used to handle MNE-BIDS data.


We refer to the :doc:`minimal example<minimal_example>` for a more detailed explanation.


Command line interface
~~~~~~~~~~~~~~~~~~~~~~

The package defines a :code:`lw_pipeline` CLI accepting the following arguments:

.. glossary::

    :code:`-v, --version`
        Show the version of the pipeline.

    :code:`-r, --run`
        Run the pipeline.

    :code:`steps`
        Positional argument. List of steps to run, separated by commas (only necessary to specify 00-99).

    :code:`-c, --config`
        Path to the configuration file.

    :code:`-l, --list`
        List all steps in the step directory.

    :code:`--list-derivatives`
        List methods in steps that could be used to produce derivatives.

    :code:`--ignore-questions`
        Ignore questions, i.e., always respond with the default answer to a question.

    :code:`--report`
        Generate a report of the pipeline's derivatives.

    :code:`--store-report`
        Store the report tables in `.tsv` files in the derivatives directory (e.g., `pipeline_report_bids_dir.tsv`, `pipeline_report_deriv_dir.tsv`).

    :code:`--full-report`
        Generate a full report (do not limit to subject, session, task specification in the config) of the pipeline's derivatives.