
Minimal Example
===============

This section provides an overview of a minimal example pipeline setup processing EEG data using the `MNE-BIDS <https://mne.tools/mne-bids/>`_ package.

It demonstrates

#. More complex pipeline steps.
#. Using the :class:`Pipeline_MNE_BIDS_Data <lw_pipeline.Pipeline_MNE_BIDS_Data>` class to handle MNE-BIDS data.
#. Running the pipeline (interactively) from a jupyter notebook.
#. Using `Sphinx doc <https://www.sphinx-doc.org/en/master/index.html>`_ to document the pipeline steps.


Folder Structure
----------------

The minimal example folder contains the following files: 

.. code-block:: text

    📂 examples/minimal
    ├── 📂 steps/                 # Steps 
    │   ├── 00_conversion.py
    │   ├── 01_preprocessing.py
    │   ├── 02_continue.py
    │   ├── __init__.py           # Marks the directory as a Python package
    ├── 📂 doc/                   # Sphinx documentation of steps.
    │   ├── index.rst             
    │   └── ...                   
    ├── config.py                 # Configuration file for the pipeline
    ├── Makefile
    └── run.ipynb                 # Jupyter Notebook for running the pipeline


(cf. `Example Code at Github <https://github.com/jbkordass/lightweight-pipeline/tree/master/examples/minimal>`_)

The basic setup is similar to the trivial example with a bit of processing logic added.
We will not go into details here, but focus on the data class that is used to pass data between the steps.


Pipeline_MNE_BIDS_Data
----------------------

The :class:`Pipeline_MNE_BIDS_Data <lw_pipeline.Pipeline_MNE_BIDS_Data>` is essentially a book keeping device to manage
 a dictionary of the form

.. code-block:: python

    {
        "1001": {
            "session1": {
                "task1": {
                    "01": DATA_RUN_1,
                    "02": DATA_RUN_2,
                    # ...
                }
            }
        }
    }

where `DATA_RUN_1`, `DATA_RUN_2`, etc. are paths to the files or data objects.

In many cases we would like to apply the same processing to all (or a certain subset of) runs in the data 
class. This can be achieved using the :func:`apply() <lw_pipeline.Pipeline_MNE_BIDS_Data.apply>` method.

For the sake of example, this is demonstrated below.

.. code-block:: python

    from lw_pipeline import Pipeline_MNE_BIDS_Data, Config

    data = Pipeline_MNE_BIDS_Data(Config())

    data.file_paths = {
        "1001": {
            "session1": {
                "task1": {
                    "1": 5,
                }
            }
        }
    }

    # Define a named function to multiply by 5
    def multiply_by_5(source, x):
        source = source * 5
        return source

    data.apply(multiply_by_5)

    print(str(data))

.. code-block:: text
    :caption: Output

    Step multiplyby5 took 0.00 seconds.
    PipelineData object handling the following files:
    | Subject 1001
    |--- Session session1
    |----- Task task1
    |------- Run 1: 25

A common use case would be to apply a function that is a method in a Pipline_Step subclass.

.. note::

    The second argument :code:`x` in the defined function is provided a BidsPath object that represents a
    possibly generated derivative from the applied function.
    
.. note::

    If the function applied returns an MNE raw object, an MNE epochs object or MNE Annotations the data class
    will attempt to save the object at the proposed BidsPath location.