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


def build_inputs(tool_path):
    tool = to_cwl_tool_object(tool_path)
    return tool


def to_cwl_tool_object(tool_path):
    if ref_resolver is None:
        raise Exception("Using CWL tools requires cwltool module.")
    toolpath_object = ref_resolver.from_url(tool_path)
    if "schema" in toolpath_object:
        return draft1tool.Tool(toolpath_object)
    if "class" in toolpath_object:
        if toolpath_object["class"] == "CommandLineTool":
            return draft2tool.CommandLineTool(toolpath_object)
    raise Exception("Unsupported CWL object encountered.")
