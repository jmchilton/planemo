Dependencies and Conda
===========================================

----------------------------------------------------------------
Finding and Using Existing Conda Packages
----------------------------------------------------------------

.. note:: This document discusses using Conda to satisfy tool dependencies from a tool developer
    perspective. An in depth discussion of using Conda to satisfy dependencies from an
    admistrator's perspective can be found `here <https://docs.galaxyproject.org/en/latest/admin/conda_faq.html>`__.
    That document also serves as good background for this discussion.

While Galaxy can be configured to resolve dependencies various ways, Planemo
is configured with opinionated defaults geared at making building tools that
target Conda_ as easy as possible.

During the introductory tool development tutorial, we called ``planemo tool_init``
with the argument ``--requirement seqtk@1.2`` and the resulting tool contained
the XML::

    <requirements>
        <requirement type="package" version="1.2">seqtk</requirement>
    </requirements>

As configured by Planemo, when Galaxy encounters these ``requirement`` tags it
will attempt to install Conda, check for referenced packages (such as
``seqtk``), and install them as needed for tool testing.

We can check if the requirements on a tool are available in best practice
Conda channels using an extended form of the ``planemo lint`` command. Passing
``--conda_requirements`` flag will ensure all listed requirements are found.

::

    $ planemo lint --conda_requirements seqtk_seq.xml
    Linting tool /Users/john/workspace/planemo/docs/writing/seqtk_seq_v6.xml
      ...
    Applying linter requirements_in_conda... CHECK
    .. INFO: Requirement [seqtk@1.2] matches target in best practice Conda channel [bioconda].


.. note:: You can download the final version of the seqtk from the Planemo tutorial using
    the command::

        $ planemo project_init --template=seqtk_complete seqtk_example
        $ cd seqtk_example

We can verify these tool requirements install with the ``conda_install`` command. With
its default parameters ``conda_install`` processes tools and creates isolated environments
for their declared requirements.

::

    $ planemo conda_install seqtk_seq.xml
      ... TODO ...

Here we can see the underlying application seqtk installed properly in an environment
for this requirement. When we now use ``planemo test`` or ``planemo serve``, it will
reuse this environment.

Here is a portion of the output from the testing command ``planemo test seqtk_seq.xml``
demonstrating using this tool.

TODO

Before a final tool is ready to use however, you can interactively source the Conda
environment that would be created for a tool using the command::

    $ . <(planemo conda_env seqtk_seq.xml)
    Deactivate environment with conda_env_deactivate
    (seqtk_seq) $ which seqtk
    /home/planemo/miniconda2/envs/jobdepsiJClEUfecc6d406196737781ff4456ec60975c137e04884e4f4b05dc68192f7cec4656/bin/seqtk
    (seqtk_seq) $ seqtk seq

    Usage:   seqtk seq [options] <in.fq>|<in.fa>

    Options: -q INT    mask bases with quality lower than INT [0]
             -X INT    mask bases with quality higher than INT [255]
             -n CHAR   masked bases converted to CHAR; 0 for lowercase [0]
             -l INT    number of residues per line; 0 for 2^32-1 [0]
             -Q INT    quality shift: ASCII-INT gives base quality [33]
             -s INT    random seed (effective with -f) [11]
             -f FLOAT  sample FLOAT fraction of sequences [1]
             -M FILE   mask regions in BED or name list FILE [null]
             -L INT    drop sequences with length shorter than INT [0]
             -c        mask complement region (effective with -M)
             -r        reverse complement
             -A        force FASTA output (discard quality)
             -C        drop comments at the header lines
             -N        drop sequences containing ambiguous bases
             -1        output the 2n-1 reads only
             -2        output the 2n reads only
             -V        shift quality by '(-Q) - 33'
             -U        convert all bases to uppercases
             -S        strip of white spaces in sequences
    (seqtk_seq) $ conda_env_deactivate
    $

How did we know what software name and software version to use? We found the existing
packages available for Conda and referenced them. To do this yourself, you can simply
use the planemo command ``conda_search``. If we do a search for ``seqt`` it will show
all the software and all the versions available matching that search term - including
``seqtk``.

::

    $ planemo conda_search seqt
    Fetching package metadata ...............
    seqtk                        r75                           0  bioconda
                                 r82                           0  bioconda
                                 r93                           0  bioconda
                                 1.2                           0  bioconda

.. note:: The Planemo command ``conda_search`` is a light wrapper around the underlying
   ``conda search`` command but configured to use the same channels and other options as
   Planemo and Galaxy. The following Conda command would also work to search::

       $ $HOME/miniconda3/bin/conda -c bioconda -c conda-forge -c iuc seqt

Alternatively the Anaconda_ website can be used to search for packages. Typing ``seqtk``
into the search form on that page and clicking the top result will bring on to `this page
https://anaconda.org/bioconda/seqtk`__ with information about the Bioconda package.

When using the website to search though, you need to aware of what channel you are using. By
default, Planemo and Galaxy will search a few different Conda channels. While it is possible
to configure a local Planemo or Galaxy to target different channels - the current best practice
it to add tools to the existing channels.

The existing channels include:

* Bioconda (`github <https://github.com/bioconda/bioconda-recipes>`__ | `conda <https://anaconda.org/bioconda>`__) - best practice channel for various bioinformatics packages.
* Conda-Forge (`github <https://github.com/conda-forge/staged-recipes>`__ | `conda <https://anaconda.org/conda-forge>`__) - best practice channel for general purpose and widely useful computing packages and libraries.
* iuc (`github <https://github.com/galaxyproject/conda-iuc>`__ | `conda <https://anaconda.org/iuc>`__) - best practice channel for other more Galaxy specific packages.

----------------------------------------------------------------
Building New Conda Packages
----------------------------------------------------------------

At this time, the most relevant source for information on building Conda packages for Galaxy
is probably the Bioconda_ documentation - in particular check out the `contributing documentation
<https://bioconda.github.io/contributing.html>`__.

.. _Bioconda: https://github.com/bioconda/bioconda-recipes
.. _Conda: https://conda.io/docs/
.. _Anaconda: https://anaconda.org/
