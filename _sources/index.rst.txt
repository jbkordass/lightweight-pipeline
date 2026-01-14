.. Lightweight MNE Pipeline documentation master file

Lightweight Pipeline documentation
==================================

As the name suggests - a lightweight, easy to modify pipeline. Initially built for EEG analysis using `MNE-Python <https://mne.tools>`_ and `MNE-BIDS <https://mne.tools/mne-bids/>`_.

Main design criterion is to keep the controller part minimal.


Goals
-----
- Provide a scheme to model concrete pipeline steps after.
- Take care of a configuration file handling and saving/loading to some extend.
- Decouple the content of a pipeline, i.e. its processing logic, from the organisatorial part.


.. toctree::
   :maxdepth: 2
   :caption: Contents:
   :hidden:

   API<api>
   Use & Examples<use>
   Output Management<output_management>