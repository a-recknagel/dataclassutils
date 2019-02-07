import os
import sys
sys.path.insert(0, os.path.abspath('../src/c11h'))

from c11h.dataclassutils.settings import VERSION


# -- Project information -----------------------------------------------------
project = 'dataclassutils'
copyright = "2019, Arne Recknagel"
author = 'Arne Recknagel'
version = VERSION
release = VERSION


# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.napoleon',
    'sphinx.ext.autodoc',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.viewcode',
]
templates_path = ['.templates']
source_suffix = '.rst'
master_doc = 'index'
language = None
exclude_patterns = []
pygments_style = 'sphinx'


# -- Options for HTML output -------------------------------------------------
html_theme = 'alabaster'
html_static_path = ['.static']
htmlhelp_basename = 'c11h-dataclassutils-doc'


# -- Options for LaTeX output ------------------------------------------------
latex_documents = [
    (master_doc,
     'c11h-dataclassutils.tex',
     'dataclassutils Documentation',
     'Arne Recknagel',
     'manual'),
]


# -- Options for manual page output ------------------------------------------
man_pages = [
    (master_doc,
     'c11h-dataclassutils',
     'dataclassutils Documentation',
     [author],
     1)
]


# -- Options for Texinfo output ----------------------------------------------
texinfo_documents = [
    (master_doc,
     'c11h-dataclassutils',
     'dataclassutils Documentation',
     author,
     'c11h-dataclassutils',
     'Utility code for dataclasses',
     'Miscellaneous'),
]


# -- Extension configuration -------------------------------------------------
todo_include_todos = True
