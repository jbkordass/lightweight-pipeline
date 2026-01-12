"""Core Pipeline class for orchestrating pipeline steps."""

# Authors: The Lightweight Pipeline developers
# SPDX-License-Identifier: BSD-3-Clause

import sys

from lw_pipeline.pipeline_step import Pipeline_Exception, Pipeline_Step


class Pipeline:
    """
    Pipeline class to run pipeline steps in sequence.

    The Pipeline orchestrates the execution of multiple pipeline steps,
    passing data through each step in order and handling errors appropriately.

    Parameters
    ----------
    steps : list of Pipeline_Step
        A list of Pipeline_Step instances to execute in sequence.

    Attributes
    ----------
    pipeline_steps : list of Pipeline_Step
        The steps to be executed.

    Examples
    --------
    >>> from lw_pipeline import Pipeline, Pipeline_Step, Config
    >>>
    >>> class Multiply_Step(Pipeline_Step):
    ...     def __init__(self, factor, config):
    ...         super().__init__(f"Multiply by {factor}", config)
    ...         self.factor = factor
    ...     def step(self, data):
    ...         return data * self.factor
    >>>
    >>> config = Config()
    >>> step1 = Multiply_Step(2, config)
    >>> step2 = Multiply_Step(3, config)
    >>> pipeline = Pipeline([step1, step2])
    >>> result = pipeline.run(5)  # 5 * 2 * 3 = 30
    """

    def __init__(self, steps):
        """
        Initialize the Pipeline.

        Parameters
        ----------
        steps : list of Pipeline_Step
            A list of Pipeline_Step instances to execute in sequence.

        Raises
        ------
        ValueError
            If steps is not a list of Pipeline_Step instances.
        """
        if not all(isinstance(step, Pipeline_Step) for step in steps):
            raise ValueError(
                "All steps must be Pipeline_Step instances. "
                "Use discovery.find_all_step_classes() to load steps from files."
            )
        self.pipeline_steps = steps

    def run(self, data=None):
        """
        Run the pipeline.

        Execute all pipeline steps in sequence, passing data from one
        step to the next. Handles Pipeline_Exception errors and reports
        progress.

        Parameters
        ----------
        data : object, optional
            Optional input data to be passed to the first step.
            Default is None.

        Returns
        -------
        data : object
            The output data after processing through all pipeline steps.

        Raises
        ------
        SystemExit
            If a Pipeline_Exception occurs during step execution.
        """
        pos = 1

        if data is not None:
            print("Pipeline starts with following input:".center(80, "-"))
            print(data)

        for step in self.pipeline_steps:
            # Print step information
            print(
                f"Step {pos}: {step.__class__.__module__} / "
                f"{step.__class__.__name__}".center(80, "-")
            )
            pos += 1

            print("ℹ " + step.description)

            try:
                data = step.step(data)
            except Pipeline_Exception as e:
                print(f"Error in {step.description}: {e}")
                sys.exit(1)

        print("Pipeline finished with following output:".center(80, "-"))
        print(data)

        return data
