# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

sys.path.insert(0, os.path.abspath('../..'))  # Example: up two levels from docs/

# -- Project information -----------------------------------------------------
project = 'TransientBVD'
author = 'Jan Helge Dörsam'
copyright = '2024, Jan Helge Dörsam'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',     # Core Sphinx feature that auto-docs docstrings
    'sphinx.ext.napoleon',    # Support for NumPy/Google style docstrings
    'sphinx.ext.viewcode',    # Add [view code] links
    # 'sphinx.ext.intersphinx', # optionally link to other projects' docs
]

templates_path = ['_templates']
exclude_patterns = []

# Napoleon settings to parse NumPy/Google style docstrings properly
napoleon_google_docstring = True
napoleon_numpy_docstring = True

# Autodoc settings
autodoc_typehints = 'description'  # or 'both', 'none', etc.
autoclass_content = 'both'         # Include __init__ docstrings for classes

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# If you prefer a different theme (e.g. ''), simply install it
# and change html_theme = 'sphinx_rtd_theme' or similar.