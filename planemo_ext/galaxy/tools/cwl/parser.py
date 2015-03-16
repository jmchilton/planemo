try:
    from cwltool import (
        ref_resolver,
        draft1tool,
        draft2tool,
    )
except ImportError:
    ref_resolver = None
    draft1tool = None
    draft2tool = None

from galaxy.util.bunch import Bunch


def build_inputs(tool_path):
    tool = to_cwl_tool_object(tool_path)
    return tool.inputs()


def to_cwl_tool_object(tool_path):
    if ref_resolver is None:
        raise Exception("Using CWL tools requires cwltool module.")
    toolpath_object = ref_resolver.from_url(tool_path)
    if "schema" in toolpath_object:
        return ToolDraft1Proxy(draft1tool.Tool(toolpath_object))
    if "class" in toolpath_object:
        if toolpath_object["class"] == "CommandLineTool":
            return ToolDraft2Proxy(draft2tool.CommandLineTool(toolpath_object))
    raise Exception("Unsupported CWL object encountered.")


class ToolDraft1Proxy(object):

    def __init__(self, tool):
        self._tool = tool

    def input_instances(self):
        return self._tool.tool["inputs"]


class ToolDraft2Proxy(object):

    def __init__(self, tool):
        self._tool = tool

    def input_instances(self):
        return self._tool.inputs_record_schema

    def _find_inputs(self, schema):
        if isinstance(schema["type"], list):
            raise Exception("Union types not yet implemented.")
        elif isinstance(schema["type"], dict):
            return self._find_inputs(schema["type"])
        else:
            if schema["type"] in self._tool.schemaDefs:
                schema = self._tool.schemaDefs[schema["type"]]

            if schema["type"] == "record":
                return map(_simple_field_to_input(schema["fields"]))


def _simple_field_to_input(field):
    pass


INPUT_TYPE = Bunch(
    DATA="DATA",
)


class InputInstance(object):

    def __init__(self, name, input_type):
        self.input_type = input_type
        self.name = name
        self.required = True
