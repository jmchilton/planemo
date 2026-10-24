"""Unit tests for the ShedVersion check's comparison against the published tool."""

from planemo.shed_lint import _same_tool

TOOL = '<tool id="cat" name="Cat" version="1.0"><command>cat $input &gt; $output</command></tool>'


def test_same_tool_ignores_formatting_whitespace():
    reformatted = '<tool id="cat" name="Cat" version="1.0">\n    <command>cat $input &gt; $output</command>\n</tool>\n'
    assert _same_tool(TOOL, reformatted)


def test_same_tool_detects_a_change():
    assert not _same_tool(TOOL, TOOL.replace("cat $input", "cat -n $input"))


def test_same_tool_treats_unparseable_source_as_changed():
    assert not _same_tool(TOOL, "<html>not a tool")
    assert not _same_tool("<tool", TOOL)
