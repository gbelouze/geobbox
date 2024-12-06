# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "GeoBbox"
copyright = "2024, Gabriel Belouze"
author = "Gabriel Belouze"
release = "0.0.4"
version = "0.0.4"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx_rtd_theme",
    "sphinx.ext.napoleon",
]

templates_path = ["_templates"]
exclude_patterns: list[str] = []

# -- Autodoc configuration ---------------------------------------------------
autodoc_default_options = {
    # "ignore-module-all": True  # see https://github.com/sphinx-doc/sphinx/issues/4961#issuecomment-1543858623
    "member-order": "bysource"
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
