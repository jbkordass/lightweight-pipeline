
Minimal Example
===============

This section provides an overview of a minimal example pipeline setup processing EEG data using the MNE-BIDS package.

It demonstrates

#. More complex pipeline steps.
#. Using the Pipeline_MNE_BIDS_Data class to handle MNE-BIDS data.
#. Running the pipeline (interactively) from a jupyter notebook.
#. Using sphinx doc to document the pipeline steps.

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


Configuration File
------------------

Here is an example of a configuration file that 

.. literalinclude:: ../examples/minimal/config.py
    :language: Python
    :caption: config.py
