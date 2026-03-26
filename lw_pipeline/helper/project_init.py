"""Helpers to initialize a minimal runnable LW Pipeline project layout."""

# Authors: The Lightweight Pipeline developers
# SPDX-License-Identifier: BSD-3-Clause

from pathlib import Path

_DEFAULT_STEP = """from lw_pipeline import Pipeline_Step


class A_Start_Step(Pipeline_Step):
    def __init__(self, config):
        super().__init__("Starter step created by lw_pipeline init helper.", config)

    def step(self, data):
        return data
"""

_DEFAULT_DOCS_CONF = """# Configuration file for the Sphinx documentation builder.

import os
import sys

project = "LW Pipeline Project"
copyright = "..."
author = "..."

curdir = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(curdir, "..")))

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
]
autosummary_generate = True

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
"""

_DEFAULT_DOCS_INDEX = """.. Documentation master file

LW Pipeline Project Documentation
=================================

Minimal Sphinx setup for documenting config and step modules.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api
"""

_DEFAULT_DOCS_API = """:orphan:

API Documentation
=================

config
------

.. automodule:: config
   :members:
   :no-inherited-members:

steps
-----

.. automodule:: steps
   :members:
   :inherited-members:
"""


def _build_default_config(
    steps_dir: str,
    data_dir: str | None = None,
    bids_root: str | None = None,
    deriv_root: str | None = None,
) -> str:
    steps_value = Path(steps_dir).as_posix()
    lines = [
        "# LW Pipeline config file",
        "# -----------------------",
        f'steps_dir = "{steps_value}"',
    ]

    if data_dir is not None:
        lines.append(f'data_dir = "{Path(data_dir).as_posix()}"')

    if bids_root is not None:
        lines.append(f'bids_root = "{Path(bids_root).as_posix()}"')

    if deriv_root is not None:
        lines.append(f'deriv_root = "{Path(deriv_root).as_posix()}"')

    lines.extend(
        [
            "",
            "overwrite = False",
            'overwrite_mode = "never"  # Overwrite behavior for output_manager '
            "(always, never, ask, ifnewer)",
            "",
        ]
    )
    return "\n".join(lines)


def scaffold_project(
    project_root,
    config_path="config.py",
    steps_dir="steps",
    data_dir=None,
    bids_root=None,
    deriv_root=None,
    with_docs=False,
    docs_dir="docs",
):
    """Create a minimal runnable LW Pipeline project skeleton.

    Parameters
    ----------
    project_root : str or Path
        Root directory of the project.
    config_path : str, optional
        Config path relative to project root. Default is ``config.py``.
    steps_dir : str, optional
        Steps directory path relative to project root. Default is ``steps``.
    data_dir : str or None, optional
        Data directory to store in ``config.py`` as ``data_dir``.
    bids_root : str or None, optional
        BIDS root to store in ``config.py`` as ``bids_root``.
    deriv_root : str or None, optional
        Derivatives root to store in ``config.py`` as ``deriv_root``.
    with_docs : bool, optional
        Whether to scaffold ``docs/`` with a minimal Sphinx setup.
    docs_dir : str, optional
        Documentation directory path relative to project root. Default is ``docs``.

    Returns
    -------
    dict
        Paths of created files and directories, keyed by kind.
    """
    root = Path(project_root).resolve()
    config_file = root / Path(config_path)
    steps_path = root / Path(steps_dir)
    docs_path = root / Path(docs_dir)
    init_file = steps_path / "__init__.py"
    step_file = steps_path / "00_start.py"
    docs_conf_file = docs_path / "conf.py"
    docs_index_file = docs_path / "index.rst"
    docs_api_file = docs_path / "api.rst"
    docs_templates_dir = docs_path / "_templates"
    docs_static_dir = docs_path / "_static"

    created = {
        "directories": [],
        "files": [],
    }

    if not root.exists():
        root.mkdir(parents=True, exist_ok=True)
        created["directories"].append(str(root))

    if not steps_path.exists():
        steps_path.mkdir(parents=True, exist_ok=True)
        created["directories"].append(str(steps_path))

    if not config_file.parent.exists():
        config_file.parent.mkdir(parents=True, exist_ok=True)
        created["directories"].append(str(config_file.parent))

    if not config_file.exists():
        config_file.write_text(
            _build_default_config(
                steps_dir=steps_dir,
                data_dir=data_dir,
                bids_root=bids_root,
                deriv_root=deriv_root,
            ),
            encoding="utf-8",
        )
        created["files"].append(str(config_file))

    if not init_file.exists():
        init_file.write_text("", encoding="utf-8")
        created["files"].append(str(init_file))

    if not step_file.exists():
        step_file.write_text(_DEFAULT_STEP, encoding="utf-8")
        created["files"].append(str(step_file))

    if with_docs:
        if not docs_path.exists():
            docs_path.mkdir(parents=True, exist_ok=True)
            created["directories"].append(str(docs_path))

        for docs_subdir in (docs_templates_dir, docs_static_dir):
            if not docs_subdir.exists():
                docs_subdir.mkdir(parents=True, exist_ok=True)
                created["directories"].append(str(docs_subdir))

        if not docs_conf_file.exists():
            docs_conf_file.write_text(_DEFAULT_DOCS_CONF, encoding="utf-8")
            created["files"].append(str(docs_conf_file))

        if not docs_index_file.exists():
            docs_index_file.write_text(_DEFAULT_DOCS_INDEX, encoding="utf-8")
            created["files"].append(str(docs_index_file))

        if not docs_api_file.exists():
            docs_api_file.write_text(_DEFAULT_DOCS_API, encoding="utf-8")
            created["files"].append(str(docs_api_file))

    return created
