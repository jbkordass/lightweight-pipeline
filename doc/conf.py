# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Lightweight Pipeline'
copyright = '2025, The Lightweight Pipeline developers'
author = 'The Lightweight Pipeline developers'



import lw_pipeline  # noqa: E402

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',  # Core library for html generation from docstrings
    'sphinx.ext.autosummary',  # Create neat summary tables
    "sphinx.ext.githubpages",
    "sphinx.ext.napoleon",  # Support for numpy and google style docstrings
    "sphinx.ext.viewcode",  # Add links to the source code
    # 'sphinx_gallery.gen_gallery',
]
autosummary_generate = True  # Turn on sphinx.ext.autosummary

templates_path = ['_templates']
exclude_patterns = ["auto_examples/index.rst", "_build", "Thumbs.db", ".DS_Store"]

# Settings for sphinx gallery
# sphinx_gallery_conf = {
#     "doc_module": "lw_pipeline",
#     "examples_dirs": "../examples",
#     "gallery_dirs": "auto_examples",
#     "reference_url": {
#         "lw_pipeline": None,
#     },
#     "backreferences_dir": "generated",
# }

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'pydata_sphinx_theme'
html_static_path = ['_static']

html_theme_options = {
    "icon_links": [
        dict(
            name="GitHub",
            url="https://github.com/rectified-evasion/lightweight-pipeline",
            icon="fab fa-github-square",
        ),
    ],
    "icon_links_label": "Quick Links",  # for screen reader
    "use_edit_page_button": False,
    "navigation_with_keys": False,
    "show_toc_level": 1,
    "header_links_before_dropdown": 6,
}
