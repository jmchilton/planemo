

TOOL_TEMPLATE = """<tool id="{{id}}" name="{{name}}" version="{{version}}">
{%- if description %}
    <description>{{ description }}</description>
{% endif %}
    <macros>
        <import>cwl_macros.xml</import>
        <token name="@CWL_TOOL_FILE@">{{ tool_file }}</token>
    </macros>
    <expand macro="cwl_requirements">
{%- for container in containers %}
        {{ container }}
{%- endfor %}
    </expand>
    <expand macro="cwl_runtime" />
    <inputs>
{%- for input in inputs %}
        {{ input }}
{%- endfor %}
    </inputs>
    <outputs>
{%- for output in outputs %}
        {{ output }}
{%- endfor %}
    </outputs>
    <configfiles>
        <configfile name="job_description">
{%- for input in inputs %}
            {{ input }}
{%- endfor %}
        </configfile>
    </configfiles>
    <help><![CDATA[
        {{ help }}
    ]]></help>
    </citations>
</tool>
"""

MACROS_TEMPLATE = """<macros>
    <xml name="cwl_requirements">
        <requirements>
            <yield/>
        </requirements>
    </xml>
    <xml name="cwl_stdio">
        <stdio>
            <exit_code range="1:" />
        </stdio>
    </xml>
    <xml name="cwl_command">
        <command><![CDATA[
            cwltool "$__tool_directory__/@CWL_TOOL_FILE@" "${job_description}"
        ]]></command>
    </xml>
    <xml name="cwl_runtime">
        <expand macro="cwl_stdio" />
        <expand macro="cwl_command" />
    </xml>
    <xml name="job_description">
        <configfiles>
            <configfile name="job_description">
                <yield />
            </configfile>
        </configfiles>
    </xml>
</macros>
"""
