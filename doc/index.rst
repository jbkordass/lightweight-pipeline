.. Lightweight MNE Pipeline documentation master file

Lightweight Pipeline documentation
==================================

As the name suggests - a lightweight, easy to modify pipeline. Initially built for EEG analysis using MNE python and MNE-BIDS.

Main design criterion is to keep the controller part minimal.


Goals
-----
- Provide a scheme to model concrete pipeline steps after.
- Take care of a configuration file handling and saving/loading to some extend.
- Decouple the content of a pipeline, i.e. its processing logic, from the organizatorial part.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   API<api>
   Use & Examples<use>