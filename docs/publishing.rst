=============================
Publishing to the Tool Shed
=============================

The `Galaxy Tool Shed`_ (referred to colloquially in Planemo as the "shed")
can store Galaxy tools, dependency definitions, and workflows among other
Galaxy artifacts. This guide will assume some basic familiarity with the shed
- please review the `Tool Shed Wiki`_ for and introduction.


Configuring a Shed Account
=============================

Before getting started, it is a good idea to have accounts on the Galaxy `test 
<https://testtoolshed.g2.bx.psu.edu/>`__ and (optionally) `main
<https://toolshed.g2.bx.psu.edu/>`__ Tool Sheds. Also, if you haven't initialized a
global Planemo configuration file (``~/.planemo.yml``) this can be done with.

:

    planemo config_init

This will populate a template ``~/.planemo.yml`` file and provide locations to fill
in shed credentials for the test and main Tool Sheds. For each shed, fill in 
either an API ``key`` or an ``email`` and ``password``. Also specify the
``shed_username`` created when registering shed accounts. All these options can be
specified and/or overridden on each planemo command invocation - but that would become
tedious quickly.

Creating a Repository
=============================

Planemo can be used to used to publish "repositories" to the Tool Shed. A
single GitHub repository or locally managed directory of tools may correspond
to any number of Tool Shed repositories. Planemo maps files to Tool Shed
repositories using a special file called ``.shed.yml``.

From a directory containing tools, a `package definition`_. etc... the ``shed_init`` `command <http://planemo.readthedocs.org/en/latest/commands.html#shed-init-command>`__
can be used to bootstrap a new ``.shed.yml`` file.

:

    planemo shed_init --name=<name>
                      --owner=<shed_username>
                      --description=<short description>
                      [--remote_repository_url=<URL to .shed.yml on github>]
                      [--homepage_url=<Homepage for tool.>]
                      [--long_description=<long description>]
                      [--category=<category name>]*

There is not a lot of magic happening here, this file could easily be created
directly with a text editor - but the command has a ``--help`` to assist you
and does some very basic validation.

After reviewing ``.shed.yml``, your ``.shed.yml`` and relevant shed artifacts
can be quickly linted using the following command.

:

    planemo shed_lint --tools

Once the details the ``.shed.yml`` are set and it is time to create the remote
repository and upload artifacts to it - the following two commands can be used
- the first only needs to be run once and creates the repository based the
metadata in ``.shed.yml`` and the second uploads your actual artifacts to it.

:

    planemo shed_create --shed_target test
    planemo shed_upload --shed_target test


Updating a Repository
=============================

Make sure the Galaxy Test Tool Shed is enabled in Galaxy's
``config/tool_sheds_conf.xml`` and try installing and using your repository.

If you make modifications these can be reviewed using:

    planemo shed_diff --shed_target test

    planemo shed_upload --shed_target test

    planemo shed_create --shed_target main
    planemo shed_upload --shed_target main

Advanced Usage
=============================


.. _Galaxy Tool Shed: https://toolshed.g2.bx.psu.edu/
.. _Tool Shed Wiki: https://wiki.galaxyproject.org/ToolShed
.. _package definition: https://wiki.galaxyproject.org/PackageRecipes
testtoolshed.g2.bx.psu.edu