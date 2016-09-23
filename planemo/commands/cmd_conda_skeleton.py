"""Module describing the planemo ``conda_skeleton`` command."""
from __future__ import print_function

import click

from planemo import options
from planemo.cli import command_function
from planemo.conda import build_conda_context
from planemo.config import planemo_option


# biocondouctor source: https://github.com/bioconda/bioconda-recipes/tree/master/scripts/bioconductor
# pypi: conda skeleton pypi pyinstrument
# empty: just make a directory?

SOURCE_OPTIONS = {
    "pypi": "TODO",
    "empty": "TODO",
    "biocondouctor": "TODO",
}


@click.command('conda_recipe_init')
@options.conda_skeletontarget_options()
@planemo_option(
    "-c",
    "--channel",
    type=click.STRING,
    default="bioconda",
)
@planemo_option(
    "--channel_path",
    type=click.STRING,
)
@click.argument(
    "source",
    metavar="SOURCE",
    type=click.Choice(["pypi", "empty", "bioconductor"]),
)
@click.argument(
    "recipe",
    metavar="RECIPE",
    type=click.STRING,
)
@command_function
def cli(ctx, source, recipe, channel="bioconda", **kwds):
    """Create the outline for Conda recipe.

    Create Conda recipes from Python packages in PyPI as follows:

        $ planemo conda_recipe_init --no-channel pypi pyinstrument

    Here the --no-channel will cause Planemo to skip cloning a channel and
    placing the recipe within the context of that channel (to ease subsequent
    pull requests of that package).

    To build a recipe and link it into a channel so that a pull request may
    indeed be made with the new package simply don't specify ``--no-channel``
    in the previous command::

        $ planemo conda_recipe_init pypi ephemeris

    By default, this will cause the package to be linked into bioconda, but
    this can be overridden with the ``--channel=<CHANNEL_NAME>`` argument.

    More information on building Conda packages in general can be found at:
    http://conda.pydata.org/docs/building/build.html. Information on best
    practices for bioconda recipes in particular can be found at:
    https://github.com/bioconda/bioconda-recipes/blob/master/GUIDELINES.md.
    """
    conda_context = build_conda_context(ctx, use_planemo_shell_exec=False, **kwds)
    pass
