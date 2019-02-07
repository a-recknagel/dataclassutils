"""Main Module call code."""
from logging import getLogger
import sys

import click

from c11h.dataclassutils.util.logging_setup import configure_logger

configure_logger()
log = getLogger(__name__)


@click.group()
def main():
    """Click CLI for dataclassutils.

    Chose any of the sub-commands to run executable parts of this package. Each
    of them also contains help-texts that offers information on potential
    parameters.
    """
    log.info(f"Program call arguments: '{sys.argv[1:]}'")


@main.command()
def version():
    """Print dataclassutils's version."""
    log.info("Printing software version")
    from c11h.dataclassutils.settings import VERSION
    print(VERSION)


if __name__ == '__main__':
    main(prog_name='dataclassutils')
