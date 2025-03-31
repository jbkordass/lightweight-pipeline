
Minimal Example
===============

This section provides a detailed explanation of the minimal example pipeline setup. It demonstrates how to configure and run a simple pipeline using `lw_pipeline`.

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

The `config.py` file defines the directories and variables used in the pipeline. For example:

.. literalinclude:: ../examples/minimal/config.py
    :language: Python
    :caption: config.py
