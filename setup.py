import sys
from setuptools import find_packages, setup


if sys.version_info < (3, 7):
    raise RuntimeError("This module requires at least Python 3.7.")

try:
    with open('README.rst') as f:
        dsc = f.read()
except (OSError, IOError):
    dsc = "FIXME"

try:
    with open('VERSION') as f:
        VERSION = f.read().strip()
except (OSError, IOError):
    VERSION = '0.0.0'


setup(
    # core
    name='dataclassutils',
    package_dir={'': 'src'},
    packages=[f'c11h.{pkg}' for pkg in find_packages('src/c11h')],
    package_data={'': ['VERSION']},
    entry_points={'console_scripts': ['dataclassutils = c11h.dataclassutils.__main__:main']},

    # metadata
    version=VERSION,
    summary='Utility code for dataclasses',
    long_description=dsc,
    author='Arne Recknagel',
    author_email='arne.recknagel@cognotekt.com',
    license='Not open source',
    python_requires='>=3.7',

)
