# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys

sys.path.insert(0, os.path.abspath("../.."))  # point to your package root

project = 'Lizzy'
copyright = '2025-2026, Simone Bancora, Paris Mulye'
author = 'Simone Bancora'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.napoleon',
    'sphinx.ext.autodoc',
    'sphinxcontrib.bibtex',
]


templates_path = ['_templates']
bibtex_bibfiles = ['refs.bib']
html_static_path = ['_static']
html_css_files = ['custom.css']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'


napoleon_google_docstring = False
napoleon_numpy_docstring = True

# autodoc_default_options = {
#     "members": False,
#     "undoc-members": False,
#     "show-inheritance": False,
#     "autosummary": False,
# }
# autodoc_class_attributes = True

latex_engine = 'xelatex'