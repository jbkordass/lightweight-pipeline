
A trivial Example
=================

This is a very simple example that shows how to set up the pipeline.

The project folder contains the following files:

.. code-block::

    📂 examples/trivial
    ├── 📂 steps
    │   ├── __init__.py     # Empty file marking directory as Python package.
    │   └── 00_start.py     # Implementation of the first step(s).
    │   └── 01_continue.py  # Implementation of the next step.
    └── config.py           # Configuration file for the pipeline.


The config file can be used to define custom variables.

.. literalinclude:: ../examples/trivial/config.py
    :language: Python
    :caption: config.py

In the context of an `lw_pipeline.Config` instance `config`, such a variable can be accessed as:

.. code-block:: python

    config.variable_a

Next we define some steps, i.e. subclasses of `lw_pipeline.Pipeline_Step` that implement the `step()` method. 
The steps are defined in the `steps` directory.

.. literalinclude:: ../examples/trivial/steps/00_start.py
    :language: Python
    :caption: steps/00_start.py

.. literalinclude:: ../examples/trivial/steps/01_continue.py
    :language: Python
    :caption: steps/01_continue.py

Already with this setups we can run the pipeline with the following command:

.. code-block:: shell

    $ lw_pipeline -c config.py --run

.. code-block:: text
    :caption: Output
    
    Using configuration file: config.py, assuming it's a python file
    Running entire pipeline
    --------------------------------Step 1: 00_start--------------------------------
    This is a description of a first step.
    Here data is 'None', we set it to variable_a from the config.
    This is a description of a second step.
    Here data is '1'. We will add 1 to it.
    ------------------------------Step 2: 01_continue-------------------------------
    This is a description of a continued step.
    Here data is '2'. We will subtract 2.
    --------------------Pipeline finished with following output:--------------------
    0
