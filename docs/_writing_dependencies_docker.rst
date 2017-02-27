Dependencies and Docker
===========================================

For years Galaxy has supported running tools inside containers. The details
of how to run Galaxy tools inside of containers varies depending on the
Galaxy job runner but details can be found in Galaxy's job_conf.xml sample file.

This document doesn't describe how to run the containers, it describes how Galaxy
figures out which container to run for a given tool. There are currently
two strategies for finding containers for a tool - and they are each
discussed in detail in this document. The newer approach is more experimental
but will ultimately be considered the best practice approach - it is
to allow Galaxy to find or build a BioContainers_ container using ``requirement``
tags that resolve to best-practice Conda channels. The older approach is
to explicitly declare a container identifier in the tool XML. The newer approach
provides superior reproducibility across Galaxy instances because the same
binary Conda packages will automatically be used for both bare metal dependencies
and inside containers.

TODO: Also talk about containers as being very small.

----------------------------------------------------------------
BioContainers_
----------------------------------------------------------------

.. note:: This section is a continuation of :ref:`dependencies_and_conda`,
    please review that section for background information on resolving
    requirements with Conda.

If a tool contains requirements in best practice Conda channels, a
BioContainers_-style container can be found or built for it.

.. note:: As reminder, ``planemo lint --conda_requirements <tool.xml>``
    can be used to check if a tool contains only best-practice ``requirement``
    tags.

TODO: planemo lint --mulled_container

Planemo can be used to build or fetch a BioContainers_ container
with ``planemo mull`` command.

TODO: Talk about how mulled containers are built.

::

    $ planemo mull seqtk_seq.xml
    /home/planemo/.planemo/involucro -v=3 -f /home/planemo/workspace/planemo/.venv/lib/python2.7/site-packages/galaxy_lib-17.5.5.dev0-py2.7.egg/galaxy/tools/deps/mulled/invfile.lua -set CHANNELS='bioconda,conda-forge,r' -set TEST='true' -set TARGETS='seqtk=1.2' -set REPO='quay.io/mulled/seqtk:1.2' -set BINDS='build/dist:/usr/local/' build
    /home/planemo/.planemo/involucro -v=3 -f /home/planemo/workspace/planemo/.venv/lib/python2.7/site-packages/galaxy_lib-17.5.5.dev0-py2.7.egg/galaxy/tools/deps/mulled/invfile.lua -set CHANNELS='bioconda,conda-forge,r' -set TEST='true' -set TARGETS='seqtk=1.2' -set REPO='quay.io/mulled/seqtk:1.2' -set BINDS='build/dist:/usr/local/' build
    [Feb 27 01:03:06] DEBU Run file [/home/planemo/workspace/planemo/.venv/lib/python2.7/site-packages/galaxy_lib-17.5.5.dev0-py2.7.egg/galaxy/tools/deps/mulled/invfile.lua]
    [Feb 27 01:03:06] STEP Run image [continuumio/miniconda:latest] with command [[rm -rf /data/dist]]
    [Feb 27 01:03:06] DEBU Creating container [step-006cbfc472]
    [Feb 27 01:03:06] DEBU Created container [c33a9afea5d3 step-006cbfc472], starting it
    [Feb 27 01:03:07] DEBU Container [c33a9afea5d3 step-006cbfc472] started, waiting for completion
    [Feb 27 01:03:07] DEBU Container [c33a9afea5d3 step-006cbfc472] completed with exit code [0] as expected
    [Feb 27 01:03:07] DEBU Container [c33a9afea5d3 step-006cbfc472] removed
    [Feb 27 01:03:07] STEP Run image [continuumio/miniconda:latest] with command [[/bin/sh -c conda install  -c bioconda -c conda-forge -c r  seqtk=1.2 -p /usr/local --copy --yes --quiet]]
    [Feb 27 01:03:07] DEBU Creating container [step-384ae36228]
    [Feb 27 01:03:07] DEBU Created container [d87bb81fd758 step-384ae36228], starting it
    [Feb 27 01:03:09] DEBU Container [d87bb81fd758 step-384ae36228] started, waiting for completion
    [Feb 27 01:03:14] SOUT Fetching package metadata .............
    [Feb 27 01:03:14] SOUT Solving package specifications: ..........
    [Feb 27 01:03:16] SOUT
    [Feb 27 01:03:16] SOUT Package plan for installation in environment /usr/local:
    [Feb 27 01:03:16] SOUT
    [Feb 27 01:03:16] SOUT The following packages will be downloaded:
    [Feb 27 01:03:16] SOUT
    [Feb 27 01:03:16] SOUT package                    |            build
    [Feb 27 01:03:16] SOUT ---------------------------|-----------------
    [Feb 27 01:03:16] SOUT zlib-1.2.11                |                0          93 KB  conda-forge
    [Feb 27 01:03:16] SOUT seqtk-1.2                  |                0          74 KB  bioconda
    [Feb 27 01:03:16] SOUT ------------------------------------------------------------
    [Feb 27 01:03:16] SOUT Total:         166 KB
    [Feb 27 01:03:16] SOUT
    [Feb 27 01:03:16] SOUT The following NEW packages will be INSTALLED:
    [Feb 27 01:03:16] SOUT
    [Feb 27 01:03:16] SOUT seqtk: 1.2-0    bioconda    (copy)
    [Feb 27 01:03:16] SOUT zlib:  1.2.11-0 conda-forge (copy)
    [Feb 27 01:03:16] SOUT
    [Feb 27 01:03:16] DEBU Container [d87bb81fd758 step-384ae36228] completed with exit code [0] as expected
    [Feb 27 01:03:16] DEBU Container [d87bb81fd758 step-384ae36228] removed
    [Feb 27 01:03:16] STEP Wrap [build/dist] as [quay.io/mulled/seqtk:1.2]
    [Feb 27 01:03:16] DEBU Creating container [step-b84e483abf]
    [Feb 27 01:03:17] DEBU Packing succeeded
    $ docker images
    REPOSITORY               TAG                 IMAGE ID            CREATED             SIZE
    quay.io/mulled/seqtk     1.2                 6c6f00eebfb6        21 seconds ago      7.34 MB
    <none>                   <none>              acbe0d78afdf        38 seconds ago      7.34 MB
    continuumio/miniconda    latest              6965a4889098        3 weeks ago         437 MB
    bgruening/busybox-bash   0.1                 3d974f51245c        9 months ago        6.73 MB
    $ planemo test --mulled_containers seqtk_seq.xml

TODO: Verify test output.

TODO: Exercise ... test the pear tool.

TODO: Build on options for local packages.

TODO: Show fleeqtk example from earlier working locally.

----------------------------------------------------------------
Explicit Annotation
----------------------------------------------------------------

TODO: This completely...

.. BioContainers_: http://biocontainers.pro/
