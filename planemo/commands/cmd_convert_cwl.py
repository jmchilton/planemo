import sys

import click

from planemo.cli import pass_context
from planemo import options
from planemo import cwl


@click.command('convert_cwl')
@options.required_tool_arg()
@click.option(
    "--draft1",
    "draft",
    flag_value=cwl.DRAFT1,
)
@click.option(
    "--draft2",
    "draft",
    flag_value=cwl.DRAFT2,
)
@pass_context
def cli(ctx, path, draft, **kwds):
    """ Convert a CWL Tool to Galaxy representation. (Experimental).
    """
    stream = sys.stdout
    cwl.convert(ctx, stream, path, draft, **kwds)
