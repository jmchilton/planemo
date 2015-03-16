import os

from planemo import cli

from galaxy.tools.cwl import parser

TESTS_DIRECTORY = os.path.dirname(__file__)
CWL_TOOLS_DIRECTORY = os.path.join(TESTS_DIRECTORY, "cwl_tools")


def test_load():
    print parser.build_inputs(_cwl_tool_path("draft1/cat1-tool.json"))
    print parser.build_inputs(_cwl_tool_path("draft2/cat1-tool.cwl"))
    assert False


def _cwl_tool_path(path):
    return os.path.join(CWL_TOOLS_DIRECTORY, path)
