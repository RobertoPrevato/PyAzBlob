import sys
import click
import logging
from . import version
from .commands.upload import upload_command
from .logs import get_app_logger


sys.path.append(".")


@click.group()
@click.option(
    "--verbose", default=False, help="Whether to display debug output.", is_flag=True
)
@click.version_option(version=version)
def main(verbose):
    """
    PyAzBlob 🚀 | Azure Blob Service Bulk Uploader.
    Written by Roberto Prevato <roberto.prevato@gmail.com>
    """
    logger = get_app_logger()
    if verbose:
        logger.setLevel(logging.DEBUG)

    logger.debug("Running in --verbose mode")


main.add_command(upload_command)
