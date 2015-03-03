================================
Common Workflow Language Tools
================================

This branch of planemo contains highly experimental support for a subset of
the Draft 1 of the Common Workflow Language (CWL_) specification.

To start playing with this, you must install the ``cwl`` branch of Planemo.

::

    % virtualenv .venv
    % . .venv/bin/activate
    % pip install git+https://github.com/galaxyproject/planemo.git@cwl

Next one can start initialize a quick CWL project to explore these commands
with the command::

    % planemo project_init --template=cwl cwl_test
    % cd cwl_test

This will download the CWL example BWA_ mem tools for `draft 1
<https://github.com/common-workflow-language/common-workflow-language/blob/draft-1/examples/bwa-mem-tool.json>`__
and `draft 2
<https://github.com/common-workflow-language/common-workflow-language/blob/draft-2-pa/examples/draft-2/bwa-mem-tool.json>`__
into the new ``cwl_test`` directory.

Next try converting the draft 1 BWA_ mem tool into a Galaxy tool and launch a
Galaxy instance serving this tool with the commands::

    % planemo convert_cwl --draft1 bwa-mem-tool-v1.json > bwa_mem.xml
    % planemo serve --install_galaxy bwa_mem.xml


.. _CWL: https://github.com/common-workflow-language/common-workflow-language
.. _BWA: http://bio-bwa.sourceforge.net/