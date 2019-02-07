Tools
=====
This section lists all tools, gives a short explanation of their purpose and the command to install and run them locally. If they are part of the buildchain, they will also indicate whether they are voting or not.

All the dependencies for these tools can also be installed by running ``pip install -r requirements-dev.txt``.

It is presupposed that the project code itself is installed locally as described in the README.


pytest
------

(*build chain, voting*)

`pytest`_ runs the unit test suite by searching functions that start with ``test_``, or a few other criteria that we don't use. For details, see `autodetection`_.

Local install:

.. code-block:: bash

  dataclassutils$ pip install pytest
  dataclassutils$ pip install -e .  # treat your project as a package, adding `src` to the code base

Usage:

.. code-block:: bash

  dataclassutils$ pytest


flake8
------

(*build chain, voting*)

`flake8`_ is the linter for this project. We want it to enforce the rules similar to those defined by `hacking`_, minus the parts that we don't like.

Local install:

.. code-block:: bash

  dataclassutils$ pip install pep8-naming flake8 flake8-docstrings flake8-import-order

Usage:

.. code-block:: bash

  dataclassutils$ flake8 src


mypy
----

(*build chain, voting*)

`mypy`_ is an optional static type checker that behaves pretty much like a linter. If you use `PEP 484`_ style type hinting, running mypy regularly is a good idea.

Local install:

.. code-block:: bash

  dataclassutils$ pip install mypy

Usage:

.. code-block:: bash

  dataclassutils$ mypy src/c11h --ignore-missing-imports


coverage
--------

(*build chain, non voting*)

`coverage`_ is our test-coverage reporting tool of choice. It is understood to be read-only, since code coverage is a very weakly defined criterion. Since it runs unit tests to compute coverage, it depends on ``pytest`` as well.

Local install:

.. code-block:: bash

  dataclassutils$ pip install pytest, coverage
  dataclassutils$ pip install -e .  # if you haven't done this for pytest already

Usage:

.. code-block:: bash

  dataclassutils$ coverage erase
  dataclassutils$ coverage run -m pytest &> /dev/null
  dataclassutils$ coverage combine &> /dev/null
  dataclassutils$ coverage report


sphinx
------

(*build chain, non voting*)

`sphinx`_ builds the project's documentation from docstring. It is build as html by default so that it can be easily picked up by serving tools like `readthedocs`_ or `gitlab-pages`_. A different option that might be of interest would be to build with the LaTeX-builder to pdf.

Local install:

.. code-block:: bash

  dataclassutils$ pip install sphinx

Usage:

.. code-block:: bash

  dataclassutils$ sphinx-apidoc -f -o docs src/c11h/dataclassutils
  dataclassutils$ sphinx-build docs build/html
  #  or `sphinx-build doc build/pdf -b latex`

.. _pytest: https://docs.pytest.org/en/latest/
.. _flake8: http://flake8.pycqa.org/en/latest/index.html
.. _mypy: http://mypy-lang.org/
.. _coverage: https://coverage.readthedocs.io/
.. _sphinx: http://www.sphinx-doc.org/en/master/
.. _PEP 484: https://www.python.org/dev/peps/pep-0484/
.. _readthedocs: https://readthedocs.org/
.. _gitlab-pages: https://about.gitlab.com/features/pages/
.. _hacking: https://docs.openstack.org/hacking/latest/user/hacking.html
.. _autodetection: https://docs.pytest.org/en/latest/goodpractices.html#conventions-for-python-test-discovery
