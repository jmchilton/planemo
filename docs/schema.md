# Galaxy Tool XML File

The XML File for a Galaxy tool, generally referred to as the "tool config
file" or "wrapper", serves a number of purposes. First, it lays out the user
interface for the tool ( e.g. form fields, text, help, etc...). Second, it
provides the glue that links your tool to Galaxy by telling Galaxy how to
invoke it, what options to pass, and what files it will produce as output.

This document serves as reference documentation. If you would like to learn
how to build tools for Galaxy,
[Planemo](http://planemo.readthedocs.io/en/latest/writing.html) features a
number of tutorials on building Galaxy tools that would better serve that purpose.

[``<tool>``](#tool)  
├──[``<description>``](#tool|description)  
├──[``<version_command>``](#tool|version_command)  
├──[``<command>``](#tool|command)  
├──[``<inputs>``](#tool|inputs)  
├──┼──[``<section>``](#tool|inputs|section)  
├──┼──[``<repeat>``](#tool|inputs|repeat)  
├──┼──[``<conditional>``](#tool|inputs|conditional)  
├──┼──┴──[``<when>``](#tool|inputs|conditional|when)  
├──┼──[``<param>``](#tool|inputs|param)  
├──┼──┼──[``<validator>``](#tool|inputs|param|validator)  
├──┼──┼──[``<option>``](#tool|inputs|param|option)  
├──┼──┼──[``<options>``](#tool|inputs|param|options)  
├──┼──┼──┼──[``<column>``](#tool|inputs|param|options|column)  
├──┼──┼──┴──[``<filter>``](#tool|inputs|param|options|filter)  
├──┼──┼──[``<sanitizer>``](#tool|inputs|param|sanitizer)  
├──┼──┼──┼──[``<valid>``](#tool|inputs|param|sanitizer|valid)  
├──┼──┼──┼──┼──[``<add>``](#tool|inputs|param|sanitizer|valid|add)  
├──┼──┼──┼──┴──[``<remove>``](#tool|inputs|param|sanitizer|valid|remove)  
├──┼──┼──┼──[``<mapping>``](#tool|inputs|param|sanitizer|mapping)  
├──┼──┼──┼──┼──[``<add>``](#tool|inputs|param|sanitizer|mapping|add)  
├──┴──┴──┴──┴──[``<remove>``](#tool|inputs|param|sanitizer|mapping|remove)  
├──[``<configfiles>``](#tool|configfiles)  
├──┼──[``<configfile>``](#tool|configfiles|configfile)  
├──┴──[``<inputs>``](#tool|configfiles|inputs)  
├──[``<environment_variables>``](#tool|environment_variables)  
├──┴──[``<environment_variable>``](#tool|environment_variables|environment_variable)  
├──[``<outputs>``](#tool|outputs)  
├──┼──[``<data>``](#tool|outputs|data)  
├──┼──┼──[``<filter>``](#tool|outputs|data|filter)  
├──┼──┼──[``<change_format>``](#tool|outputs|data|change_format)  
├──┼──┼──┴──[``<when>``](#tool|outputs|data|change_format|when)  
├──┼──┼──[``<actions>``](#tool|outputs|data|actions)  
├──┼──┼──┼──[``<conditional>``](#tool|outputs|data|actions|conditional)  
├──┼──┼──┼──┴──[``<when>``](#tool|outputs|data|actions|conditional|when)  
├──┼──┼──┴──[``<action>``](#tool|outputs|data|actions|action)  
├──┼──┴──[``<discover_datasets>``](#tool|outputs|data|discover_datasets)  
├──┼──[``<collection>``](#tool|outputs|collection)  
├──┼──┼──[``<filter>``](#tool|outputs|collection|filter)  
├──┴──┴──[``<discover_datasets>``](#tool|outputs|collection|discover_datasets)  
├──[``<tests>``](#tool|tests)  
├──┼──[``<test>``](#tool|tests|test)  
├──┼──┼──[``<param>``](#tool|tests|test|param)  
├──┼──┼──[``<repeat>``](#tool|tests|test|repeat)  
├──┼──┼──[``<section>``](#tool|tests|test|section)  
├──┼──┼──[``<conditional>``](#tool|tests|test|conditional)  
├──┼──┼──[``<output>``](#tool|tests|test|output)  
├──┼──┼──┼──[``<discover_dataset>``](#tool|tests|test|output|discover_dataset)  
├──┼──┼──┼──[``<metadata>``](#tool|tests|test|output|metadata)  
├──┼──┼──┴──[``<assert_contents>``](#tool|tests|test|output|assert_contents)  
├──┼──┼──[``<output_collection>``](#tool|tests|test|output_collection)  
├──┼──┼──[``<assert_command>``](#tool|tests|test|assert_command)  
├──┼──┼──[``<assert_stdout>``](#tool|tests|test|assert_stdout)  
├──┴──┴──[``<assert_stderr>``](#tool|tests|test|assert_stderr)  
├──[``<code>``](#tool|code)  
├──[``<requirements>``](#tool|requirements)  
├──┼──[``<requirement>``](#tool|requirements|requirement)  
├──┴──[``<container>``](#tool|requirements|container)  
├──[``<stdio>``](#tool|stdio)  
├──┼──[``<exit_code>``](#tool|stdio|exit_code)  
├──┴──[``<regex>``](#tool|stdio|regex)  
├──[``<help>``](#tool|help)  
├──[``<citations>``](#tool|citations)  
└──┴──[``<citation>``](#tool|citations|citation)  


<a name="tool"></a>
## ``tool``

The outer-most tag set of tool XML files. Attributes on this tag apply to the
tool as a whole.

### Examples

A normal tool:

```xml
<tool id="seqtk_seq"
      name="Convert FASTQ to FASTA"
      version="1.0.0"
      profile="16.04"
>
```

A ``data_source`` tool contains a few more relevant attributes.

```xml
<tool id="ucsc_table_direct1"
      name="UCSC Main"
      version="1.0.0"
      hidden="false"
      profile="16.01"
      tool_type="data_source"
      URL_method="post">
```
      

### Best Practices

Find the Intergalactic Utilities Commision suggested best practices for this
element [here](http://planemo.readthedocs.io/en/latest/standards/docs/best_practices/tool_xml.html#tools).


### Attributes
Attribute | Details | Required
--- | --- | ---
``id`` | Must be unique across all tools; should be lowercase and contain only letters, numbers, and underscores. It allows for tool versioning and metrics of the number of times a tool is used, among other things. Find the Intergalactic Utilities Commision suggested best practices for this element [here](http://planemo.readthedocs.io/en/latest/standards/docs/best_practices/tool_xml.html#tool-ids). | True
``name`` | This string is what is displayed as a hyperlink in the tool menu. Find the Intergalactic Utilities Commision suggested best practices for this element [here](http://planemo.readthedocs.io/en/latest/standards/docs/best_practices/tool_xml.html#tool-names). | True
``version`` | This string defaults to ``1.0.0`` if it is not included in the tag. It allows for tool versioning and should be increased with each new version of the tool. Find the Intergalactic Utilities Commision suggested best practices for this element [here](http://planemo.readthedocs.io/en/latest/standards/docs/best_practices/tool_xml.html#tool-versions). | False
``hidden`` | Allows for tools to be loaded upon server startup, but not displayed in the tool menu. This attribute should be applied in the toolbox configuration instead and so should be considered deprecated. | False
``display_interface`` | Disable the display the tool's graphical tool form by setting this to ``false``. | False
``tool_type`` | Allows for certain framework functionality to be performed on certain types of tools. Normal tools that execute typical command-line jobs do not need to specify this, special kinds of tools such as [Data Source](https://wiki.galaxyproject.org/Admin/Internals/DataSources) and [Data Manager](https://wiki.galaxyproject.org/Admin/Tools/DataManagers) tools should set this to have values such as ``data_source`` or ``manage_data``. | False
``profile`` | This string specified the minimum Galaxy version that should be required to run this tool. Certain legacy behaviors such as using standard error content to detect errors instead of exit code are disabled automatically if profile is set to any version newer than ``16.01``, such as ``16.04``. | False
``workflow_compatible`` | This attribute indicates if this tool is usable within a workflow (defaults to ``true`` for normal tools and ``false`` for data sources). | False
``URL_method`` | Only used if ``tool_type`` attribute value is ``data_source`` - this attribute defines the HTTP request method to use when communicating with an external data source application (the default is ``get``). | False




<a name="tool|description"></a>
## ``tool`` > ``description``
The value is displayed in
the tool menu immediately following the hyperlink for the tool (based on the
``name`` attribute of the ``<tool>`` tag set described above).

### Example

```xml
<description>table browser</description>
```


### Best Practices

Find the Intergalactic Utilities Commision suggested best practices for this
element [here](http://planemo.readthedocs.io/en/latest/standards/docs/best_practices/tool_xml.html#tool-descriptions).





<a name="tool|version_command"></a>
## ``tool`` > ``version_command``
Specifies the command to be run in
order to get the tool's version string. The resulting value will be found in the
"Info" field of the history dataset.

Unlike the [``command``](#tool|command) tag, this value is taken as a literal and so there is no
need to escape values like ``$`` and command inputs are not available for variable
substitution.

### Example

```xml
<version_command>tophat -version</version_command>
```






<a name="tool|command"></a>
## ``tool`` > ``command``

This tag specifies how Galaxy should invoke the tool's executable, passing its
required input parameter values (the command line specification links the
parameters supplied in the form with the actual tool executable). Any word
inside it starting with a dollar sign (``$``) will be treated as a variable whose
values can be acquired from one of three sources: parameters, metadata, or
output files. After the substitution of variables with their values, the content
is interpreted with [Cheetah](http://www.cheetahtemplate.org/) and finally given
to the interpreter specified in the corresponding attribute (if any).

### Examples

The following uses a compiled executable ([bedtools](http://bedtools.readthedocs.io/en/latest/)).

```xml
<command>bed12ToBed6 -i '$input' > '$output'</command>
```

A few things to note about even this simple example:

* Input and output variables (boringly named ``input`` and ``output``)
  are expanded into paths using the ``$`` Cheetah directive.
* Paths should be quoted so that the Galaxy database files may contain spaces.
* We are building up a shell script - so special characters like ``>`` can be used
  (in this case the standard output of the bedtools call is written to the path
  specified by ``'$output'``).

The bed12ToBed6 tool can be found [here](https://github.com/galaxyproject/tools-iuc/blob/master/tools/bedtools/bed12ToBed6.xml).

A more sophisticated bedtools example demonstrates the use of loops, conditionals,
and uses whitespace to make a complex command very readable can be found in
[annotateBed](https://github.com/galaxyproject/tools-iuc/blob/master/tools/bedtools/annotateBed.xml)
tool.

```xml
<command><![CDATA[
bedtools annotate
        -i "${inputA}"
        #if $names.names_select == 'yes':
            -files
            #for $bed in $names.beds:
                '${bed.input}'
            #end for
            -names
            #for $bed in $names.beds:
                '${bed.inputName}'
            #end for
        #else:
            #set files = '" "'.join( [ str( $file ) for $file in $names.beds ] )
            -files '${files}'
            #set names = '" "'.join( [ str( $name.display_name ) for $name in $names.beds ] )
            -names '${names}'
        #end if
        $strand
        $counts
        $both
        > "${output}"
]]></command>
```

The following example (taken from [xpath](https://github.com/galaxyproject/tools-iuc/blob/master/tools/xpath/xpath.xml) tool)
uses an interpreted executable. In this case a Perl script is shipped with the
tool and the directory of the tool itself is referenced with ``$__tool_directory__``.

```xml
<command>
  perl $__tool_directory__/xpath -q -e '$expression' '$input' > '$output'
</command>
```

The following example demonstrates accessing metadata from datasets. Metadata values
(e.g., ``${input.metadata.chromCol}``) are acquired from the ``Metadata`` model associated
with the objects selected as the values of each of the relative form field
parameters in the tool form. Accessing this information is generally enabled using
the following feature components.

A set of "metadata information" is defined for each supported data type (see the
``MetadataElement`` objects in the various data types classes in
[``/lib/galaxy/datatypes``](https://github.com/galaxyproject/galaxy/tree/dev/lib/galaxy/datatypes).
The ``DatasetFilenameWrapper`` class in the
[/lib/galaxy/tools/wrappers.py](https://github.com/galaxyproject/galaxy/blob/dev/lib/galaxy/tools/wrappers.py)
code file wraps a metadata collection to return metadata parameters wrapped
according to the Metadata spec.

```xml
        #set genome = $input.metadata.dbkey
        #set datatype = $input.datatype
        mkdir -p output_dir &&
        python $__tool_directory__/extract_genomic_dna.py
        --input '$input'
        --genome '$genome'
        #if $input.is_of_type("gff"):
            --input_format "gff"
            --columns "1,4,5,7"
            --interpret_features $interpret_features
        #else:
            --input_format "interval"
            --columns "${input.metadata.chromCol},${input.metadata.startCol},${input.metadata.endCol},${input.metadata.strandCol},${input.metadata.nameCol}"
        #end if
        --reference_genome_source $reference_genome_cond.reference_genome_source
        #if str($reference_genome_cond.reference_genome_source) == "cached"
            --reference_genome $reference_genome_cond.reference_genome.fields.path
        #else:
            --reference_genome $reference_genome_cond.reference_genome
        #end if
        --output_format $output_format_cond.output_format
        #if str($output_format_cond.output_format) == "fasta":
            --fasta_header_type $output_format_cond.fasta_header_type_cond.fasta_header_type
            #if str($output_format_cond.fasta_header_type_cond.fasta_header_type) == "char_delimited":
                --fasta_header_delimiter $output_format_cond.fasta_header_type_cond.fasta_header_delimiter
            #end if
        #end if
        --output '$output'
```

In additon to demonstrating accessing metadata, this example demonstrates:

* ``$input.is_of_type("gff")`` which can be used to check if an input is of a
  given datatype.
* ``#set datatype = $input.datatype`` which is the syntax for defining variables
  in Cheetah.

<a name="cheetah_reserved_variables"></a>

### Reserved Variables

Galaxy provides a few pre-defined variables which can be used in your command line,
even though they don't appear in your tool's parameters.

Name | Description
---- | -----------
``$__tool_directory__`` | The directory the tool description (XML file) currently resides in (new in 15.03)
``$__new_file_path__`` | ``config/galaxy.ini``'s ``new_file_path`` value
``$__tool_data_path__`` | ``config/galaxy.ini``'s tool_data_path value
``$__root_dir__`` | Top-level Galaxy source directory made absolute via ``os.path.abspath()``
``$__datatypes_config__`` | ``config/galaxy.ini``'s datatypes_config value
``$__user_id__`` | Email's numeric ID (id column of ``galaxy_user`` table in the database)
``$__user_email__`` | User's email address
``$__app__`` | The ``galaxy.app.UniverseApplication`` instance, gives access to all other configuration file variables (e.g. $__app__.config.output_size_limit). Should be used as a last resort, may go away in future releases.

Additional runtime properties are available as environment variables. Since these
are not Cheetah variables (the values aren't available until runtime) these should likely
be escaped with a backslash (``\``) when appearing in ``command`` or ``configfile`` elements.

Name | Description
---- | -----------
``\${GALAXY_SLOTS:-4}`` | Number of cores/threads allocated by the job runner or resource manager to the tool for the given job (here 4 is the default number of threads to use if running via custom runner that does not configure GALAXY_SLOTS or in an older Galaxy runtime).

See the [Planemo docs](http://planemo.readthedocs.io/en/latest/writing_advanced.html#cluster-usage)
on the topic of ``GALAXY_SLOTS`` for more information and examples.

### Attributes

#### ``detect_errors``

If present on the ``command`` tag, this attribute can be one of:

* ``default`` no-op fallback to ``stdio`` tags and erroring on standard error output (for legacy tools).
* ``exit_code`` error if tool exit code is not 0. (The @jmchilton recommendation).
* ``aggressive`` error if tool exit code is not 0 or either ``Exception:`` or ``Error:``
  appears in standard error/output. (The @bgruening recommendation).

For newer tools with ``profile>=16.04``, the default behavior is ``exit_code``.
Legacy tools default to ``default`` behavior described above (erroring if the tool
produces any standard error output).

See [PR 117](https://github.com/galaxyproject/galaxy/pull/117) for more implementation
information and discussion on the ``detect_errors`` attribute.

#### ``strict``

This boolean forces the ``#set -e`` directive on in shell scripts - so that in a
multi-part command if any part fails the job exits with a non-zero exit code.
This is enabled by default for tools with ``profile>=16.04`` and disabled on
legacy tools.

#### ``interpreter``

Older tools may define an ``intepreter`` attribute on the command, but this is
deprecated and using the ``$__tool_directory__`` variable is superior.



### Best Practices

Find the Intergalactic Utilities Commision suggested best practices for this
element [here](http://planemo.readthedocs.io/en/latest/standards/docs/best_practices/tool_xml.html#command-tag).





<a name="tool|inputs"></a>
## ``tool`` > ``inputs``
Consists of all tag sets that define the
tool's input parameters. Each ``<param>`` tag within the ``<inputs>`` tag set
maps to a command line parameter within the [``command``](#tool|command) tag. Most
tools will not need to specify any attributes on this tag itself.



### Attributes
Attribute | Details | Required
--- | --- | ---
``action`` | URL used by data source tools. | False
``check_values`` | Set to ``false`` to disable parameter checking in data source tools. | False
``method`` | Data source HTTP action (e.g. ``get`` or ``put``) to use. | False
``target`` | UI link target to use for data source tools (e.g. ``_top``). | False
``nginx_upload`` | This boolean indicates if this is an upload tool or not. | False




<a name="tool|inputs|section"></a>
## ``tool`` > ``inputs`` > ``section``

This tag is used to group parameters into sections of the interface. Sections
are implemented to replace the commonly used tactic of hiding advanced options
behind a conditional, with sections you can easily visually group a related set
of options.

### Example

The XML configuration is relatively trivial for sections:

```xml
<inputs>
    <section name="adv" title="Advanced Options" expanded="False">
        <param name="plot_color" type="color" label="Track color" />
    </section>
</inputs>
```

In your command template, you'll need to include the section name to access the
variable:

```
--color $adv.plot_color
```

Further examples can be found in the [test case](https://github.com/galaxyproject/galaxy/blob/master/test/functional/tools/section.xml) from [PR #35](https://github.com/galaxyproject/galaxy/pull/35)



### Attributes
Attribute | Details | Required
--- | --- | ---
``name`` | The internal key used for the section. | True
``title`` | Human readable label for the section. | True
``expanded`` | Whether the section should be expanded by default or not. If not, the default set values are used. | False




<a name="tool|inputs|repeat"></a>
## ``tool`` > ``inputs`` > ``repeat``

See
[xy_plot.xml](https://github.com/galaxyproject/tools-devteam/blob/master/tools/xy_plot/xy_plot.xml)
for an example of how to use this tag set. This is a container for any tag sets
that can be contained within the ``<inputs>`` tag set. When this is used, the
tool will allow the user to add any number of additional sets of the contained
parameters (an option to add new iterations will be displayed on the tool form).
All input parameters contained within the ``<repeat>`` tag can be retrieved by
enumerating over ``$<name_of_repeat_tag_set>`` in the relevant Cheetah code.
This returns the rank and the parameter objects of the repeat container. See the
Cheetah code below.

### Example

This part is contained in the ``<inputs>`` tag set.

```xml
<repeat name="series" title="Series">
    <param name="input" type="data" format="tabular" label="Dataset"/>
    <param name="xcol" type="data_column" data_ref="input" label="Column for x axis"/>
    <param name="ycol" type="data_column" data_ref="input" label="Column for y axis"/>
</repeat>
```

This Cheetah code can be used in the ``<command>`` tag set or the
``<configfile>`` tag set.

```xml
#for $i, $s in enumerate( $series )
    rank_of_series=$i
    input_path='${s.input}'
    x_colom=${s.xcol}
    y_colom=${s.ycol}
#end for
```

### Testing

This is an example test case with multiple repeat elements for the example above.

```xml
<test>
    <repeat name="series">
        <param name="input" value="tabular1.tsv" ftype="tabular"/>
        <param name="xcol" value="1"/>
        <param name="ycol" value="2"/>
    </repeat>
    <repeat name="series">
        <param name="input" value="tabular2.tsv" ftype="tabular"/>
        <param name="xcol" value="4"/>
        <param name="ycol" value="2"/>
    </repeat>
    <output name="out_file1" file="cool.pdf" ftype="pdf" />
</test>
```

See the documentation on the [``repeat`` test directive](#tool|tests|test|repeat).

An older way to specify repeats in a test is by instances that are created by referring to names with a special format: "<repeat name>_<repeat index>|<param name>"

```xml
<test>
    <param name="series_0|input" value="tabular1.tsv" ftype="tabular"/>
    <param name="series_0|xcol" value="1"/>
    <param name="series_0|ycol" value="2"/>
    <param name="series_1|input" value="tabular2.tsv" ftype="tabular"/>
    <param name="series_1|xcol" value="4"/>
    <param name="series_1|ycol" value="2"/>
    <output name="out_file1" file="cool.pdf" ftype="pdf" />
</test>
```

The test tool [disambiguate_repeats.xml](https://github.com/galaxyproject/galaxy/blob/dev/test/functional/tools/disambiguate_repeats.xml)
demonstrates both testing strategies.




### Attributes
Attribute | Details | Required
--- | --- | ---
``name`` | Name for this element | False
``title`` | The title of the repeat section, which will be displayed on the tool form. | True
``min`` | The minimum number of repeat units. | False
``max`` | The maximum number of repeat units. | False
``default`` | The default number of repeat units. | False
``help`` | Short help description for repeat element. | False




<a name="tool|inputs|conditional"></a>
## ``tool`` > ``inputs`` > ``conditional``


This is a container for conditional parameters in the tool (must contain 'when'
tag sets) - the command line (or portions thereof) are then wrapped in an if-else
statement. A good example tool that demonstrates many conditional parameters is
[biom_convert.xml](https://github.com/galaxyproject/tools-iuc/blob/master/tools/biom_format/biom_convert.xml).

```xml
<conditional name="input_type">
    <param name="input_type_selector" type="select" label="Choose the source BIOM format">
        <option value="tsv" selected="True">Tabular File</option>
        <option value="biom">BIOM File</option>
    </param>
    <when value="tsv">
        <param name="input_table" type="data" format="tabular" label="Tabular File" argument="--input-fp"/>
        <param name="process_obs_metadata" type="select" label="Process metadata associated with observations when converting" argument="--process-obs-metadata">
            <option value="" selected="True">Do Not process metadata</option>
            <option value="taxonomy">taxonomy</option>
            <option value="naive">naive</option>
            <option value="sc_separated">sc_separated</option>
        </param>
    </when>
    <when value="biom">
        <param name="input_table" type="data" format="biom1" label="Tabular File" argument="--input-fp"/>
    </when>
</conditional>
```

The first directive following the conditional is a [``param``](#tool|inputs|param),
this param must be of type ``select`` or ``boolean``. Depending on the value a
user selects for this "test" parameter - different UI elements will be shown.
These different paths are described by the following the ``when`` blocks shown
above.

The following Cheetah block demonstrates the use of the ``conditional``
shown above:

```
biom convert -i "${input_type.input_table}" -o "${output_table}"
#if str( $input_type.input_type_selector ) == "tsv":
    #if $input_type.process_obs_metadata:
        --process-obs-metadata "${input_type.process_obs_metadata}"
    #end if
#end if
```

Notice that the parameter ``input_table`` appears down both ``when`` clauses
so ``${input_type.input_table}`` appears unconditionally but we need to
conditionally reference ``${input_type.process_obs_metadata}`` with a Cheetah
``if`` statement.

A common use of the conditional wrapper is to select between reference data
managed by the Galaxy admins (for instance via
[data managers](https://wiki.galaxyproject.org/Admin/Tools/DataManagers)
) and
history files. A good example tool that demonstrates this is
the [Bowtie 2](https://github.com/galaxyproject/tools-devteam/blob/master/tools/bowtie2/bowtie2_wrapper.xml) wrapper.

```xml
<conditional name="reference_genome">
  <param name="source" type="select" label="Will you select a reference genome from your history or use a built-in index?" help="Built-ins were indexed using default options. See `Indexes` section of help below">
    <option value="indexed">Use a built-in genome index</option>
    <option value="history">Use a genome from the history and build index</option>
  </param>
  <when value="indexed">
    <param name="index" type="select" label="Select reference genome" help="If your genome of interest is not listed, contact the Galaxy team">
      <options from_data_table="bowtie2_indexes">
        <filter type="sort_by" column="2"/>
        <validator type="no_options" message="No indexes are available for the selected input dataset"/>
      </options>
    </param>
  </when>
  <when value="history">
    <param name="own_file" type="data" format="fasta" metadata_name="dbkey" label="Select reference genome" />
  </when>
</conditional>
```

The Bowtie 2 wrapper also demonstrates other conditional paths - such as choosing
between paired inputs of single stranded inputs.



### Attributes
Attribute | Details | Required
--- | --- | ---
``name`` | Name for this element | False
``value_from`` | Infrequently used option to dynamically access Galaxy internals, this should be avoided.  Galaxy method to execute. | False
``value_ref`` | Infrequently used option to dynamically access Galaxy internals, this should be avoided.  Referenced parameter to pass method. | False
``value_ref_in_group`` | Infrequently used option to dynamically access Galaxy internals, this should be avoided.  Is referenced parameter is the same group. | False
``label`` | Human readable description for the conditional, unused in the Galaxy UI currently. | False




<a name="tool|inputs|conditional|when"></a>
## ``tool`` > ``inputs`` > ``conditional`` > ``when``
This directive describes one potential
set of input for the tool at this depth. See documentation for the
[``conditional``](#tool|inputs|conditional) block for more details and examples (XML
and corresponding Cheetah conditionals).


### Attributes
Attribute | Details | Required
--- | --- | ---
``value`` | Value for the tool form test parameter corresponding to this ``when`` block. | True




<a name="tool|inputs|param"></a>
## ``tool`` > ``inputs`` > ``param``


Contained within the ``<inputs>`` tag set - each of these specifies a field that
will be displayed on the tool form. Ultimately, the values of these form fields
will be passed as the command line parameters to the tool's executable.

### Common Attributes

The attributes valid for this tag vary wildly based on the ``type`` of the
parameter being described. All the attributes for the ``param`` element are
documented below for completeness, but here are the common ones for each
type are as follows:




### Attributes
Attribute | Details | Required
--- | --- | ---
``type`` | Describes the parameter type - each different type as different semantics and the tool form widget is different. Currently valid parameter types are: ``text``,  ``integer``,  ``float``,  ``boolean``,  ``genomebuild``,  ``select``, ``color``,  ``data_column``,  ``hidden``,  ``hidden_data``,  ``baseurl``, ``file``,  ``ftpfile``,  ``data``,  ``data_collection``,  ``library_data``, ``drill_down``. The definition of supported parameter types as defined in the ``parameter_types`` dictionary in [/lib/galaxy/tools/parameters/basic.py](https://github.com/galaxyproject/galaxy/blob/master/lib/galaxy/tools/parameters/basic.py). | True
``name`` | Name for this element. This ``name`` is used as the Cheetah variable containing the user-supplied parameter name in ``command`` and ``configfile`` elements. The name should not contain pipes or periods (e.g. ``.``). Some "reserved" names are ``REDIRECT_URL``, ``DATA_URL``, ``GALAXY_URL``. | False
``argument`` | If the parameter reflects just one command line argument of a certain tool, this tag should be set to that particular argument. It is rendered in parenthesis after the help section, and it will create the name attribute from the argument attribute by stripping the dashes (e.g. if ``argument="--sensitive"`` then ``name="sensitive"`` is implicit). | False
``label`` | The attribute value will be displayed on the tool page as the label of the form field (``label="Sort Query"``). | False
``help`` | Short bit of text, rendered on the tool form just below the associated field to provide information about the field. Find the Intergalactic Utilities Commision suggested best practices for this element [here](http://planemo.readthedocs.io/en/latest/standards/docs/best_practices/tool_xml.html#parameter-help). | False
``optional`` | If ``false``, parameter must have a value. Defaults to "false". | False


### Parameter Types

#### ``text``

When ``type="text"``, the parameter is free form text and appears as a text box
in the tool form.




### Attributes
Attribute | Details | Required
--- | --- | ---
``area`` | Boolean indicating if this should be rendered as a one line text box (if ``false``) or a multi-line text area (if ``true``). | False
``value`` | The default value for this parameter. | False
``size`` | Used only if ``type`` attribute value is ``text``. To create a multi-line text box add an ``area="True"`` attribute to the param tag. This can be one dimensional (e.g. ``size="40"``) or two dimensional (e.g. ``size="5x25"``). | False


##### Examples

Sometimes you need labels for data or graph axes, chart titles, etc. This can be
done using a text field. The following will create a text box 30 characters wide
with the default value of "V1".

```xml
<param name="xlab" size="30" type="text" value="V1" label="Label for x axis"/>
```

The ``size`` parameter can be two dimensional, if it is the textbox will be
rendered on the tool form as a text area instead of a single line text box.

```xml
<param name="foo" type="text" area="True" size="5x25" />
```

#### ``integer`` and ``float``

These parameters represent whole number and real numbers, respectively.




### Attributes
Attribute | Details | Required
--- | --- | ---
``value`` | The default value for this parameter. | False
``min`` | Minimum valid parameter value - only valid when ``type`` is ``integer`` or ``float``. | False
``max`` | Maximum valid parameter value - only valid when ``type`` is ``integer`` or ``float``. | False


##### Example

```
<param name="region_size" size="4" type="integer" value="1" label="flanking regions of size" />
```

#### ``boolean``

This represents a binary true or false value.




### Attributes
Attribute | Details | Required
--- | --- | ---
``checked`` | Set to ``true`` if the ``boolean`` parameter should be checked (or ``true``) by default. | False
``truevalue`` | The parameter value in the Cheetah template if the parameter is ``true`` or checked by the user. Only valid if ``type`` is ``boolean``. | False
``falsevalue`` | The parameter value in the Cheetah template if the parameter is ``false`` or not checked by the user. Only valid if ``type`` is ``boolean``. | False


#### ``data``

A dataset from the current history. Multiple types might be used for the param form.

##### Examples

The following will find all "coordinate interval files" contained within the
current history and dynamically populate a select list with them. If they are
selected, their destination and internal file name will be passed to the
appropriate command line variable.

```xml
<param name="interval_file" type="data" format="interval" label="near intervals in"/>
```

The following demonstrates a ``param`` which may accept multiple files and
multiple formats.

```xml
<param format="sam,bam" multiple="true" name="bamOrSamFile" type="data"
       label="Alignments in BAM or SAM format"
       help="The set of aligned reads." />
```




### Attributes
Attribute | Details | Required
--- | --- | ---
``format`` | Only if ``type`` attribute value is ``data`` or ``data_collection`` - the list of supported data formats is contained in the [/config/datatypes_conf.xml.sample](https://github.com/galaxyproject/galaxy/blob/dev/config/datatypes_conf.xml.sample) file. Use the file extension. | False
``multiple`` | Allow multiple valus to be selected. Valid with ``data`` and ``select`` parameters. | False


#### ``select``

The following will create a select list containing the options "Downstream" and
"Upstream". Depending on the selection, a ``d`` or ``u`` value will be passed to
the ``$upstream_or_down`` variable on the command line.

```xml
<param name="upstream_or_down" type="select" label="Get">
  <option value="u">Upstream</option>
  <option value="d">Downstream</option>
</param>
```

The following will create a checkbox list allowing the user to select
"Downstream", "Upstream", both, or neither. Depending on the selection, the
value of ``$upstream_or_down`` will be ``d``, ``u``, ``u,d``, or "".

```xml
<param name="upstream_or_down" type="select" label="Get" multiple="true" display="checkboxes">
  <option value="u">Upstream</option>
  <option value="d">Downstream</option>
</param>
```




### Attributes
Attribute | Details | Required
--- | --- | ---
``data_ref`` | Only valid if ``type`` attribute value is ``select`` or ``data_column``. Used with select lists whose options are dynamically generated based on certain metadata attributes of the dataset upon which this parameter depends (usually but not always the tool's input dataset). | False
``display`` | This attribute is used only if ``type`` attribute value is ``select`` - render a select list as a set of check boxes or radio buttons. Defaults to a drop-down menu select list. | False
``multiple`` | Allow multiple valus to be selected. Valid with ``data`` and ``select`` parameters. | False
``dynamic_options`` | Deprecated/discouraged method to allow access to Python code to generate options for a select list. See ``code``'s documentation for an example. | False


#### ``data_column``

This parameter type is used to select columns from a parameter.




### Attributes
Attribute | Details | Required
--- | --- | ---
``force_select`` | Used only if the ``type`` attribute value is ``data_column``, this is deprecated and the inverse of ``optional``. Set to ``false`` to not force user to select an option in the list. | False
``numerical`` | Used only if the ``type`` attribute value is ``data_column``, if ``true`` the column will be treated as numerical when filtering columns based on metadata. | False


#### ``drill_down``




### Attributes
Attribute | Details | Required
--- | --- | ---
``hierarchy`` | Used only if the ``type`` attribute value is ``drill_down``, this attribute determines the drill down is ``recursive`` or ``exact``. | False


#### ``data_collection``




### Attributes
Attribute | Details | Required
--- | --- | ---
``format`` | Only if ``type`` attribute value is ``data`` or ``data_collection`` - the list of supported data formats is contained in the [/config/datatypes_conf.xml.sample](https://github.com/galaxyproject/galaxy/blob/dev/config/datatypes_conf.xml.sample) file. Use the file extension. | False
``collection_type`` | This is only valid if ``type`` is ``data_collection``. Restrict the kind of collection that can be consumed by this parameter (e.g. ``paired``, ``list:paired``, ``list``). Multiple such collection types can be specified here as a comma separated list. | False


The following will create a parameter that only accepts paired FASTQ files grouped into a collection.

##### Examples

```xml
<param name="inputs" type="data_collection" collection_type="paired" label="Input FASTQs" format="fastq">
</param>
```

More detailed information on writing tools that consume collections can be found
in the [planemo documentation](http://planemo.readthedocs.io/en/latest/writing_advanced.html#collections).

#### ``color``




### Attributes
Attribute | Details | Required
--- | --- | ---
``value`` | The default value for this parameter. | False


##### Examples

The following example will create a color selector parameter.

```xml
<param name="feature_color" type="color" label="Default feature color" value="#ff00ff">
</param>
```

Given that the output includes a pound sign, it is often convenient to use a
sanitizer to prevent Galaxy from escaping the result.

```xml
<param name="feature_color" type="color" label="Default feature color" value="#ff00ff">
  <sanitizer>
    <valid initial="string.letters,string.digits">
      <add value="#" />
    </valid>
  </sanitizer>
</param>
```

This covers examples of the most common parameter types, the remaining parameter
types are more obsecure and less likely to be useful for most tool authors.




### Attributes
Attribute | Details | Required
--- | --- | ---
``type`` | Describes the parameter type - each different type as different semantics and the tool form widget is different. Currently valid parameter types are: ``text``,  ``integer``,  ``float``,  ``boolean``,  ``genomebuild``,  ``select``, ``color``,  ``data_column``,  ``hidden``,  ``hidden_data``,  ``baseurl``, ``file``,  ``ftpfile``,  ``data``,  ``data_collection``,  ``library_data``, ``drill_down``. The definition of supported parameter types as defined in the ``parameter_types`` dictionary in [/lib/galaxy/tools/parameters/basic.py](https://github.com/galaxyproject/galaxy/blob/master/lib/galaxy/tools/parameters/basic.py). | True
``name`` | Name for this element. This ``name`` is used as the Cheetah variable containing the user-supplied parameter name in ``command`` and ``configfile`` elements. The name should not contain pipes or periods (e.g. ``.``). Some "reserved" names are ``REDIRECT_URL``, ``DATA_URL``, ``GALAXY_URL``. | False
``area`` | Boolean indicating if this should be rendered as a one line text box (if ``false``) or a multi-line text area (if ``true``). | False
``argument`` | If the parameter reflects just one command line argument of a certain tool, this tag should be set to that particular argument. It is rendered in parenthesis after the help section, and it will create the name attribute from the argument attribute by stripping the dashes (e.g. if ``argument="--sensitive"`` then ``name="sensitive"`` is implicit). | False
``label`` | The attribute value will be displayed on the tool page as the label of the form field (``label="Sort Query"``). | False
``help`` | Short bit of text, rendered on the tool form just below the associated field to provide information about the field. Find the Intergalactic Utilities Commision suggested best practices for this element [here](http://planemo.readthedocs.io/en/latest/standards/docs/best_practices/tool_xml.html#parameter-help). | False
``value`` | The default value for this parameter. | False
``optional`` | If ``false``, parameter must have a value. Defaults to "false". | False
``min`` | Minimum valid parameter value - only valid when ``type`` is ``integer`` or ``float``. | False
``max`` | Maximum valid parameter value - only valid when ``type`` is ``integer`` or ``float``. | False
``format`` | Only if ``type`` attribute value is ``data`` or ``data_collection`` - the list of supported data formats is contained in the [/config/datatypes_conf.xml.sample](https://github.com/galaxyproject/galaxy/blob/dev/config/datatypes_conf.xml.sample) file. Use the file extension. | False
``collection_type`` | This is only valid if ``type`` is ``data_collection``. Restrict the kind of collection that can be consumed by this parameter (e.g. ``paired``, ``list:paired``, ``list``). Multiple such collection types can be specified here as a comma separated list. | False
``data_ref`` | Only valid if ``type`` attribute value is ``select`` or ``data_column``. Used with select lists whose options are dynamically generated based on certain metadata attributes of the dataset upon which this parameter depends (usually but not always the tool's input dataset). | False
``accept_default`` | Documentation for PermissiveBoolean | False
``force_select`` | Used only if the ``type`` attribute value is ``data_column``, this is deprecated and the inverse of ``optional``. Set to ``false`` to not force user to select an option in the list. | False
``use_header_names`` | Used only if the ``type`` attribute value is ``data_column``, if ``true`` Galaxy assumes first row of ``data_ref`` is a header and builds the select list with these values rather than the more generic ``c1`` ... ``cN``. | False
``display`` | This attribute is used only if ``type`` attribute value is ``select`` - render a select list as a set of check boxes or radio buttons. Defaults to a drop-down menu select list. | False
``multiple`` | Allow multiple valus to be selected. Valid with ``data`` and ``select`` parameters. | False
``numerical`` | Used only if the ``type`` attribute value is ``data_column``, if ``true`` the column will be treated as numerical when filtering columns based on metadata. | False
``hierarchy`` | Used only if the ``type`` attribute value is ``drill_down``, this attribute determines the drill down is ``recursive`` or ``exact``. | False
``checked`` | Set to ``true`` if the ``boolean`` parameter should be checked (or ``true``) by default. | False
``truevalue`` | The parameter value in the Cheetah template if the parameter is ``true`` or checked by the user. Only valid if ``type`` is ``boolean``. | False
``falsevalue`` | The parameter value in the Cheetah template if the parameter is ``false`` or not checked by the user. Only valid if ``type`` is ``boolean``. | False
``size`` | Used only if ``type`` attribute value is ``text``. To create a multi-line text box add an ``area="True"`` attribute to the param tag. This can be one dimensional (e.g. ``size="40"``) or two dimensional (e.g. ``size="5x25"``). | False
``dynamic_options`` | Deprecated/discouraged method to allow access to Python code to generate options for a select list. See ``code``'s documentation for an example. | False




<a name="tool|inputs|param|validator"></a>
## ``tool`` > ``inputs`` > ``param`` > ``validator``


See the
[annotation_profiler](https://github.com/galaxyproject/tools-devteam/blob/master/tools/annotation_profiler/annotation_profiler.xml)
tool for an example of how to use this tag set. This tag set is contained within
the <param> tag set - it applies a validator to the containing parameter.

### Examples

The following demonstrates a simple validator ``unspecified_build`` ensuring
that a dbkey is present on the selected dataset. This example is taken from the
[extract_genomic_dna](https://github.com/galaxyproject/tools-iuc/blob/master/tools/extract_genomic_dna/extract_genomic_dna.xml#L42)
tool.

```xml
<param name="input" type="data" format="gff,interval" label="Fetch sequences for intervals in">
    <validator type="unspecified_build" />
</param>
```

Along the same line, the following example taken from
[samtools_mpileup](https://github.com/galaxyproject/tools-devteam/blob/master/tool_collections/samtools/samtools_mpileup/samtools_mpileup.xml)
ensures that a dbkey is present and that FASTA indices in the ``fasta_indexes``
tool data table are present.

```xml
<param format="bam" label="BAM file(s)" name="input_bam" type="data" min="1" multiple="True">
    <validator type="unspecified_build" />
    <validator type="dataset_metadata_in_data_table" metadata_name="dbkey" table_name="fasta_indexes" metadata_column="1"
               message="Sequences are not currently available for the specified build." />
</param>
```

In this older, somewhat deprecated example - a genome build of the dataset must
be stored in Galaxy clusters and the name of the genome (``dbkey``) must be one
of the values in the first column of file ``alignseq.loc`` - that could be
expressed with the validator. In general, ``dataset_metadata_in_file`` should be
considered deprecated in favor of

```xml
<validator type="dataset_metadata_in_file"
           filename="alignseq.loc"
           metadata_name="dbkey"
           metadata_column="1"
           message="Sequences are not currently available for the specified build."
           split=" "
           line_startswith="seq" />
```

A very common validator is simply ensure a Python expression is valid for a
specified value. In the following example - paths/names that downstream tools
use in filenames may not contain ``..``.

```xml
<validator type="expression" message="No two dots (..) allowed">'..' not in value</validator>
```



### Attributes
Attribute | Details | Required
--- | --- | ---
``type`` | The list of supported validators is in the ``validator_types`` dictionary in [/lib/galaxy/tools/parameters/validation.py](https://github.com/galaxyproject/galaxy/blob/dev/lib/galaxy/tools/parameters/validation.py). Valid values include: ``expression``, ``regex``, ``in_range``, ``length``, ``metadata``, ``unspecified_build``, ``no_options``, ``empty_field``, ``dataset_metadata_in_file``, ``dataset_metadata_in_data_table``, ``dataset_ok_validator`` | True
``message`` | The error message displayed on the tool form if validation fails. | False
``check`` | Comma-seperated list of metadata fields to check for if type is ``metadata``. If not specified, all non-optional metadata fields will be checked unless they appear in the list of fields specified by the ``skip`` attribute. | False
``table_name`` | Tool data table name to check against if ``type`` is ``dataset_metadata_in_tool_data``. See the documentation for [tool data tables](https://wiki.galaxyproject.org/Admin/Tools/Data%20Tables) and [data managers](https://wiki.galaxyproject.org/Admin/Tools/DataManagers) for more information. | False
``filename`` | Tool data filename to check against if ``type`` is ``dataset_metadata_in_file``. File should be present Galaxy's ``tool-data`` directory. | False
``metadata_name`` | Target metadata attribute name for ``dataset_metadata_in_data_table`` and ``dataset_metadata_in_file`` options. | False
``metadata_column`` | Target column for metadata attribute in ``dataset_metadata_in_data_table`` and ``dataset_metadata_in_file`` options. This can be an integer index to the column or a column name. | False
``line_startswith`` | Used to indicate lines in the file being used for validation start with a this attribute value. | False
``min`` | When the ``type`` attribute value is ``in_range`` - this is the minimum number allowed. | False
``max`` | When the ``type`` attribute value is ``in_range`` - this is the maximum number allowed. | False
``exclude_min`` | When the ``type`` attribute value is ``in_range`` - this boolean indicates if the ``min`` value is allowed. | False
``exclude_max`` | When the ``type`` attribute value is ``in_range`` - this boolean indicates if the ``max`` value is allowed. | False
``split`` | If ``type`` is `dataset_metadata_in_file``, this attribute is the column separator to use for values in the specified file. This default is ``\t`` and due to a bug in older versions of Galaxy, should not be modified. | False
``skip`` | Comma-seperated list of metadata fields to skip if type is ``metadata``. If not specified, all non-optional metadata fields will be checked unless ``check`` attribute is specified. | False




<a name="tool|inputs|param|option"></a>
## ``tool`` > ``inputs`` > ``param`` > ``option``


See [/tools/filters/sorter.xml](https://github.com/galaxyproject/galaxy/blob/master/tools/filters/sorter.xml)
for typical examples of how to use this tag set. This directive is used to described
static lists of options and is contained
within the [``param``](#tool|inputs|param) directive when the ``type`` attribute
value is ``select`` (i.e. ``<param type="select" ...>``).

### Example

```xml
<param name="style" type="select" label="with flavor">
    <option value="num">Numerical sort</option>
    <option value="gennum">General numeric sort</option>
    <option value="alpha">Alphabetical sort</option>
</param>
```

An option can also be annotated with ``selected="true"`` to specify a
default option.

```xml
<param name="col" type="select" label="From">
    <option value="0" selected="true">Column 1 / Sequence name</option>
    <option value="1">Column 2 / Source</option>
    <option value="2">Column 3 / Feature</option>
    <option value="6">Column 7 / Strand</option>
    <option value="7">Column 8 / Frame</option>
</param>
```




### Attributes
Attribute | Details | Required
--- | --- | ---
``value`` | The value of the corresponding variable when used the Cheetah template. Also the value that should be used in building test cases and used when building requests for the API. | False
``selected`` | A boolean parameter indicating if the corresponding option is selected by default (the default is ``false``). | False




<a name="tool|inputs|param|options"></a>
## ``tool`` > ``inputs`` > ``param`` > ``options``


See [/tools/extract/liftOver_wrapper.xml](https://github.com/galaxyproject/galaxy/blob/master/tools/extract/liftOver_wrapper.xml)
for an example of how to use this tag set. This tag set is optionally contained
within the ``<param>`` tag when the ``type`` attribute value is ``select`` or
``data`` and used to dynamically generated lists of options. This tag set
dynamically creates a list of options whose values can be
obtained from a predefined file stored locally or a dataset selected from the
current history.

There are at least five basic ways to use this tag - four of these correspond to
a ``from_XXX`` attribute on the ``options`` directive and the other is to
exclusively use ``filter``s to populate options.

* ``from_data_table`` - The options for the select list are dynamically obtained
  from a file specified in the Galaxy configuration file
  ``tool_data_table_conf.xml`` or from a Tool Shed installed data manager.
* ``from_dataset`` - The options for the select list are dynamically obtained
  from input dataset selected for the tool from the current history.
* ``from_file`` - The options for the select list are dynamically obtained from
  a file. This mechanis is discourage in favor of the more generic
  ``from_data_table``.
* ``from_parameter`` - The options for the select list are dynamically obtained
  from a parameter.
* Using ``filter``s - various filters can be used to populate options, see
  examples in the [``filter``](#tool|inputs|param|options|filter) documentation.

### ``from_data_table``

See Galaxy's
[data tables documentation](https://wiki.galaxyproject.org/Admin/Tools/Data%20Tables)
for information on setting up data tables.

Once a data table has been configured and populated, these can be easily
leveraged via tools.

This ``conditional`` block in the
[bowtie2](https://github.com/galaxyproject/tools-devteam/blob/master/tools/bowtie2/bowtie2_wrapper.xml)
wrapper demonstrates using ``from_data_table`` options as an
alternative to local reference data.

```xml
<conditional name="reference_genome">
  <param name="source" type="select" label="Will you select a reference genome from your history or use a built-in index?" help="Built-ins were indexed using default options. See `Indexes` section of help below">
    <option value="indexed">Use a built-in genome index</option>
    <option value="history">Use a genome from the history and build index</option>
  </param>
  <when value="indexed">
    <param name="index" type="select" label="Select reference genome" help="If your genome of interest is not listed, contact the Galaxy team">
      <options from_data_table="bowtie2_indexes">
        <filter type="sort_by" column="2"/>
        <validator type="no_options" message="No indexes are available for the selected input dataset"/>
      </options>
    </param>
  </when>
  <when value="history">
    <param name="own_file" type="data" format="fasta" metadata_name="dbkey" label="Select reference genome" />
  </when>
</conditional>
```

A minimal example wouldn't even need the ``filter`` or ``validator`` above, but
they are frequently nice features to add to your wrapper and can improve the user
experience of a tool.

### ``from_dataset``

The following example is taken from the Mothur tool
[remove.lineage.xml](https://github.com/galaxyproject/tools-iuc/blob/master/tools/mothur/remove.lineage.xml)
and demonstrates generating options from a dataset directly.

```xml
<param name="taxonomy" type="data" format="mothur.seq.taxonomy" label="taxonomy - Taxonomy" help="please make sure your file has no quotation marks in it"/>
<param name="taxons" type="select" size="120" optional="true" multiple="true" label="Browse Taxons from Taxonomy">
    <options from_dataset="taxonomy">
        <column name="name" index="1"/>
        <column name="value" index="1"/>
        <filter type="unique_value" name="unique_taxon" column="1"/>
        <filter type="sort_by" name="sorted_taxon" column="1"/>
    </options>
    <sanitizer>
        <valid initial="default">
            <add preset="string.printable"/>
            <add value=";"/>
            <remove value="&quot;"/>
            <remove value="&apos;"/>
        </valid>
    </sanitizer>
</param>
```

Filters can be used to generate options from dataset directly also as the
example below demonstrates (many more examples are present in the
[``filter``](#tool|inputs|param|options|filter) documentation).

```xml
<param name="species1" type="select" label="When Species" multiple="false">
    <options>
        <filter type="data_meta" ref="input1" key="species" />
    </options>
</param>
```

### ``from_file``

The following example is for Blast databases. In this example users maybe select
a database that is pre-formatted and cached in Galaxy clusters. When a new
dataset is available, admins must add the database to the local file named
"blastdb.loc". All such databases in that file are included in the options of
the select list. For a local instance, the file (e.g. ``blastdb.loc`` or
``alignseq.loc``) must be stored in the configured
[``tool_data_path``](https://github.com/galaxyproject/galaxy/tree/master/tool-data)
directory. In this example, the option names and values are taken from column 0
of the file.

```xml
<param name="source_select" type="select" display="radio" label="Choose target database">
    <options from_file="blastdb.loc">
        <column name="name" index="0"/>
        <column name="value" index="0"/>
    </options>
</param>
```

In general, ``from_file`` should be considered deprecated and  ``from_data_table``
should be prefered.

### ``from_parameter``

This variant of the ``options`` directive is discouraged because it exposes
internal Galaxy structures. See the older
[bowtie](https://github.com/galaxyproject/tools-devteam/blob/master/tools/bowtie_wrappers/bowtie_wrapper.xml)
wrappers for an example of these.

### Other Ways to Dynamically Generate Options

Though deprecated and discouraged, [``code``](#tool|code) blocks can also be
used to generate dynamic options.





### Attributes
Attribute | Details | Required
--- | --- | ---
``from_dataset`` | Documentation for from_dataset | False
``from_file`` | Documentation for from_file | False
``from_data_table`` | Documentation for from_data_table | False
``from_parameter`` | Documentation for from_parameter | False
``options_filter_attribute`` | Documentation for options_filter_attribute | False
``transform_lines`` | Documentation for transform_lines | False
``startswith`` | Documentation for startswith | False




<a name="tool|inputs|param|options|column"></a>
## ``tool`` > ``inputs`` > ``param`` > ``options`` > ``column``
Optionally contained within an
``<options>`` tag set - specifies columns used in building select options from a
file stored locally (i.e. index or tool data) or a dataset in the
current history.

Any number of columns may be described, but at least one must be given the name
``value`` and it will serve as the value of this parameter in the Cheetah
template and elsewhwere (e.g. in API for instance).

If a column named ``name`` is defined, this too has special meaning and it will
be the value the tool form user sees for each option. If no ``name`` column
appears, ``value`` will serve as the name.

### Examples

The following fragment shows options from the dataset in the current history
that has been selected as the value of the parameter named ``input1``.

```xml
<options from_dataset="input1">
    <column name="name" index="0"/>
    <column name="value" index="0"/>
</options>
```

The [interval2maf](https://github.com/galaxyproject/galaxy/blob/dev/tools/maf/interval2maf.xml)
tool makes use of this tag with files from a history, and the
[star_fusion](https://github.com/galaxyproject/tools-iuc/blob/master/tools/star_fusion/star_fusion.xml)
tool makes use of this to reference a data table.



### Attributes
Attribute | Details | Required
--- | --- | ---
``name`` | Name given to the column with index ``index``, the names ``name`` and ``value`` have special meaning as described above. | True
``index`` | 0-based index of the column in the target file. | True




<a name="tool|inputs|param|options|filter"></a>
## ``tool`` > ``inputs`` > ``param`` > ``options`` > ``filter``
Optionally contained within an
``<options>`` tag set - filter out values obtained from a locally stored file (e.g.
a tool data table) or a dataset in the current history.

### Examples

The following example from Mothur's
[remove.groups.xml](https://github.com/galaxyproject/tools-iuc/blob/master/tools/mothur/remove.groups.xml)
tool demonstrates filtering a select list based on the metadata of an input to
to the tool.

```xml
<param name="group_in" type="data" format="mothur.groups,mothur.count_table" label="group or count table - Groups"/>
<param name="groups" type="select" label="groups - Pick groups to remove" multiple="true" optional="false">
    <options>
        <filter type="data_meta" ref="group_in" key="groups"/>
    </options>
</param>
```

This more advanced example, taken from Mothur's
[remove.linage.xml](https://github.com/galaxyproject/tools-iuc/blob/master/tools/mothur/remove.lineage.xml)
tool demonstrates using filters to sort a list and remove duplicate entries.

```xml
<param name="taxonomy" type="data" format="mothur.cons.taxonomy" label="constaxonomy - Constaxonomy file. Provide either a constaxonomy file or a taxonomy file" help="please make sure your file has no quotation marks in it"/>
<param name="taxons" type="select" size="120" optional="true" multiple="true" label="Browse Taxons from Taxonomy">
    <options from_dataset="taxonomy">
        <column name="name" index="2"/>
        <column name="value" index="2"/>
        <filter type="unique_value" name="unique_taxon" column="2"/>
        <filter type="sort_by" name="sorted_taxon" column="2"/>
    </options>
    <sanitizer>
        <valid initial="default">
            <add preset="string.printable"/>
            <add value=";"/>
            <remove value="&quot;"/>
            <remove value="&apos;"/>
        </valid>
    </sanitizer>
</param>
```

This example taken from the
[hisat2](https://github.com/galaxyproject/tools-iuc/blob/master/tools/hisat2/hisat2.xml)
tool demonstrates filtering values from a tool data table.

```xml
<param help="If your genome of interest is not listed, contact the Galaxy team" label="Select a reference genome" name="index" type="select">
    <options from_data_table="hisat2_indexes">
        <filter column="2" type="sort_by" />
        <validator message="No genomes are available for the selected input dataset" type="no_options" />
    </options>
</param>
```

The
[gemini_load.xml](https://github.com/galaxyproject/tools-iuc/blob/master/tools/gemini/gemini_load.xml)
tool demonstrates adding values to an option list using ``filter``s.

```xml
<param name="infile" type="data" format="vcf" label="VCF file to be loaded in the GEMINI database" help="Only build 37 (aka hg19) of the human genome is supported.">
    <options>
        <filter type="add_value" value="hg19" />
        <filter type="add_value" value="Homo_sapiens_nuHg19_mtrCRS" />
        <filter type="add_value" value="hg_g1k_v37" />
    </options>
</param>
```

While this fragment from maf_to_interval.xml demonstrates removing items.

```xml
<param name="species" type="select" label="Select additional species"
       display="checkboxes" multiple="true"
       help="The species matching the dbkey of the alignment is always included.
       A separate history item will be created for each species.">
    <options>
        <filter type="data_meta" ref="input1" key="species" />
        <filter type="remove_value" meta_ref="input1" key="dbkey" />
    </options>
</param>
```

This example taken from
[snpSift_dbnsfp.xml](https://github.com/galaxyproject/tools-iuc/blob/master/tool_collections/snpsift/snpsift_dbnsfp/snpSift_dbnsfp.xml)
demonstrates splitting up strings into multiple values.

```xml
<param name="annotations" type="select" multiple="true" display="checkboxes" label="Annotate with">
    <options from_data_table="snpsift_dbnsfps">
        <column name="name" index="4"/>
        <column name="value" index="4"/>
        <filter type="param_value" ref="dbnsfp" column="3" />
        <filter type="multiple_splitter" column="4" separator=","/>
    </options>
</param>
```



### Attributes
Attribute | Details | Required
--- | --- | ---
``type`` | These values are defined in the module [/lib/galaxy/tools/parameters/dynamic_options.py](https://github.com/galaxyproject/galaxy/blob/master/lib/galaxy/tools/parameters/dynamic_options.py) in the ``filter_types`` dictionary. Currently defined values are: ``data_meta``, ``param_value``, ``static_value``, ``unique_value``, ``multiple_splitter``, ``attribute_value_splitter``, ``add_value``, ``remove_value``, and ``sort_by`` | True
``column`` | Column targeted by this filter - this attribute is unused and invalid if ``type`` is ``add_value`` or ``remove_value``. This can be a column index or a column name. | False
``name`` | Name displayed for value to add (only used with ``type`` of ``add_value``). | False
``ref`` | The attribute name of the reference file (tool data) or input dataset. Only used when ``type`` is ``data_meta`` (required), ``param_value`` (required), or ``remove_value`` (optional). | False
``key`` | When ``type`` is ``data_meta``, ``param_value``, or ``remove_value`` - this is the name of the metadata key of ref to filter by. | False
``multiple`` | For types ``data_meta`` and ``remove_value``, whether option values are multiple. Columns will be split by separator. Defaults to ``false``. | False
``separator`` | When ``type`` is ``data_meta``, ``multiple_splitter``, or ``remove_value`` - this is used to split one value into multiple parts. When ``type`` is ``data_meta`` or ``remove_value`` this is only used if ``multiple`` is set to ``true``. | False
``keep`` | If ``true``, keep columns matching the value, if ``false`` discard columns matching the value. Used when ``type`` is either ``static_value`` or ``param_value``. | False
``value`` | Target value of the operations - has slightly different meanings depending on ``type``. For instance when ``type`` is ``add_value`` it is the value to add to the list and when ``type`` is ``static_value`` it is the value compared against. | False
``ref_attribute`` | Only used when ``type`` is ``param_value``. Period (``.``) separated attribute chain of input (``ref``) attributes to use as value for filter. | False
``index`` | Used when ``type`` is ``add_value``, it is the index into the list to add the option to. If not set, the option will be added to the end of the list. | False




<a name="tool|inputs|param|sanitizer"></a>
## ``tool`` > ``inputs`` > ``param`` > ``sanitizer``


See
[/tools/filters/grep.xml](https://github.com/galaxyproject/galaxy/blob/dev/tools/filters/grep.xml)
for a typical example of how to use this tag set. This tag set is used to
replace the basic parameter sanitization with custom directives. This tag set is
contained within the ``<param>`` tag set - it contains a set of ``<valid>`` and
``<mapping>`` tags.

### Examples

This example replaces the invalid character default of ``X`` with the empty
string (so invalid characters are effectively dropped instead of replaced with
``X``) and indicates the only valid characters for this input are ASCII letters,
ASCII digits, and ``_``.

```
<param name="mystring" type="text" label="Say something interesting">
    <sanitizer invalid_char="">
        <valid initial="string.letters,string.digits"><add value="_" /> </valid>
    </sanitizer>
</param>
```

This example allows many more valid characters and specifies that ``&`` will just
be dropped from the input.

```
<sanitizer>
    <valid initial="string.printable">
        <remove value="&apos;"/>
    </valid>
    <mapping initial="none">
        <add source="&apos;" target=""/>
    </mapping>
</sanitizer>
```



### Attributes
Attribute | Details | Required
--- | --- | ---
``sanitize`` | This boolean parameter determines if the input is sanitized at all (the default is ``true``). | False
``invalid_char`` | The attribute specifies the character used as a replacement for invalid characters. | False




<a name="tool|inputs|param|sanitizer|valid"></a>
## ``tool`` > ``inputs`` > ``param`` > ``sanitizer`` > ``valid``
Contained within the
``<sanitizer>`` tag set, these are used to specify a list of allowed characters.
Contains ``<add>`` and ``<remove>`` tags.


### Attributes
Attribute | Details | Required
--- | --- | ---
``initial`` | This describes the initial characters to allow as valid, the default is ``string.letters + string.digits + " -=_.()/+*^,:?!"`` | False




<a name="tool|inputs|param|sanitizer|valid|add"></a>
## ``tool`` > ``inputs`` > ``param`` > ``sanitizer`` > ``valid`` > ``add``
This directive is used to add individual
characters or preset lists of characters. Character must not be allowed as a
valid input for the mapping to occur. Preset lists include default and none as well as those available from string.* (e.g. ``string.printable``).


### Attributes
Attribute | Details | Required
--- | --- | ---
``preset`` | Add target characters from the list of valid characters (e.g. ``string.printable``). | False
``value`` | Add a character to the list of valid characters. | False




<a name="tool|inputs|param|sanitizer|valid|remove"></a>
## ``tool`` > ``inputs`` > ``param`` > ``sanitizer`` > ``valid`` > ``remove``
This directive is used to remove
individual characters or preset lists of characters.
Character must not be allowed as a valid input for the mapping to occur.
Preset lists include default and none as well as those available from string.* (e.g. ``string.printable``).


### Attributes
Attribute | Details | Required
--- | --- | ---
``preset`` | Remove characters from the list of valid characters (e.g. ``string.printable``). | False
``value`` | A character to remove from the list of valid characters. | False




<a name="tool|inputs|param|sanitizer|mapping"></a>
## ``tool`` > ``inputs`` > ``param`` > ``sanitizer`` > ``mapping``
Contained within the <sanitizer> tag set. Used to specify a mapping of disallowed character to replacement string. Contains <add> and <remove> tags.


### Attributes
Attribute | Details | Required
--- | --- | ---
``initial`` | initial character mapping (default is ``galaxy.util.mapped_chars``) | False




<a name="tool|inputs|param|sanitizer|mapping|add"></a>
## ``tool`` > ``inputs`` > ``param`` > ``sanitizer`` > ``mapping`` > ``add``
Use to add character mapping during sanitization. Character must not be allowed as a valid input for the mapping to occur.


### Attributes
Attribute | Details | Required
--- | --- | ---
``source`` | Replace all occurrences of this character with the string of ``target``. | False
``target`` | Replace all occurrences of ``source`` with this string | False




<a name="tool|inputs|param|sanitizer|mapping|remove"></a>
## ``tool`` > ``inputs`` > ``param`` > ``sanitizer`` > ``mapping`` > ``remove``
Use to remove character mapping during sanitization.


### Attributes
Attribute | Details | Required
--- | --- | ---
``source`` | Character to remove from mapping. | False




<a name="tool|configfiles"></a>
## ``tool`` > ``configfiles``
See
[xy_plot.xml](https://github.com/galaxyproject/tools-devteam/blob/master/tools/xy_plot/xy_plot.xml)
for an example of how this tag set is used in a tool. This tag set is a
container for ``<configfile>`` and ``<inputs>`` tag sets - which can be used
to setup configuration files for use by tools.





<a name="tool|configfiles|configfile"></a>
## ``tool`` > ``configfiles`` > ``configfile``


This tag set is contained within the ``<configfiles>`` tag set. It allows for
the creation of a temporary file for file-based parameter transfer.

*Example*

The following is taken from the [xy_plot.xml](https://github.com/galaxyproject/tools-devteam/blob/master/tools/xy_plot/xy_plot.xml)
tool config.

```xml
<configfiles>
    <configfile name="script_file">
      ## Setup R error handling to go to stderr
      options( show.error.messages=F, error = function () { cat( geterrmessage(), file=stderr() ); q( "no", 1, F ) } )
      ## Determine range of all series in the plot
      xrange = c( NULL, NULL )
      yrange = c( NULL, NULL )
      #for $i, $s in enumerate( $series )
          s${i} = read.table( "${s.input.file_name}" )
          x${i} = s${i}[,${s.xcol}]
          y${i} = s${i}[,${s.ycol}]
          xrange = range( x${i}, xrange )
          yrange = range( y${i}, yrange )
      #end for
      ## Open output PDF file
      pdf( "${out_file1}" )
      ## Dummy plot for axis / labels
      plot( NULL, type="n", xlim=xrange, ylim=yrange, main="${main}", xlab="${xlab}", ylab="${ylab}" )
      ## Plot each series
      #for $i, $s in enumerate( $series )
          #if $s.series_type['type'] == "line"
              lines( x${i}, y${i}, lty=${s.series_type.lty}, lwd=${s.series_type.lwd}, col=${s.series_type.col} )
          #elif $s.series_type.type == "points"
              points( x${i}, y${i}, pch=${s.series_type.pch}, cex=${s.series_type.cex}, col=${s.series_type.col} )
          #end if
      #end for
      ## Close the PDF file
      devname = dev.off()
    </configfile>
</configfiles>
```

This file is then used in the ``command`` block of the tool as follows:

```xml
<command>bash "$__tool_directory__/r_wrapper.sh" "$script_file"</command>
```




### Attributes
Attribute | Details | Required
--- | --- | ---
``name`` | Cheetah variable used to reference the path to the file created with this directive. | False




<a name="tool|configfiles|inputs"></a>
## ``tool`` > ``configfiles`` > ``inputs``


This tag set is contained within the <configfiles> tag set. It tells Galaxy to
write out a JSON representation of the tool parameters .

*Example*

The following will create a cheetah variable that can be evaluated as ``$inputs`` that
will contain the tool parameter inputs.

```xml
<configfiles>
    <inputs name="inputs" />
<configfiles>
```

The following will instead write the inputs to the tool's working directory with
the specified name (i.e. ``inputs.json``).

```xml
<configfiles>
    <inputs name="inputs" filename="inputs.json" />
<configfiles>
```

A contrived example of a tool that uses this is the test tool
[inputs_as_json.xml](https://github.com/galaxyproject/galaxy/blob/dev/test/functional/tools/inputs_as_json.xml).



### Attributes
Attribute | Details | Required
--- | --- | ---
``name`` | Cheetah variable to populate the path to the inputs JSON file created in response to this directive. | False
``filename`` | Path relative to the working directory of the tool for the inputs JSON file created in response to this directive. | False




<a name="tool|environment_variables"></a>
## ``tool`` > ``environment_variables``

This directive should contain one or more ``environment_variable`` definition.
      





<a name="tool|environment_variables|environment_variable"></a>
## ``tool`` > ``environment_variables`` > ``environment_variable``


This directive defines an environment variable that will be available when the
tool executes. The body should be a Cheetah template block that may reference
the tool's inputs as demonstrated below.

### Example

The following demonstrates a couple ``environment_variable`` definitions.

```xml
<environment_variables>
    <environment_variable name="INTVAR">$inttest</environment_variable>
    <environment_variable name="IFTEST">#if int($inttest) == 3
ISTHREE
#else#
NOTTHREE
#end if#</environment_variable>
    </environment_variables>
</environment_variables>
```

If these environment variables are used in another Cheetah context, such as in
the ``command`` block, the ``$`` used indicate shell expansion of a variable
should be escaped with a ``\`` so prevent it from being evaluated as a Cheetah
variable instead of shell variable.

```xml
<command>
    echo "\$INTVAR"  >  $out_file1;
    echo "\$IFTEST"  >> $out_file1;
</command>
```




### Attributes
Attribute | Details | Required
--- | --- | ---
``name`` | Name of the environment variable to define. | False




<a name="tool|outputs"></a>
## ``tool`` > ``outputs``

Container tag set for the ``<data>`` and ``<collection>`` tag sets.
The files and collections created by tools as a result of their execution are
named by Galaxy. You specify the number and type of your output files using the
contained ``<data>`` and ``<collection>`` tags. These may be passed to your tool
executable through using line variables just like the parameters described in
the ``<inputs>`` documentation.






<a name="tool|outputs|data"></a>
## ``tool`` > ``outputs`` > ``data``


This tag set is contained within the ``<outputs>`` tag set, and it defines the
output data description for the files resulting from the tool's execution. The
value of the attribute ``label`` can be acquired from input parameters or metadata
in the same way that the command line parameters are (discussed in the
<command> tag set section above).

### Examples

The following will create a variable called ``$out_file1`` with data type
``pdf``.

```xml
<outputs>
    <data format="pdf" name="out_file1" />
</outputs>
```

The valid values for format can be found in
[/config/datatypes_conf.xml.sample](https://github.com/galaxyproject/galaxy/blob/dev/config/datatypes_conf.xml.sample).

The following will create a dataset in the history panel whose data type is the
same as that of the input dataset selected (and named ``input1``) for the tool.

```xml
<outputs>
    <data format_source="input1" name="out_file1" metadata_source="input1"/>
</outputs>
```

The following will create datasets in the history panel, setting the output data
type to be the same as that of an input dataset named by the ``format_source``
attribute. Note that a conditional name is not included, so 2 separate
conditional blocks should not contain parameters with the same name.

```xml
<inputs>
    <!-- fasta may be an aligned fasta that subclasses Fasta -->
    <param name="fasta" type="data" format="fasta" label="fasta - Sequences"/>
    <conditional name="qual">
        <param name="add" type="select" label="Trim based on a quality file?" help="">
            <option value="no">no</option>
            <option value="yes">yes</option>
        </param>
        <when value="no"/>
        <when value="yes">
            <!-- qual454, qualsolid, qualillumina -->
            <param name="qfile" type="data" format="qual" label="qfile - a quality file"/>
        </when>
    </conditional>
</inputs>
<outputs>
    <data format_source="fasta" name="trim_fasta"
          label="${tool.name} on ${on_string}: trim.fasta"/>
    <data format_source="qfile" name="trim_qual"
          label="${tool.name} on ${on_string}: trim.qual">
        <filter>qual['add'] == 'yes'</filter>
    </data>
</outputs>
```

Assume that the tool includes an input parameter named ``database`` which is a
select list (as shown below). Also assume that the user selects the first option
in the ``$database`` select list. Then the following will ensure that the tool
produces a tabular data set whose associated history item has the label ``Blat
on Human (hg18)``.

```xml
<inputs>
    <param format="tabular" name="input" type="data" label="Input stuff"/>
    <param type="select" name="database" label="Database">
        <option value="hg18">Human (hg18)</option>
        <option value="dm3">Fly (dm3)</option>
    </param>
</inputs>
<outputs>
    <data format="input" name="output" label="Blat on ${database.value_label}" />
</outputs>
```




### Attributes
Attribute | Details | Required
--- | --- | ---
``name`` | Name for this output. This ``name`` is used as the Cheetah variable containing the Galaxy assigned output path in ``command`` and ``configfile`` elements. The name should not contain pipes or periods (e.g. ``.``). | False
``auto_format`` | If ``true``, this output will sniffed and its format determined automatically by Galaxy. | False
``format`` | The short name for the output datatype. The valid values for format can be found in [/config/datatypes_conf.xml.sample](https://github.com/galaxyproject/galaxy/blob/dev/config/datatypes_conf.xml.sample) (e.g. ``format="pdf"`` or ``format="fastqsanger"``). | False
``format_source`` | This sets the data type of the output file to be the same format as that of a tool input dataset. | False
``metadata_source`` | This copies the metadata information from the tool's input dataset. This is particularly useful for interval data types where the order of the columns is not set. | False
``label`` | This will be the name of the history item for the output data set. The string can include structure like ``${<some param name>.<some attribute>}``, as discussed for command line parameters in the ``<command>`` tag set section above. The default label is ``${tool.name} on ${on_string}``. | False
``from_work_dir`` | Relative path to a file produced by the tool in its working directory. Output's contents are set to this file's contents. | False
``hidden`` | Boolean indicating whether to hide dataset in the history view. (Default is ``false``.) | False




<a name="tool|outputs|data|filter"></a>
## ``tool`` > ``outputs`` > ``data`` > ``filter``

The ``<data>`` tag can contain a ``<filter>`` tag which includes a Python code
block to be executed to test whether to include this output in the outputs the
tool ultimately creates. If the code, when executed, returns ``True``,
the output dataset is retained. In these code blocks the tool parameters appear
as Python variables and are thus referred to without the $ used for the Cheetah
template (used in the ``<command>`` tag). Variables that are part of
conditionals are accessed using a hash named after the conditional.

### Example

```xml
    <inputs>
      <param type="data" format="fasta" name="reference_genome" label="Reference genome" />
      <param type="data" format="bam" name="input_bam" label="Aligned reads" />
      <conditional name="options">
        <param label="Use advanced options" name="selection_mode" type="select">
          <option selected="True" value="defaults">Use default options</option>
          <option value="advanced">Use advanced options</option>
        </param>
        <when value="defaults"> </when>
        <when value="advanced">
          <param name="vcf_output" type="boolean" checked="false" label="VCF output"
            truevalue="--vcf" falsevalue="" />
        </when>
      <conditional>
    </inputs>
    <outputs>
      <data format="txt" label="Alignment report on ${on_string}" name="output_txt" />
      <data format="vcf" label="Variant summary on ${on_string}" name="output_vcf>
          <filter>options['selection_mode'] == 'advanced' and options['vcf_output']</filter>
      </data>
    </outputs>
    </outputs>
```






<a name="tool|outputs|data|change_format"></a>
## ``tool`` > ``outputs`` > ``data`` > ``change_format``
See
[extract_genomic_dna.xml](https://github.com/galaxyproject/tools-iuc/blob/master/tools/extract_genomic_dna/extract_genomic_dna.xml)
or the test tool
[output_action_change_format.xml](https://github.com/galaxyproject/galaxy/blob/dev/test/functional/tools/output_action_change_format.xml)
for simple examples of how this tag set is used in a tool. This tag set is
optionally contained within the ``<data>`` tag set and is the container tag set
for the following ``<when>`` tag set.





<a name="tool|outputs|data|change_format|when"></a>
## ``tool`` > ``outputs`` > ``data`` > ``change_format`` > ``when``


If the data type of the output dataset is the specified type, the data type is
changed to the desired type.

### Examples

Assume that your tool config includes the following select list parameter
structure:

```xml
<param name="out_format" type="select" label="Output data type">
    <option value="fasta">FASTA</option>
    <option value="interval">Interval</option>
</param>
```

Then whenever the user selects the ``interval`` option from the select list, the
following structure in your tool config will override the ``format="fasta"`` setting
in the ``<data>`` tag set with ``format="interval"``.

```xml
<outputs>
    <data format="fasta" name="out_file1">
        <change_format>
            <when input="out_format" value="interval" format="interval" />
        </change_format>
    </data>
</outputs>
```

See
[extract_genomic_dna.xml](https://github.com/galaxyproject/tools-iuc/blob/master/tools/extract_genomic_dna/extract_genomic_dna.xml)
or the test tool
[output_action_change_format.xml](https://github.com/galaxyproject/galaxy/blob/dev/test/functional/tools/output_action_change_format.xml)
for more examples.




### Attributes
Attribute | Details | Required
--- | --- | ---
``input`` | This value must be the attribute name of the desired input parameter (e.g. ``input="out_format"`` above). | True
``value`` | This value must also be an attribute name of an input parameter (e.g. ``value="interval"`` above). | True
``format`` | This value must be a supported data type (e.g. ``format="interval"``). See [/config/datatypes_conf.xml.sample](https://github.com/galaxyproject/galaxy/blob/dev/config/datatypes_conf.xml.sample) for a list of supported formats. | True




<a name="tool|outputs|data|actions"></a>
## ``tool`` > ``outputs`` > ``data`` > ``actions``


The ``actions`` directive allows tools to dynamically take actions related to an
``output`` either unconditionally or conditionally based on inputs. These
actions currently include setting metadata values and the output's data format.

The examples below will demonstrate that the ``actions`` tag contains child
``conditional`` tags. The these conditionals are met, additional ``action``
directives below the conditional are apply to the ``data`` output.

### Metadata

The ``<actions>`` in the Bowtie 2 wrapper is used in lieu of the deprecated
``<code>`` tag to set the ``dbkey`` of the output dataset. In
[bowtie2_wrapper.xml](https://github.com/galaxyproject/tools-devteam/blob/master/tools/bowtie2/bowtie2_wrapper.xml)
(see below), according to the first action block, if the
```reference_genome.source`` is ``indexed`` (not ``history``), then it will assign
the ``dbkey`` of the output file to be the same as that of the reference file. It
does this by looking at through the data table and finding the entry that has the
value that's been selected in the index dropdown box as column 1 of the loc file
entry and using the dbkey, in column 0 (ignoring comment lines (starting with #)
along the way).

If ``reference_genome.source`` is ``history``, it pulls the ``dbkey`` from the
supplied file.

```xml
<data format="bam" name="output" label="${tool.name} on ${on_string}: aligned reads (sorted BAM)">
  <filter>analysis_type['analysis_type_selector'] == "simple" or analysis_type['sam_opt'] is False</filter>
  <actions>
    <conditional name="reference_genome.source">
      <when value="indexed">
        <action type="metadata" name="dbkey">
          <option type="from_data_table" name="bowtie2_indexes" column="1" offset="0">
            <filter type="param_value" column="0" value="#" compare="startswith" keep="False"/>
            <filter type="param_value" ref="reference_genome.index" column="0"/>
          </option>
        </action>
      </when>
      <when value="history">
        <action type="metadata" name="dbkey">
          <option type="from_param" name="reference_genome.own_file" param_attribute="dbkey" />
        </action>
      </when>
    </conditional>
  </actions>
</data>
```

### Format

The Bowtie 2 example also demonstrates conditionally setting an output format
based on inputs, as shown below:

```xml
<data format="fastqsanger" name="output_unaligned_reads_r" label="${tool.name} on ${on_string}: unaligned reads (R)">
    <filter>( library['type'] == "paired" or library['type'] == "paired_collection" ) and library['unaligned_file'] is True</filter>
    <actions>
        <conditional name="library.type">
            <when value="paired">
                <action type="format">
                    <option type="from_param" name="library.input_2" param_attribute="ext" />
                </action>
            </when>
            <when value="paired_collection">
                <action type="format">
                    <option type="from_param" name="library.input_1" param_attribute="reverse.ext" />
                </action>
            </when>
        </conditional>
    </actions>
</data>
```

### Unconditional Actions - An Older Example

The first approach above to setting ``dbkey`` based on tool data tables is
prefered, but an older example using so called "loc files" directly is found
below.

In addition to demonstrating this lower-level direct access of .loc files, it
demonstrates an unconditional action. The second block would not be needed for
most cases - it was required in this tool to handle the specific case of a small
reference file used for functional testing. It says that if the dbkey has been
set to ``equCab2chrM`` (which is what the ```<filter type="metadata_value"...
column="1" />`` tag does), then it should be changed to ``equCab2`` (which is the
``<option type="from_param" ... column="0" ...>`` tag does).

```xml
<actions>
   <conditional name="refGenomeSource.genomeSource">
      <when value="indexed">
           <action type="metadata" name="dbkey">
            <option type="from_file" name="bowtie_indices.loc" column="0" offset="0">
               <filter type="param_value" column="0" value="#" compare="startswith" keep="False"/>
               <filter type="param_value" ref="refGenomeSource.index" column="1"/>
            </option>
         </action>
       </when>
    </conditional>
    <!-- Special casing equCab2chrM to equCab2 -->
    <action type="metadata" name="dbkey">
        <option type="from_param" name="refGenomeSource.genomeSource" column="0" offset="0">
            <filter type="insert_column" column="0" value="equCab2chrM"/>
            <filter type="insert_column" column="0" value="equCab2"/>
            <filter type="metadata_value" ref="output" name="dbkey" column="1" />
        </option>
    </action>
</actions>
```







<a name="tool|outputs|data|actions|conditional"></a>
## ``tool`` > ``outputs`` > ``data`` > ``actions`` > ``conditional``


This directive is contained within an output ``data``'s  ``actions`` directive.
This directive describes the state of the inputs required to apply an ``action``
(specified as children of the child ``when`` directives to this element) to an
output.

See [``actions``](#tool|outputs|data|actions) documentation for examples
of this directive.




### Attributes
Attribute | Details | Required
--- | --- | ---
``name`` | Name of the input parameter to base conditional logic on. The value of this parameter will be matched against nested ``when`` directives. | True




<a name="tool|outputs|data|actions|conditional|when"></a>
## ``tool`` > ``outputs`` > ``data`` > ``actions`` > ``conditional`` > ``when``


See [``actions``](#tool|outputs|data|actions) documentation for examples
of this directive.

      


### Attributes
Attribute | Details | Required
--- | --- | ---
``value`` | Value to match conditional input value against. | True




<a name="tool|outputs|data|actions|action"></a>
## ``tool`` > ``outputs`` > ``data`` > ``actions`` > ``action``


This directive is contained within an output ``data``'s  ``actions`` directive
(either directly or beneath a parent ``conditional`` tag). This directive
describes modifications to either the output's format or metadata (based on
whether ``type`` is ``format`` or ``metadata``).

See [``actions``](#tool|outputs|data|actions) documentation for examples
of this directive.




### Attributes
Attribute | Details | Required
--- | --- | ---
``type`` | Type of action (either ``format`` or ``metadata`` currently). | True
``name`` | If ``type="metadata"``, the name of the metadata element. | False
``default`` | If ``type="format"``, the default format if none of the nested options apply. | False




<a name="tool|outputs|data|discover_datasets"></a>
## ``tool`` > ``outputs`` > ``data`` > ``discover_datasets``


Describe datasets to dynamically collect after the job complete.

There are many simple tools with examples of this element distributed with
Galaxy, including:

* https://github.com/galaxyproject/galaxy/tree/master/test/functional/tools/multi_output.xml
* https://github.com/galaxyproject/galaxy/tree/master/test/functional/tools/multi_output_assign_primary.xml
* https://github.com/galaxyproject/galaxy/tree/master/test/functional/tools/multi_output_configured.xml

More information can be found on Planemo's documentation for
[multiple output files](http://planemo.readthedocs.io/en/latest/writing_advanced.html#multiple-output-files).



### Attributes
Attribute | Details | Required
--- | --- | ---
``pattern`` | Regular expression used to find filenames and parse dynamic properties. | True
``directory`` | Directory (relative to working directory) to search for files. | False
``format`` | Format (or datatype) of discovered datasets (an alias with ``ext``). | False
``ext`` | Format (or datatype) of discovered datasets (an alias with ``format``). | False
``visible`` | Indication if this dataset is visible in output history. This defaults to ``false``, but probably shouldn't - be sure to set to ``true`` if that is your intention. | False
``assign_primary_output`` | Replace the primary dataset described by the parameter ``data`` parameter with the first output discovered. | False




<a name="tool|outputs|collection"></a>
## ``tool`` > ``outputs`` > ``collection``


This tag set is contained within the ``<outputs>`` tag set, and it defines the
output dataset collection description resulting from the tool's execution. The
value of the attribute ``label`` can be acquired from input parameters or
metadata in the same way that the command line parameters are (discussed in the
[``command``](#tool|command) directive).

Creating collections in tools is covered in-depth in
[planemo's documentation](http://planemo.readthedocs.io/en/latest/writing_advanced.html#creating-collections).




### Attributes
Attribute | Details | Required
--- | --- | ---
``name`` | Name for this output. This ``name`` is used as the Cheetah variable containing the Galaxy assigned output path in ``command`` and ``configfile`` elements. The name should not contain pipes or periods (e.g. ``.``). | True
``type`` | Collection type for output (e.g. ``paired``, ``list``, or ``list:list``). | False
``label`` | This will be the name of the history item for the output data set. The string can include structure like ``${<some param name>.<some attribute>}``, as discussed for command line parameters in the ``<command>`` tag set section above. The default label is ``${tool.name} on ${on_string}``. | False
``format_source`` | This is the name of input collection or dataset to derive output dataset collection's element's format/datatype from. | False
``type_source`` | This is the name of input collection to derive collection's type (e.g. ``collection_type``) from. | False
``structured_like`` | This is the name of input collection or dataset to derive "structure" of the output from (output element count and identifiers). For instance, if the referenced input has three ordered items with identifiers ``sample1``, ``sample2``,  and ``sample3`` | False
``inherit_format`` | If ``structured_like`` is set, inherit format of outputs from format of corresponding input. | False




<a name="tool|outputs|collection|filter"></a>
## ``tool`` > ``outputs`` > ``collection`` > ``filter``

The ``<data>`` tag can contain a ``<filter>`` tag which includes a Python code
block to be executed to test whether to include this output in the outputs the
tool ultimately creates. If the code, when executed, returns ``True``,
the output dataset is retained. In these code blocks the tool parameters appear
as Python variables and are thus referred to without the $ used for the Cheetah
template (used in the ``<command>`` tag). Variables that are part of
conditionals are accessed using a hash named after the conditional.

### Example

```xml
    <inputs>
      <param type="data" format="fasta" name="reference_genome" label="Reference genome" />
      <param type="data" format="bam" name="input_bam" label="Aligned reads" />
      <conditional name="options">
        <param label="Use advanced options" name="selection_mode" type="select">
          <option selected="True" value="defaults">Use default options</option>
          <option value="advanced">Use advanced options</option>
        </param>
        <when value="defaults"> </when>
        <when value="advanced">
          <param name="vcf_output" type="boolean" checked="false" label="VCF output"
            truevalue="--vcf" falsevalue="" />
        </when>
      <conditional>
    </inputs>
    <outputs>
      <data format="txt" label="Alignment report on ${on_string}" name="output_txt" />
      <data format="vcf" label="Variant summary on ${on_string}" name="output_vcf>
          <filter>options['selection_mode'] == 'advanced' and options['vcf_output']</filter>
      </data>
    </outputs>
    </outputs>
```






<a name="tool|outputs|collection|discover_datasets"></a>
## ``tool`` > ``outputs`` > ``collection`` > ``discover_datasets``


This tag allows one to describe the datasets contained within an output
collection dynamically, such that the outputs are "discovered" based on regular
expressions after the job is complete.

There are many simple tools with examples of this element distributed with
Galaxy, including:

* https://github.com/galaxyproject/galaxy/blob/master/test/functional/tools/collection_split_on_column.xml
* https://github.com/galaxyproject/galaxy/blob/master/test/functional/tools/collection_creates_dynamic_list_of_pairs.xml
* https://github.com/galaxyproject/galaxy/blob/master/test/functional/tools/collection_creates_dynamic_nested.xml




### Attributes
Attribute | Details | Required
--- | --- | ---
``pattern`` | Regular expression used to find filenames and parse dynamic properties. | True
``directory`` | Directory (relative to working directory) to search for files. | False
``format`` | Format (or datatype) of discovered datasets (an alias with ``ext``). | False
``ext`` | Format (or datatype) of discovered datasets (an alias with ``format``). | False
``visible`` | Indication if this dataset is visible in output history. This defaults to ``false``, but probably shouldn't - be sure to set to ``true`` if that is your intention. | False




<a name="tool|tests"></a>
## ``tool`` > ``tests``


Container tag set to specify tests via the <test> tag sets. Any number of tests can be included,
and each test is wrapped within separate <test> tag sets. Functional tests are
executed via [Planemo](http://planemo.readthedocs.io/) or the
[run_tests.sh](https://github.com/galaxyproject/galaxy/blob/dev/run_tests.sh)
shell script distributed with Galaxy.

The documentation contained here is mostly reference documentation, for
tutorials on writing tool tests please check out Planemo's
[Test-Driven Development](http://planemo.readthedocs.io/en/latest/writing_advanced.html#test-driven-development)
documentation or the much older wiki content for
[WritingTests](https://wiki.galaxyproject.org/Admin/Tools/WritingTests).



### Best Practices

Find the Intergalactic Utilities Commision suggested best practices for this
element [here](http://planemo.readthedocs.io/en/latest/standards/docs/best_practices/tool_xml.html#tests).





<a name="tool|tests|test"></a>
## ``tool`` > ``tests`` > ``test``


This tag set contains the necessary parameter values for executing the tool via
the functional test framework.

### Example

The following two tests will execute the
[/tools/filters/sorter.xml](https://github.com/galaxyproject/galaxy/blob/dev/tools/filters/sorter.xml)
tool. Notice the way that the tool's inputs and outputs are defined.

```xml
  <tests>
    <test>
      <param name="input" value="1.bed" ftype="bed" />
      <param name="column" value="1"/>
      <param name="order" value="ASC"/>
      <param name="style" value="num"/>
      <output name="out_file1" file="sort1_num.bed" ftype="bed" />
    </test>
    <test>
      <param name="input" value="7.bed" ftype="bed" />
      <param name="column" value="1"/>
      <param name="order" value="ASC"/>
      <param name="style" value="alpha"/>
      <output name="out_file1" file="sort1_alpha.bed" ftype="bed" />
    </test>
  </tests>
```

The following example, tests the execution of the MAF-to-FASTA converter
([/tools/maf/maf_to_fasta.xml](https://github.com/galaxyproject/galaxy/blob/master/tools/maf/maf_to_fasta.xml)).

```xml
<tests>
    <test>
        <param name="input1" value="3.maf" ftype="maf"/>
        <param name="species" value="canFam1"/>
        <param name="fasta_type" value="concatenated"/>
        <output name="out_file1" file="cf_maf2fasta_concat.dat" ftype="fasta"/>
    </test>
</tests>
```

This test demonstrates verifying specific properties about a test output instead
of directly comparing it to another file. Here the file attribute is not
specified and instead a series of assertions is made about the output.

```xml
<test>
    <param name="input" value="maf_stats_interval_in.dat" />
    <param name="lineNum" value="99999"/>
    <output name="out_file1">
        <assert_contents>
            <has_text text="chr7" />
            <not_has_text text="chr8" />
            <has_text_matching expression="1274\d+53" />
            <has_line_matching expression=".*\s+127489808\s+127494553" />
            <!-- &#009; is XML escape code for tab -->
            <has_line line="chr7&#009;127471195&#009;127489808" />
            <has_n_columns n="3" />
        </assert_contents>
    </output>
</test>
```




### Attributes
Attribute | Details | Required
--- | --- | ---
``expect_exit_code`` | Describe the job's expected exit code. | False
``expect_num_outputs`` | Assert the number of outputs this test should produce, this is useful to ensure ``filter`` directives are implemented correctly. | False
``expect_failure`` | Setting this to ``true`` indicates the expectation is for the job fail. If set to ``true`` no job output checks may be present in ``test`` definition. | False
``maxseconds`` | Maximum amount of time to let test run. | False




<a name="tool|tests|test|param"></a>
## ``tool`` > ``tests`` > ``test`` > ``param``


This tag set defines the tool's input parameters for executing the tool via the
functional test framework. See [``test``'s](#tool|tests|test) documentation for
some simple examples of parameters.




### Attributes
Attribute | Details | Required
--- | --- | ---
``name`` | This value must match the name of the associated input parameter (``param``). | True
``value`` | This value must be one of the legal values that can be assigned to an input parameter. | False
``ftype`` | This attribute name should be included only with parameters of ``type`` ``data`` for the tool. If this attribute name is not included, the functional test framework will attempt to determine the data type for the input dataset using the data type sniffers. | False
``dbkey`` | Specifies a ``dbkey`` value for the referenced input dataset. This is only valid if the corresponding parameter is of ``type`` ``data``. | False




<a name="tool|tests|test|repeat"></a>
## ``tool`` > ``tests`` > ``test`` > ``repeat``


Specify test parameters below an iteration of a ``repeat`` block with this
element.

``param`` elements in a ``test`` block can be arranged into nested ``repeat``,
``conditional``, and ``select`` structures to match the inputs. While this might
be overkill for simple tests, it helps prevent ambiguous definitions and keeps
things organized in large test cases. A future ``profile`` version of Galaxy
tools may require ``repeat`` blocks be explicitly defined with this directive.

### Examples

The test tool [disambiguate_repeats.xml](https://github.com/galaxyproject/galaxy/blob/dev/test/functional/tools/disambiguate_repeats.xml)
demonstrates the use of this directive.

This first test case demonstrates that this block allows different values for
the ``param`` named ``input`` to be tested even though this parameter name
appears in two different ``<repeat>`` elements in the ``<inputs>`` definition.

```xml
<!-- Can disambiguate repeats and specify multiple blocks using,
     nested structure. -->
<test>
    <repeat name="queries">
        <param name="input" value="simple_line.txt"/>
    </repeat>
    <repeat name="more_queries">
        <param name="input" value="simple_line_alternative.txt"/>
    </repeat>
    <output name="out_file1">
        <assert_contents>
            <has_line line="This is a line of text." />
            <has_line line="This is a different line of text." />
        </assert_contents>
    </output>
</test>
```

The second definition in that file demonstrates repeated ``<repeat>`` blocks
allowing multiple instances of a single repeat to be specified.

```xml
<!-- Multiple such blocks can be specified but only with newer API
     driven tests. -->
<test>
    <repeat name="queries">
        <param name="input" value="simple_line.txt"/>
    </repeat>
    <repeat name="queries">
        <param name="input" value="simple_line_alternative.txt"/>
    </repeat>
    <repeat name="more_queries">
        <param name="input" value="simple_line.txt"/>
    </repeat>
    <repeat name="more_queries">
        <param name="input" value="simple_line_alternative.txt"/>
    </repeat>
    <output name="out_file1" file="simple_lines_interleaved.txt"/>
</test>
```




### Attributes
Attribute | Details | Required
--- | --- | ---
``name`` | This value must match the name of the associated input ``repeat``. | True




<a name="tool|tests|test|section"></a>
## ``tool`` > ``tests`` > ``test`` > ``section``


Specify test parameters below a named of a ``section`` block matching
one in ``inputs`` with this element.

``param`` elements in a ``test`` block can be arranged into nested ``repeat``,
``conditional``, and ``select`` structures to match the inputs. While this might
be overkill for simple tests, it helps prevent ambiguous definitions and keeps
things organized in large test cases. A future ``profile`` version of Galaxy
tools may require ``section`` blocks be explicitly defined with this
directive.

### Examples

The test tool demonstrating sections
([section.xml](https://github.com/galaxyproject/galaxy/blob/dev/test/functional/tools/section.xml))
contains a test case demonstrating this block. This test case appears below:

```xml
<test>
    <section name="int">
        <param name="inttest" value="12456" />
    </section>
    <section name="float">
        <param name="floattest" value="6.789" />
    </section>
    <output name="out_file1">
        <assert_contents>
            <has_line line="12456" />
            <has_line line="6.789" />
        </assert_contents>
    </output>
</test>
```


      


### Attributes
Attribute | Details | Required
--- | --- | ---
``name`` | This value must match the name of the associated input ``section``. | True




<a name="tool|tests|test|conditional"></a>
## ``tool`` > ``tests`` > ``test`` > ``conditional``


Specify test parameters below a named of a ``conditional`` block matching
one in ``inputs`` with this element.

``param`` elements in a ``test`` block can be arranged into nested ``repeat``,
``conditional``, and ``select`` structures to match the inputs. While this might
be overkill for simple tests, it helps prevent ambiguous definitions and keeps
things organized in large test cases. A future ``profile`` version of Galaxy
tools may require ``conditional`` blocks be explicitly defined with this
directive.

### Examples

The following example demonstrates disambiguation of a parameter (named ``use``)
which appears in multiple ``param`` names in ``conditional``s in the ``inputs``
definition of the [disambiguate_cond.xml](https://github.com/galaxyproject/galaxy/blob/dev/test/functional/tools/disambiguate_cond.xml)
tool.

```xml
<!-- Can use nested conditional blocks as shown below to disambiguate
     various nested parameters. -->
<test>
    <conditional name="p1">
        <param name="use" value="False"/>
    </conditional>
    <conditional name="p2">
        <param name="use" value="True"/>
    </conditional>
    <conditional name="p3">
        <param name="use" value="False"/>
    </conditional>
    <conditional name="files">
        <param name="attach_files" value="True" />
        <conditional name="p4">
            <param name="use" value="True"/>
            <param name="file" value="simple_line_alternative.txt" />
        </conditional>
    </conditional>
    <output name="out_file1">
        <assert_contents>
            <has_line line="7 4 7" />
            <has_line line="This is a different line of text." />
        </assert_contents>
    </output>
</test>
```

The [tophat2](https://github.com/galaxyproject/tools-devteam/blob/master/tools/tophat2/tophat2_wrapper.xml)
tool demonstrates a real tool that benefits from more structured test cases
using the ``conditional`` test directive. One such test case from that tool is
shown below.

```xml
<!-- Test base-space paired-end reads with user-supplied reference fasta and full parameters -->
<test>
    <!-- TopHat commands:
    tophat2 -o tmp_dir -r 20 -p 1 -a 8 -m 0 -i 70 -I 500000 -g 40 +coverage-search +min-coverage-intron 50 +max-coverage-intro 20000 +segment-mismatches 2 +segment-length 25 +microexon-search +report_discordant_pairs tophat_in1 test-data/tophat_in2.fastqsanger test-data/tophat_in3.fastqsanger
    Replace the + with double-dash
    Rename the files in tmp_dir appropriately
    -->
    <conditional name="singlePaired">
      <param name="sPaired" value="paired"/>
      <param name="input1" ftype="fastqsanger" value="tophat_in2.fastqsanger"/>
      <param name="input2" ftype="fastqsanger" value="tophat_in3.fastqsanger"/>
      <param name="mate_inner_distance" value="20"/>
      <param name="report_discordant_pairs" value="Yes" />
    </conditional>
    <param name="genomeSource" value="indexed"/>
    <param name="index" value="tophat_test"/>
    <conditional name="params">
      <param name="settingsType" value="full"/>
      <param name="library_type" value="FR Unstranded"/>
      <param name="read_mismatches" value="5"/>
      <!-- Error: the read mismatches (5) and the read gap length (2) should be less than or equal to the read edit dist (2) -->
      <param name="read_edit_dist" value="5" />
      <param name="bowtie_n" value="Yes"/>
      <param name="mate_std_dev" value="20"/>
      <param name="anchor_length" value="8"/>
      <param name="splice_mismatches" value="0"/>
      <param name="min_intron_length" value="70"/>
      <param name="max_intron_length" value="500000"/>
      <param name="max_multihits" value="40"/>
      <param name="min_segment_intron" value="50" />
      <param name="max_segment_intron" value="500000" />
      <param name="seg_mismatches" value="2"/>
      <param name="seg_length" value="25"/>
      <conditional name="indel_search">
        <param name="allow_indel_search" value="No"/>
      </conditional>
      <conditional name="own_junctions">
        <param name="use_junctions" value="Yes" />
        <conditional name="gene_model_ann">
          <param name="use_annotations" value="No" />
        </conditional>
        <conditional name="raw_juncs">
          <param name="use_juncs" value="No" />
        </conditional>
        <conditional name="no_novel_juncs">
          <param name="no_novel_juncs" value="No" />
        </conditional>
      </conditional>
      <conditional name="coverage_search">
        <param name="use_search" value="No" />
      </conditional>
      <param name="microexon_search" value="Yes" />
      <conditional name="bowtie2_settings">
        <param name="b2_settings" value="No" />
      </conditional>
      <!-- Fusion search params -->
      <conditional name="fusion_search">
        <param name="do_search" value="Yes" />
        <param name="anchor_len" value="21" />
        <param name="min_dist" value="10000021" />
        <param name="read_mismatches" value="3" />
        <param name="multireads" value="4" />
        <param name="multipairs" value="5" />
        <param name="ignore_chromosomes" value="chrM"/>
      </conditional>
    </conditional>
    <conditional name="readGroup">
      <param name="specReadGroup" value="no" />
    </conditional>
    <output name="junctions" file="tophat2_out4j.bed" />
    <output name="accepted_hits" file="tophat_out4h.bam" compare="sim_size" />
</test>
```




### Attributes
Attribute | Details | Required
--- | --- | ---
``name`` | This value must match the name of the associated input ``conditional``. | True




<a name="tool|tests|test|output"></a>
## ``tool`` > ``tests`` > ``test`` > ``output``


This tag set defines the variable that names the output dataset for the
functional test framework. The functional test framework will execute the tool
using the parameters defined in the ``<param>`` tag sets and generate a
temporary file, which will either be compared with the file named in the
``file`` attribute value or checked against assertions made by a child
``assert_contents`` tag to verify that the tool is functionally correct.

        


### Attributes
Attribute | Details | Required
--- | --- | ---
``name`` | This value is the same as the value of the ``name`` attribute of the ``<data>`` tag set contained within the tool's ``<outputs>`` tag set. | False
``file`` | If specified, this value is the name of the output file stored in the target ``test-data`` directory which will be used to compare the results of executing the tool via the functional test framework. | False
``ftype`` | If specified, this value will be checked against the corresponding output's data type. If these do not match, the test will fail. | False
``sort`` | This flag causes the lines of the output to be sorted before they are compared to the expected output. This could be useful for non-deterministic output. | False
``value`` | An alias for ``file``. | False
``md5`` | If specified, the target output's MD5 hash should match the value specified here. For large static files it may be inconvenient to upload the entiry file and this can be used instead. | False
``checksum`` | If specified, the target output's checksum should match the value specified here. This value should have the form ``hash_type:hash_value`` (e.g. ``sha1:8156d7ca0f46ed7abac98f82e36cfaddb2aca041``). For large static files it may be inconvenient to upload the entiry file and this can be used instead. | False
``compare`` | Type of comparison to use when comparing test generated output files to expected output files. Currently valid value are ``diff`` (the default), ``re_match``, ``sim_size``, ``re_match_multiline``, and ``contains``. | False
``lines_diff`` | If ``compare`` is set to ``diff``, the number of lines of difference to allow (each line with a modification is a line added and a line removed so this counts as two lines). | False
``delta`` | If ``compare`` is set to ``sim_size``, this is the number of bytes different allowed. | False




<a name="tool|tests|test|output|discover_dataset"></a>
## ``tool`` > ``tests`` > ``test`` > ``output`` > ``discover_dataset``


This directive specifies a test for an output's discovered dataset. It acts as an
``output`` test tag in many ways and can define any tests of that tag (e.g.
``assert_contents``, ``value``, ``compare``, ``md5``, ``checksum``, ``metadata``, etc...).

### Example

The functional test tool
multi_output_assign_primary.xml](https://github.com/galaxyproject/galaxy/blob/dev/test/functional/tools/multi_output_assign_primary.xml)
provides a demonstration of using this tag.

```xml
<test>
  <param name="num_param" value="7" />
  <param name="input" ftype="txt" value="simple_line.txt"/>
  <output name="sample">
    <assert_contents>
      <has_line line="1" />
    </assert_contents>
    <!-- no sample1 it was consumed by named output "sample" -->
    <discovered_dataset designation="sample2" ftype="tabular">
      <assert_contents><has_line line="2" /></assert_contents>
    </discovered_dataset>
    <discovered_dataset designation="sample3" ftype="tabular">
      <assert_contents><has_line line="3" /></assert_contents>
    </discovered_dataset>
  </output>
</test>
```




### Attributes
Attribute | Details | Required
--- | --- | ---
``designation`` | The designation of the discovered dataset. | False




<a name="tool|tests|test|output|metadata"></a>
## ``tool`` > ``tests`` > ``test`` > ``output`` > ``metadata``


This directive specifies a test for an output's metadata as an expected key-value pair.

### Example

The functional test tool
[tool_provided_metadata_1.xml](https://github.com/galaxyproject/galaxy/blob/dev/test/functional/tools/tool_provided_metadata_1.xml)
provides a demonstration of using this tag.

```xml
<test>
  <param name="input1" value="simple_line.txt" />
  <output name="out1" file="simple_line.txt" ftype="txt">
    <metadata name="name" value="my dynamic name" />
    <metadata name="info" value="my dynamic info" />
    <metadata name="dbkey" value="cust1" />
  </output>
</test>
```




### Attributes
Attribute | Details | Required
--- | --- | ---
``name`` | Name of the metdata element to check. | True
``value`` | Expected value (as a string) of metadata value. | True




<a name="tool|tests|test|output|assert_contents"></a>
## ``tool`` > ``tests`` > ``test`` > ``output`` > ``assert_contents``


This tag set defines a sequence of checks or assertions to run against the
target output. This tag requires no attributes, but child tags should be used to
define the assertions to make about the output. The functional test framework
makes it easy to extend Galaxy with such tags, the following table summarizes
many of the default assertion tags that come with Galaxy and examples of each
can be found below.

The implementation of these tags are simply Python functions defined in the
[``galaxy.tools.verify.asserts``](https://github.com/galaxyproject/galaxy/tree/dev/lib/galaxy/tools/verify/asserts]
module.

      

Child Element/Assertion | Details 
--- | ---
``has_text`` | Asserts the specified ``text`` appears in the output (e.g. ``<has_text text="chr7">``).
``not_has_text`` | Asserts the specified ``text`` does not appear in the output (e.g. ``<not_has_text text="chr8" />``).
``has_text_matching`` | Asserts text matching the specified regular expression (``expression``) appears in the output (e.g. ``<has_text_matching expression="1274\d+53" />`` ).
``has_line`` | Asserts a line matching the specified string (``line``) appears in the output (e.g. ``<has_line line="A full example line." />``).
``has_line_matching`` | Asserts a line matching the specified regular expression (``expression``) appears in the output (e.g. ``<has_line_matching expression=".*\s+127489808\s+127494553" />``).
``has_n_columns`` | Asserts tabular output contains the specified number (``n``) of columns (e.g. ``<has_n_columns n="3" />``).
``is_valid_xml`` | Asserts the output is a valid XML file (e.g. ``<is_valid_xml />``).
``has_element_with_path`` | Asserts the XML output contains at least one element (or tag) with the specified XPath-like ``path`` (e.g. ``<has_element_with_path path="BlastOutput_param/Parameters/Parameters_matrix" />``).
``has_n_elements_with_path`` | Asserts the XML output contains the specified number (``n``) of elements (or tags) with the specified XPath-like ``path`` (e.g. ``<has_n_elements_with_path n="9" path="BlastOutput_iterations/Iteration/Iteration_hits/Hit/Hit_num" />``).
``element_text_is`` | Asserts the text of the XML element with the specified XPath-like ``path`` is the specified ``text`` (e.g. ``<element_text_is path="BlastOutput_program" text="blastp" />``).
``element_text_matches`` | Asserts the text of the XML element with the specified XPath-like ``path`` matches the regular expression defined by ``expression`` (e.g. ``<element_text_matches path="BlastOutput_version" expression="BLASTP\s+2\.2.*" />``).
``attribute_is`` | Asserts the XML ``attribute`` for the element (or tag) with the specified XPath-like ``path`` is the specified ``text`` (e.g. ``<attribute_is path="outerElement/innerElement1" attribute="foo" text="bar" />`` ).
``attribute_matches`` | Asserts the XML ``attribute`` for the element (or tag) with the specified XPath-like ``path`` matches the regular expression specified by ``expression`` (e.g. ``<attribute_matches path="outerElement/innerElement2" attribute="foo2" expression="bar\d+" />``).
``element_text`` | This tag allows the developer to recurisively specify additional assertions as child elements about just the text contained in the element specified by the XPath-like ``path`` (e.g. ``<element_text path="BlastOutput_iterations/Iteration/Iteration_hits/Hit/Hit_def"><not_has_text text="EDK72998.1" /></element_text>``).


### Examples

The following demonstrtes a wide variety of text-based and tabular
assertion statements.

```xml
<output name="out_file1">
    <assert_contents>
        <has_text text="chr7" />
        <not_has_text text="chr8" />
        <has_text_matching expression="1274\d+53" />
        <has_line_matching expression=".*\s+127489808\s+127494553" />
        <!-- &#009; is XML escape code for tab -->
        <has_line line="chr7&#009;127471195&#009;127489808" />
        <has_n_columns n="3" />
    </assert_contents>
</output>
```

The following demonstrtes a wide variety of XML assertion statements.

```xml
<output name="out_file1">
    <assert_contents>
        <is_valid_xml />
        <has_element_with_path path="BlastOutput_param/Parameters/Parameters_matrix" />
        <has_n_elements_with_path n="9" path="BlastOutput_iterations/Iteration/Iteration_hits/Hit/Hit_num" />
        <element_text_matches path="BlastOutput_version" expression="BLASTP\s+2\.2.*" />
        <element_text_is path="BlastOutput_program" text="blastp" />
        <element_text path="BlastOutput_iterations/Iteration/Iteration_hits/Hit/Hit_def">
            <not_has_text text="EDK72998.1" />
            <has_text_matching expression="ABK[\d\.]+" />
        </element_text>
    </assert_contents>
</output>
```

The following demonstrtes verifying XML content with XPath-like expressions.

```xml
<output name="out_file1">
    <assert_contents>
        <attribute_is path="outerElement/innerElement1" attribute="foo" text="bar" />
        <attribute_matches path="outerElement/innerElement2" attribute="foo2" expression="bar\d+" />
    </assert_contents>
</output>
```







<a name="tool|tests|test|output_collection"></a>
## ``tool`` > ``tests`` > ``test`` > ``output_collection``


Define tests for extra files corresponding to an output collection.

``output_collection`` directives should specify a ``name`` and ``type``
attribute to describe the expected output collection as a whole.

Expectations about collecton contents are described using child ``element``
directives. For nested collections, these child ``element`` directives may
themselves contain children.

### Examples

The [genetrack](https://github.com/galaxyproject/tools-iuc/blob/master/tools/genetrack/genetrack.xml)
tool demonstrates basic usage of an ``output_collection`` test expectation.

```xml
<test>
    <param name="input" value="genetrack_input2.gff" ftype="gff" />
    <param name="input_format" value="gff" />
    <param name="sigma" value="5" />
    <param name="exclusion" value="20" />
    <param name="up_width" value="10" />
    <param name="down_width" value="10" />
    <param name="filter" value="3" />
    <output_collection name="genetrack_output" type="list">
        <element name="s5e20u10d10F3_on_data_1" file="genetrack_output2.gff" ftype="gff" />
    </output_collection>
</test>
```

The [CWPair2](https://github.com/galaxyproject/tools-iuc/blob/master/tools/cwpair2/cwpair2.xml)
tool demonstrates that ``element``s can specify a ``compare`` attribute just
like [``output``](#tool|tests|test|output).

```xml
<test>
    <param name="input" value="cwpair2_input1.gff" />
    <param name="up_distance" value="25" />
    <param name="down_distance" value="100" />
    <param name="method" value="all" />
    <param name="binsize" value="1" />
    <param name="threshold_format" value="relative_threshold" />
    <param name="relative_threshold" value="0.0" />
    <param name="output_files" value="matched_pair" />
    <output name="statistics_output" file="statistics1.tabular" ftype="tabular" />
    <output_collection name="MP" type="list">
        <element name="data_MP_closest_f0u25d100_on_data_1.gff" file="closest_mp_output1.gff" ftype="gff" compare="contains"/>
        <element name="data_MP_largest_f0u25d100_on_data_1.gff" file="largest_mp_output1.gff" ftype="gff" compare="contains"/>
        <element name="data_MP_mode_f0u25d100_on_data_1.gff" file="mode_mp_output1.gff" ftype="gff" compare="contains"/>
    </output_collection>
</test>
```

The
[collection_creates_dynamic_nested](https://github.com/galaxyproject/galaxy/blob/dev/test/functional/tools/collection_creates_dynamic_nested.xml)
test tool demonstrates the use of nested ``element`` directives as described
above. Notice also that it tests the output with ``assert_contents`` instead of
supplying a ``file`` attribute. Like hinted at with with ``compare`` attribute
above, the ``element`` tag can specify any of the test attributes that apply to
the [``output``](#tool|tests|test|output) (e.g. ``md5``, ``compare``, ``diff``,
etc...).

```xml
<test>
  <param name="foo" value="bar" />
  <output_collection name="list_output" type="list:list">
    <element name="oe1">
      <element name="ie1">
        <assert_contents>
          <has_text_matching expression="^A\n$" />
        </assert_contents>
      </element>
      <element name="ie2">
        <assert_contents>
          <has_text_matching expression="^B\n$" />
        </assert_contents>
      </element>
    </element>
    <element name="oe2">
      <element name="ie1">
        <assert_contents>
          <has_text_matching expression="^C\n$" />
        </assert_contents>
      </element>
      <element name="ie2">
        <assert_contents>
          <has_text_matching expression="^D\n$" />
        </assert_contents>
      </element>
    </element>
    <element name="oe3">
      <element name="ie1">
        <assert_contents>
          <has_text_matching expression="^E\n$" />
        </assert_contents>
      </element>
      <element name="ie2">
        <assert_contents>
          <has_text_matching expression="^F\n$" />
        </assert_contents>
      </element>
    </element>
  </output_collection>
</test>
```




### Attributes
Attribute | Details | Required
--- | --- | ---
``name`` | This value is the same as the value of the ``name`` attribute of the ``<collecton>`` tag set contained within the tool's ``<outputs>`` tag set. | True
``type`` | Expected collection type (e.g. ``list``, ``paired``, or ``list:paired``). | False
``count`` | Number of elements in output collection. | False




<a name="tool|tests|test|assert_command"></a>
## ``tool`` > ``tests`` > ``test`` > ``assert_command``
Describe assertions about the job's
generated command-line.


This tag set defines a sequence of checks or assertions to run against the
target output. This tag requires no attributes, but child tags should be used to
define the assertions to make about the output. The functional test framework
makes it easy to extend Galaxy with such tags, the following table summarizes
many of the default assertion tags that come with Galaxy and examples of each
can be found below.

The implementation of these tags are simply Python functions defined in the
[``galaxy.tools.verify.asserts``](https://github.com/galaxyproject/galaxy/tree/dev/lib/galaxy/tools/verify/asserts]
module.

      

Child Element/Assertion | Details 
--- | ---
``has_text`` | Asserts the specified ``text`` appears in the output (e.g. ``<has_text text="chr7">``).
``not_has_text`` | Asserts the specified ``text`` does not appear in the output (e.g. ``<not_has_text text="chr8" />``).
``has_text_matching`` | Asserts text matching the specified regular expression (``expression``) appears in the output (e.g. ``<has_text_matching expression="1274\d+53" />`` ).
``has_line`` | Asserts a line matching the specified string (``line``) appears in the output (e.g. ``<has_line line="A full example line." />``).
``has_line_matching`` | Asserts a line matching the specified regular expression (``expression``) appears in the output (e.g. ``<has_line_matching expression=".*\s+127489808\s+127494553" />``).
``has_n_columns`` | Asserts tabular output contains the specified number (``n``) of columns (e.g. ``<has_n_columns n="3" />``).
``is_valid_xml`` | Asserts the output is a valid XML file (e.g. ``<is_valid_xml />``).
``has_element_with_path`` | Asserts the XML output contains at least one element (or tag) with the specified XPath-like ``path`` (e.g. ``<has_element_with_path path="BlastOutput_param/Parameters/Parameters_matrix" />``).
``has_n_elements_with_path`` | Asserts the XML output contains the specified number (``n``) of elements (or tags) with the specified XPath-like ``path`` (e.g. ``<has_n_elements_with_path n="9" path="BlastOutput_iterations/Iteration/Iteration_hits/Hit/Hit_num" />``).
``element_text_is`` | Asserts the text of the XML element with the specified XPath-like ``path`` is the specified ``text`` (e.g. ``<element_text_is path="BlastOutput_program" text="blastp" />``).
``element_text_matches`` | Asserts the text of the XML element with the specified XPath-like ``path`` matches the regular expression defined by ``expression`` (e.g. ``<element_text_matches path="BlastOutput_version" expression="BLASTP\s+2\.2.*" />``).
``attribute_is`` | Asserts the XML ``attribute`` for the element (or tag) with the specified XPath-like ``path`` is the specified ``text`` (e.g. ``<attribute_is path="outerElement/innerElement1" attribute="foo" text="bar" />`` ).
``attribute_matches`` | Asserts the XML ``attribute`` for the element (or tag) with the specified XPath-like ``path`` matches the regular expression specified by ``expression`` (e.g. ``<attribute_matches path="outerElement/innerElement2" attribute="foo2" expression="bar\d+" />``).
``element_text`` | This tag allows the developer to recurisively specify additional assertions as child elements about just the text contained in the element specified by the XPath-like ``path`` (e.g. ``<element_text path="BlastOutput_iterations/Iteration/Iteration_hits/Hit/Hit_def"><not_has_text text="EDK72998.1" /></element_text>``).







<a name="tool|tests|test|assert_stdout"></a>
## ``tool`` > ``tests`` > ``test`` > ``assert_stdout``
Describe assertions about the job's
standard output.


This tag set defines a sequence of checks or assertions to run against the
target output. This tag requires no attributes, but child tags should be used to
define the assertions to make about the output. The functional test framework
makes it easy to extend Galaxy with such tags, the following table summarizes
many of the default assertion tags that come with Galaxy and examples of each
can be found below.

The implementation of these tags are simply Python functions defined in the
[``galaxy.tools.verify.asserts``](https://github.com/galaxyproject/galaxy/tree/dev/lib/galaxy/tools/verify/asserts]
module.

      

Child Element/Assertion | Details 
--- | ---
``has_text`` | Asserts the specified ``text`` appears in the output (e.g. ``<has_text text="chr7">``).
``not_has_text`` | Asserts the specified ``text`` does not appear in the output (e.g. ``<not_has_text text="chr8" />``).
``has_text_matching`` | Asserts text matching the specified regular expression (``expression``) appears in the output (e.g. ``<has_text_matching expression="1274\d+53" />`` ).
``has_line`` | Asserts a line matching the specified string (``line``) appears in the output (e.g. ``<has_line line="A full example line." />``).
``has_line_matching`` | Asserts a line matching the specified regular expression (``expression``) appears in the output (e.g. ``<has_line_matching expression=".*\s+127489808\s+127494553" />``).
``has_n_columns`` | Asserts tabular output contains the specified number (``n``) of columns (e.g. ``<has_n_columns n="3" />``).
``is_valid_xml`` | Asserts the output is a valid XML file (e.g. ``<is_valid_xml />``).
``has_element_with_path`` | Asserts the XML output contains at least one element (or tag) with the specified XPath-like ``path`` (e.g. ``<has_element_with_path path="BlastOutput_param/Parameters/Parameters_matrix" />``).
``has_n_elements_with_path`` | Asserts the XML output contains the specified number (``n``) of elements (or tags) with the specified XPath-like ``path`` (e.g. ``<has_n_elements_with_path n="9" path="BlastOutput_iterations/Iteration/Iteration_hits/Hit/Hit_num" />``).
``element_text_is`` | Asserts the text of the XML element with the specified XPath-like ``path`` is the specified ``text`` (e.g. ``<element_text_is path="BlastOutput_program" text="blastp" />``).
``element_text_matches`` | Asserts the text of the XML element with the specified XPath-like ``path`` matches the regular expression defined by ``expression`` (e.g. ``<element_text_matches path="BlastOutput_version" expression="BLASTP\s+2\.2.*" />``).
``attribute_is`` | Asserts the XML ``attribute`` for the element (or tag) with the specified XPath-like ``path`` is the specified ``text`` (e.g. ``<attribute_is path="outerElement/innerElement1" attribute="foo" text="bar" />`` ).
``attribute_matches`` | Asserts the XML ``attribute`` for the element (or tag) with the specified XPath-like ``path`` matches the regular expression specified by ``expression`` (e.g. ``<attribute_matches path="outerElement/innerElement2" attribute="foo2" expression="bar\d+" />``).
``element_text`` | This tag allows the developer to recurisively specify additional assertions as child elements about just the text contained in the element specified by the XPath-like ``path`` (e.g. ``<element_text path="BlastOutput_iterations/Iteration/Iteration_hits/Hit/Hit_def"><not_has_text text="EDK72998.1" /></element_text>``).







<a name="tool|tests|test|assert_stderr"></a>
## ``tool`` > ``tests`` > ``test`` > ``assert_stderr``
Describe assertions about the job's
standard error.


This tag set defines a sequence of checks or assertions to run against the
target output. This tag requires no attributes, but child tags should be used to
define the assertions to make about the output. The functional test framework
makes it easy to extend Galaxy with such tags, the following table summarizes
many of the default assertion tags that come with Galaxy and examples of each
can be found below.

The implementation of these tags are simply Python functions defined in the
[``galaxy.tools.verify.asserts``](https://github.com/galaxyproject/galaxy/tree/dev/lib/galaxy/tools/verify/asserts]
module.

      

Child Element/Assertion | Details 
--- | ---
``has_text`` | Asserts the specified ``text`` appears in the output (e.g. ``<has_text text="chr7">``).
``not_has_text`` | Asserts the specified ``text`` does not appear in the output (e.g. ``<not_has_text text="chr8" />``).
``has_text_matching`` | Asserts text matching the specified regular expression (``expression``) appears in the output (e.g. ``<has_text_matching expression="1274\d+53" />`` ).
``has_line`` | Asserts a line matching the specified string (``line``) appears in the output (e.g. ``<has_line line="A full example line." />``).
``has_line_matching`` | Asserts a line matching the specified regular expression (``expression``) appears in the output (e.g. ``<has_line_matching expression=".*\s+127489808\s+127494553" />``).
``has_n_columns`` | Asserts tabular output contains the specified number (``n``) of columns (e.g. ``<has_n_columns n="3" />``).
``is_valid_xml`` | Asserts the output is a valid XML file (e.g. ``<is_valid_xml />``).
``has_element_with_path`` | Asserts the XML output contains at least one element (or tag) with the specified XPath-like ``path`` (e.g. ``<has_element_with_path path="BlastOutput_param/Parameters/Parameters_matrix" />``).
``has_n_elements_with_path`` | Asserts the XML output contains the specified number (``n``) of elements (or tags) with the specified XPath-like ``path`` (e.g. ``<has_n_elements_with_path n="9" path="BlastOutput_iterations/Iteration/Iteration_hits/Hit/Hit_num" />``).
``element_text_is`` | Asserts the text of the XML element with the specified XPath-like ``path`` is the specified ``text`` (e.g. ``<element_text_is path="BlastOutput_program" text="blastp" />``).
``element_text_matches`` | Asserts the text of the XML element with the specified XPath-like ``path`` matches the regular expression defined by ``expression`` (e.g. ``<element_text_matches path="BlastOutput_version" expression="BLASTP\s+2\.2.*" />``).
``attribute_is`` | Asserts the XML ``attribute`` for the element (or tag) with the specified XPath-like ``path`` is the specified ``text`` (e.g. ``<attribute_is path="outerElement/innerElement1" attribute="foo" text="bar" />`` ).
``attribute_matches`` | Asserts the XML ``attribute`` for the element (or tag) with the specified XPath-like ``path`` matches the regular expression specified by ``expression`` (e.g. ``<attribute_matches path="outerElement/innerElement2" attribute="foo2" expression="bar\d+" />``).
``element_text`` | This tag allows the developer to recurisively specify additional assertions as child elements about just the text contained in the element specified by the XPath-like ``path`` (e.g. ``<element_text path="BlastOutput_iterations/Iteration/Iteration_hits/Hit/Hit_def"><not_has_text text="EDK72998.1" /></element_text>``).







<a name="tool|code"></a>
## ``tool`` > ``code``

**Deprecated** do not use this unless absolutely necessary.

This tag set provides detailed control of the way the tool is executed. This
(optional) code can be deployed in a separate file in the same directory as the
tool's config file. These hooks are being replaced by new tool config features
and methods in the ~/lib/galaxy/tools/__init__.py code file.

### Examples

#### Dynamic Options

Use associated dynamic select lists where selecting an option in the first
select list dynamically re-renders the options in the second select list. In
this example, we are populating both dynamic select lists from metadata elements
associated with a tool's single input dataset. The 2 metadata elements we're
using look like this.

```python
MetadataElement( name="field_names", default=[], desc="Field names", readonly=True, optional=True, visible=True, no_value=[] )
# The keys in the field_components map to the list of field_names in the above element
# which ensures order for select list options that are built from it.
MetadataElement( name="field_components", default={}, desc="Field names and components", readonly=True, optional=True, visible=True, no_value={} )
```

Our tool config includes a code file tag like this.

```xml
<code file="tool_form_utils.py" />
```

Here are the relevant input parameters in our tool config. The first parameter
is the input dataset that includes the above metadata elements.

```xml
<param name="input" type="data" format="vtkascii,vtkbinary" label="Shape with uncolored surface field">
    <validator type="expression" message="Shape must have an uncolored surface field.">value is not None and len(value.metadata.field_names) > 0</validator>
</param>
```

The following parameter dynamically renders a select list consisting of the
elements in the ``field_names`` metadata element associated with the selected
input dataset.

```xml
<param name="field_name" type="select" label="Field name" refresh_on_change="True">
    <options>
        <filter type="data_meta" ref="input" key="field_names"/>
        <validator type="no_options" message="The selected shape has no uncolored surface fields." />
    </options>
</param>
```

The following parameter calls the ``get_field_components_options()`` function in
the ``tool_form_utils.py`` code file discussed above. This function returns the
value of the input dataset's ``field_components`` metadata element dictionary
whose key is the currently selected ``field_name`` from the select list parameter
above.

```xml
<param name="field_component_index" type="select" label="Field component index" dynamic_options="get_field_components_options(input, field_name=field_name)" help="Color will be applied to the selected field's component associated with this index." />
```

Changing the selected option in the ``field_name`` select list will dynamically
re-render the options available in the associated ``field_component_index`` select
list, which is the behavior we want.

The ``get_field_components_options()`` method looks like this.

```python
def get_field_components_options( dataset, field_name ):
    options = []
    if dataset.metadata is None:
        return options
    if not hasattr( dataset.metadata, 'field_names' ):
        return options
    if dataset.metadata.field_names is None:
        return options
    if field_name is None:
        # The expression validator that helps populate the select list of input
        # datsets in the icqsol_color_surface_field tool does not filter out
        # datasets with no field field_names, so we need this check.
        if len( dataset.metadata.field_names ) == 0:
            return options
        field_name = dataset.metadata.field_names[0]
    field_components = dataset.metadata.field_components.get( field_name, [] )
    for i, field_component in enumerate( field_components ):
        options.append( ( field_component, field_component, i == 0 ) )
    return options
```




### Attributes
Attribute | Details | Required
--- | --- | ---
``file`` | This value is the name of the executable code file, and is called in the exec_before_process(), exec_before_job(), exec_after_process() and exec_after_job()( methods. | True




<a name="tool|requirements"></a>
## ``tool`` > ``requirements``


This is a container tag set for the ``requirement`` and ``container`` tags
described in greater detail below. ``requirement``s describe software packages
and other individual computing requirements required to execute a tool, while
``container``s describe Docker containers that should be able to serve as
complete descriptions of the runtime of a tool.







<a name="tool|requirements|requirement"></a>
## ``tool`` > ``requirements`` > ``requirement``


This tag set is contained within the ``requirements`` tag set. Third party
programs or modules that the tool depends upon are included in this tag set.

When a tool runs, Galaxy attempts to *resolve* these requirements (also called
dependencies). ``requirement``s are meant to be abstract and resolvable by
multiple different systems (e.g. [conda](http://conda.pydata.org/docs/), the
[Galaxy Tool Shed dependency management system](https://wiki.galaxyproject.org/ToolShedToolFeatures#Automatic_third-party_tool_dependency_installation_and_compilation_with_installed_repositories),
or [environment modules](http://modules.sourceforge.net/)).

Read more about dependency resolvers in Galaxy on
[docs.galaxyproject.org](https://docs.galaxyproject.org/en/master/admin/dependency_resolvers.html).
The current best practice for tool dependencies is to target Conda, this is
discussed in greater detail
[here](https://docs.galaxyproject.org/en/master/admin/conda_faq.html).

### Examples

This example shows a tool that requires the samtools 0.0.18 package.

This package is available via the Tool Shed (see
[Tool Shed dependency management](https://wiki.galaxyproject.org/ToolShedToolFeatures#Automatic_third-party_tool_dependency_installation_and_compilation_with_installed_repositories)
) as well as [Conda](https://docs.galaxyproject.org/en/master/admin/conda_faq.html)
and can be configured locally to adapt to any other package management system.

```xml
<requirements>
    <requirement type="package" version="0.1.18">samtools</requirement>
</requirements>
```

This older example shows a tool that requires R version 2.15.1. The
``tool_depensencies.xml`` should contain matching declarations for Galaxy to
actually install the R runtime. The ``set_envirornment`` type is only respected
by the tool shed and is ignored by the newer and preferred conda dependency
resolver.

```xml
<requirements>
    <requirement type="set_environment">R_SCRIPT_PATH</requirement>
    <requirement type="package" version="2.15.1">R</requirement>
</requirements>
```




### Attributes
Attribute | Details | Required
--- | --- | ---
``type`` | This value defines the which type of the 3rd party module required by this tool. | True
``version`` | For package type requirements this value defines a specific version of the tool dependency. | False




<a name="tool|requirements|container"></a>
## ``tool`` > ``requirements`` > ``container``


This tag set is contained within the 'requirements' tag set. Galaxy can be
configured to run tools within Docker (https://www.docker.com/) containers -
this tag allows the tool to suggest possible valid Docker containers for this
tool.

Read more about configuring Galaxy to run Docker jobs
[here](https://wiki.galaxyproject.org/Admin/Tools/Docker).




### Attributes
Attribute | Details | Required
--- | --- | ---
``type`` | This value describes the type of container that the tool may be executed in and currently must be 'docker'. | True




<a name="tool|stdio"></a>
## ``tool`` > ``stdio``
Tools write the bulk of useful data to datasets, but they can also write messages to standard I/O (stdio) channels known as standard output (stdout) and standard error (stderr). Both stdout and stderr are typically written to the executing program's console or terminal. Previous versions of Galaxy checked stderr for execution errors - if any text showed up on stderr, then the tool's execution was marked as failed. However, many tools write messages to stderr that are not errors, and using stderr allows programs to redirect other interesting messages to a separate file. Programs may also exit with codes that indicate success or failure. One convention is for programs to return 0 on success and a non-zero exit code on failure.

Legacy tools (ones with ``profile`` unspecified or a ``profile`` of less than
16.04) will default to checking stderr for errors as described above. Newer
tools will instead treat an exit code other than 0 as an error. The
``detect_error`` on ``command`` can swap between these behaviors but the
``stdio`` directive allows more options in defining error conditions (though
these aren't always intuitive).

With ``stdio`` directive, Galaxy can use regular expressions to scan stdout and
stderr, and it also allows exit codes to be scanned for ranges. The ``<stdio>``
tag has two subtags, ``<regex>`` and ``<exit_code>``, to define regular
expressions and exit code processing, respectively. They are defined below. If a
tool does not have any valid ``<regex>`` or ``<exit_code>`` tags, then Galaxy
will use the previous technique for finding errors.

A note should be made on the order in which exit codes and regular expressions
are applied and how the processing stops. Exit code rules are applied before
regular expression rules. The rationale is that exit codes are more clearly
defined and are easier to check computationally, so they are applied first. Exit
code rules are applied in the order in which they appear in the tool's
configuration file, and regular expressions are also applied in the order in
which they appear in the tool's configuration file. However, once a rule is
triggered that causes a fatal error, no further rules are
checked.





<a name="tool|stdio|exit_code"></a>
## ``tool`` > ``stdio`` > ``exit_code``

Tools may use exit codes to indicate specific execution errors. Many programs use 0 to indicate success and non-zero exit codes to indicate errors. Galaxy allows each tool to specify exit codes that indicate errors. Each <exit_code> tag defines a range of exit codes, and each range can be associated with a description of the error (e.g., "Out of Memory", "Invalid Sequence File") and an error level. The description just describes the condition and can be anything. The error level is either a warning or a fatal error. A warning means that stderr will be updated with the error's description. A fatal error means that the tool's execution will be marked as having an error and the workflow will stop. Note that, if the error level is not supplied, then a fatal error is assumed to have occurred.

The exit code's range can be any consecutive group of integers. More advanced ranges, such as noncontiguous ranges, are currently not supported. Ranges can be specified in the form "m:n", where m is the start integer and n is the end integer. If ":n" is specified, then the exit code will be compared against all integers less than or equal to n. If "m:" is used, then the exit code will be compared against all integers greater than or equal to m. If the exit code matches, then the error level is applied and the error's description is added to stderr. If a tool's exit code does not match any of the supplied <exit_code> tags' ranges, then no errors are applied to the tool's execution.

Note that most Unix and Linux variants only support positive integers 0 to 255 for exit codes. If an exit code falls out of the range 0 to 255, the usual convention is to only use the lower 8 bits for the exit code. The only known exception is if a job is broken into subtasks using the tasks runner and one of those tasks is stopped with a POSIX signal. (Note that signals should be used as a last resort for terminating processes.) In those cases, the task will receive -1 times the signal number. For example, suppose that a job uses the tasks runner and 8 tasks are created for the job. If one of the tasks hangs, then a sysadmin may choose to send the "kill" signal, SIGKILL, to the process. In that case, the task (and its job) will exit with an exit code of -9. More on POSIX signals can be found at http://en.wikipedia.org/wiki/Unix_signal as well as man pages on "signal".

The <exit_code> tag's supported attributes are as follows:

* ``range``: This indicates the range of exit codes to check. The range can be one of the following:
  * ``n``: the exit code will only be compared to n;
  * ``[m:n]``: the exit code must be greater than or equal to m and less than or equal to n;
  * ``[m:]``: the exit code must be greater than or equal to m;
  * ``[:n]``: the exit code must be less than or equal to n.
* ``level``: This indicates the error level of the exit code. The level can have one of two values:
  * ``warning``: If an exit code falls in the given range, then a description of the error will be added to the beginning of stderr. A warning-level error will not cause the tool to fail.
  * ``fatal``: If an exit code falls in the given range, then a description of the error will be added to the beginning of stderr. A fatal-level error will cause the tool to fail. If no level is specified, then the fatal error level will be assumed to have occurred.
* ``description``: This is an optional description of the error that corresponds to the exit code.

The following is an example of the <exit_code> tag:

```xml
<stdio>
    <exit_code range="2"   level="fatal"   description="Out of Memory" />
    <exit_code range="3:5" level="warning" description="Low disk space" />
    <exit_code range="6:"  level="fatal"   description="Bad input dataset" />
</stdio>
```

If the tool returns 0 or 1, then the tool will not be marked as having an error.
If the exit code is 2, then the tool will fail with the description ``Out of
Memory`` added to stderr. If the tool returns 3, 4, or 5, then the tool will not
be marked as having failed, but ``Low disk space`` will be added to stderr.
Finally, if the tool returns any number greater than or equal to 6, then the
description ``Bad input dataset`` will be added to stderr and the tool will be
marked as having failed.







<a name="tool|stdio|regex"></a>
## ``tool`` > ``stdio`` > ``regex``

A regular expression defines a pattern of characters. The patterns include the following:

* ``GCTA``, which matches on the fixed string "GCTA";
* ``[abcd]``, which matches on the characters a, b, c, or d;
* ``[CG]{12}``, which matches on 12 consecutive characters that are C or G;
* ``a.*z``, which matches on the character "a", followed by 0 or more characters of any type, followed by a "z";
* ``^X``, which matches the letter X at the beginning of a string;
* ``Y$``, which matches the letter Y at the end of a string.

There are many more possible regular expressions. A reference to all supported
regular expressions can be found under
[Python Regular Expression Syntax](https://docs.python.org/3/library/re.html#regular-expression-syntax).

A regular expression includes the following attributes:

* ``source``: This tells whether the regular expression should be matched against stdout, stderr, or both. If this attribute is missing or is incorrect, then both stdout and stderr will be checked. The source can be one of the follwing values:
  * ``stdout``: the regular expression will be applied to stdout;
  * ``stderr``: the regular expression will be applied to stderr;
  * ``both``: the regular expression will be applied to both stderr and stdout (which is the default case).
* ``match``: This is the regular expression that will be used to match against stdout and/or stderr. If the <regex> tag does not contain the match attribute, then the <regex> tag will be ignored. The regular expression can be any valid Python regular expression. All regular expressions are performed case insensitively. For example, if match contains the regular expression "actg", then the regular expression will match against "actg", "ACTG", "AcTg", and so on. Also note that, if double quotes (") are to be used in the match attribute, then the value " can be used in place of double quotes. Likewise, if single quotes (') are to be used in the match attribute, then the value ' can be used if necessary.
* ``level``: This works very similarly to the <exit_code> tag, except that, when a regular expression matches against its source, the description is added to the beginning of the source. For example, if stdout matches on a regular expression, then the regular expression's description is added to the beginning of stdout (instead of stderr). The level can be log, warning or fatal as described below.
 * ``log`` and ``warning``: If the regular expression matches against its source input (i.e., stdout and/or stderr), then a description of the error will be added to the beginning of the source, prepended with either 'Log:' or 'Warning:'. A log-level/warning-level error will not cause the tool to fail.
 * ``fatal``: If the regular expression matches against its source input, then a description of the error will be added to the beginning of the source. A fatal-level error will cause the tool to fail. If no level is specified, then the fatal error level will be assumed to have occurred.
* ``description``: Just like its ``exit_code`` counterpart, this is an optional description of the regular expression that has matched.

The following is an example of regular expressions that may be used:

```xml
<stdio>
    <regex match="low space"
           source="both"
           level="warning"
           description="Low space on device" />
    <regex match="error"
           source="stdout"
           level="fatal"
           description="Unknown error encountered" />
    <regex match="[CG]{12}"
           description="Fatal error - CG island 12 nts long found" />
    <regex match="^Branch A"
           level="warning"
           description="Branch A was taken in execution" />
</stdio>
```

The regular expression matching proceeds as follows. First, if either stdout or
stderr match on ``low space``, then a warning is registered. If stdout contained
the string ``---LOW SPACE---``, then stdout has the string ``Warning: Low space
on device`` added to its beginning. The same goes for if stderr had contained the
string ``low space``. Since only a warning could have occurred, the processing
continues.

Next, the regular expression ``error`` is matched only against stdout. If stdout
contains the string ``error`` regardless of its capitalization, then a fatal
error has occurred and the processing stops. In that case, stdout would be
prepended with the string ``Fatal: Unknown error encountered``. Note that, if
stderr contained ``error``, ``ERROR``, or ``ErRor`` then it would not matter -
stderr was not being scanned.

If the second regular expression did not match, then the third regular
expression is checked. The third regular expression does not contain an error
level, so an error level of ``fatal`` is assumed. The third regular expression
also does not contain a source, so both stdout and stderr are checked. The third
regular expression looks for 12 consecutive "C"s or "G"s in any order and in
uppercase or lowercase. If stdout contained ``cgccGGCCcGGcG`` or stderr
contained ``CCCCCCgggGGG``, then the regular expression would match, the tool
would be marked with a fatal error, and the stream that contained the
12-nucleotide CG island would be prepended with ``Fatal: Fatal error - CG island
12 nts long found``.

Finally, if the tool did not match any of the fatal errors, then the fourth
regular expression is checked. Since no source is specified, both stdout and
stderr are checked. If ``Branch A`` is at the beginning of stdout or stderr, then
a warning will be registered and the source that contained ``Branch A`` will be
prepended with the warning ``Warning: Branch A was taken in execution``.







<a name="tool|help"></a>
## ``tool`` > ``help``
This tag set includes all of the necessary details of how to use the tool. This tag set should be included as the next to the last tag set, before citations, in the tool config. Tool help is written in reStructuredText. Included here is only an overview of a subset of features. For more information see http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html.

tag | details
--- | -------
``.. class:: warningmark`` | a yellow warning symbol
``.. class:: infomark`` | a blue information symbol
``.. image:: path-of-the-file.png :height: 500 :width: 600`` | insert a png file of height 500 and width 600 at this position |
``**bold**`` | bold
``*italic*`` | italic
``*`` | list
``-`` | list
``::`` | paragraph
``-----`` | a horizontal line

### Examples

Show a warning sign to remind users that this tool accept fasta format files only, followed by an example of the query sequence and a figure.

```xml
<help>

.. class:: warningmark

'''TIP''' This tool requires *fasta* format.

----

'''Example'''

Query sequence::
    >seq1
    ATCG...

.. image:: my_figure.png
    :height: 500
    :width: 600

</help>
```



### Best Practices

Find the Intergalactic Utilities Commision suggested best practices for this
element [here](http://planemo.readthedocs.io/en/latest/standards/docs/best_practices/tool_xml.html#help-tag).





<a name="tool|citations"></a>
## ``tool`` > ``citations``
Tool files may declare one
citations element. Each citations element can contain one or more citation tag
elements - each of which specifies tool citation information using either a DOI
or a BibTeX entry.

These citations will appear at the bottom of the tool form in a formatted way
but the user will have to option to select RAW BibTeX for copying and pasting as
well. Likewise, the history menu includes an option allowing users to aggregate
all such citations across an analysis in a list of citations.

BibTeX entries for citations annotated with DOIs will be fetched by Galaxy from
http://dx.doi.org/ and cached.

```xml
<citations>
   <!-- Example of annotating a citation using a DOI. -->
   <citation type="doi">10.1093/bioinformatics/btq281</citation>

   <!-- Example of annotating a citation using a BibTex entry. -->
   <citation type="bibtex">@ARTICLE{Kim07aninterior-point,
   author = {Seung-jean Kim and Kwangmoo Koh and Michael Lustig and Stephen Boyd and Dimitry Gorinevsky},
   title = {An interior-point method for large-scale l1-regularized logistic regression},
   journal = {Journal of Machine Learning Research},
   year = {2007},
   volume = {8},
   pages = {1519-1555}
   }</citation>
 </citations>
```

For more implementation information see the
[pull request](https://bitbucket.org/galaxy/galaxy-central/pull-requests/440/initial-bibtex-doi-citation-support-in/diff)
adding this feature. For more examples of how to add this to tools checkout the
following commits adding this to the
[NCBI BLAST+ suite](https://github.com/peterjc/galaxy_blast/commit/9d2e3906915895765ecc3f48421b91fabf2ccd8b),
[phenotype association tools](https://bitbucket.org/galaxy/galaxy-central/commits/39c983151fe328ff5d415f6da81ce5b21a7e18a4),
[MAF suite](https://bitbucket.org/galaxy/galaxy-central/commits/60f63d6d4cb7b73286f3c747e8acaa475e4b6fa8),
and [MACS2 suite](https://github.com/jmchilton/galaxytools/commit/184971dea73e236f11e82b77adb5cab615b8391b).

This feature was added to the August 2014 release of Galaxy, tools annotated
with citations will work in older releases of Galaxy but no citation information
will be available to the end user.






<a name="tool|citations|citation"></a>
## ``tool`` > ``citations`` > ``citation``
Each citations element can contain one or
more ``citation`` tag elements - each of which specifies tool citation
information using either a DOI or a BibTeX entry.


### Attributes
Attribute | Details | Required
--- | --- | ---
``type`` | Type of citation - currently ``doi`` and ``bibtex`` are the only supported options. | True



