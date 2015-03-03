import copy
import os

import jsonschema
from cwltool.ref_resolver import from_url
from cwltool.flatten import flatten

from cwltool import (
    draft1tool,
    draft2tool,
)

from planemo import io
import sys

DRAFT1 = "draft1"
DRAFT2 = "draft2"


def convert(ctx, stream, path, draft, **kwds):
    tool_class = _tool_class(draft)
    try:
        t = tool_class(from_url(path))
    except jsonschema.exceptions.ValidationError:
        io.error("Tool definition failed validation")
        sys.exit(2)

    if 'outputs' not in t.tool:
        io.error("Must have an outputs section")
        sys.exit(3)

    stream.write("<?xml version=\"1.0\"?>\n")
    stream.write("<tool id=\"%s\" name=\"%s\">\n" % (os.path.basename(path), os.path.basename(path)))

    docker_identifier = _docker_identifier(t.tool, draft)
    if docker_identifier:
        stream.write("  <requirements>\n")
        stream.write("      <container type=\"docker\">%s</container>\n" % docker_identifier)
        stream.write("  </requirements>\n")

    stream.write("  <inputs>\n")

    def handle_param(k, v, indent):
        if v['type'] == 'array':
            stream.write(indent + "<repeat name=\"%s\">\n" % k)
            if 'type' in v['items']:
                if v['items']['type'] == 'object' and not ('_type' in v['items'] and v['items']['_type'] == 'file'):
                    for k1, v1 in v['items']['properties'].items():
                        handle_param(k1, v1, indent + "  ")
                else:
                    handle_param("item", v['items'], indent + "  ")
            stream.write(indent + "</repeat>\n")
        else:
            stream.write(indent + "<param ")
            stream.write("name=\"%s\" " % k)
            stream.write("type=\"")
            if v['type'] == 'integer':
                stream.write("integer")
            elif v['type'] == 'number':
                stream.write("float")
            elif v['type'] == 'string':
                stream.write("text")
            elif v['type'] == 'boolean':
                stream.write("boolean")
            elif v['type'] == 'file' or ('_type' in v and v['_type'] == 'file'):
                stream.write("data")
            stream.write("\" ")
            stream.write("/>\n")

    for k, v in t.tool['inputs']['properties'].items():
        handle_param(k, v, "    ")

    stream.write("  </inputs>\n")

    stream.write("  <outputs>\n")
    for k, v in t.tool['outputs']['properties'].items():
        stream.write("    <data ")
        stream.write("name=\"%s\" " % k)
        stream.write("format=\"%s\" " % "text")
        if 'adapter' in v and 'glob' in v['adapter']:
            if 'stdout' in t.tool['adapter'] and t.tool['adapter']['stdout'] == v['adapter']['glob']:
                stdout_param = k
            else:
                stream.write("from_work_dir=\"%s\" " % v['adapter']['glob'])
        stream.write("/>\n")

    stream.write("  </outputs>\n")

    adapter = t.tool["adapter"]
    adapters = [{
        "order": [-1000000],
        "value": adapter['baseCmd']
    }]

    stream.write("  <command>")

    def adapt(k, v):
        if 'adapter' in v:
            va = v['adapter']
            effective_prefix = _effective_prefix(va)
            if v['type'] == 'array':
                if 'itemSeparator' in va:
                    val = "%s#for $i, $v in enumerate(${%s})##if $i!=0#%s#end if#$v#endfor#" % (effective_prefix, k, va["itemSeparator"])
                else:
                    val = "#for $v in ${%s}# \"%s$v\" #end for#" % (k, effective_prefix)
                adapters.append({"order": [va['order']] if 'order' in va else [10000000],
                                "value": val})
            else:
                adapters.append({"order": [va['order']] if 'order' in va else [10000000],
                                "value": "%s${%s}" % (effective_prefix, k)})

    if "args" in adapter:
        for i, arg in enumerate(adapter["args"]):
            arg = copy.copy(arg)
            if "order" in arg:
                arg["order"] = [arg["order"]]
            else:
                arg["order"] = [1000000]
            galaxy_value = _adapter_to_galaxy_value(arg)
            arg["value"] = galaxy_value
            adapters.append(arg)

    for k, v in t.tool['inputs']['properties'].items():
        adapt(k, v)

    adapters.sort(key=lambda a: a["order"])

    for f in flatten([a["value"] for a in adapters]):
        stream.write(f)
        stream.write(" ")

    if stdout_param:
        stream.write("&gt; ${%s}" % stdout_param)
    stream.write("</command>\n")

    stream.write("</tool>\n")


def _adapter_to_galaxy_value(adapter):
    f = adapter["value"]
    if isinstance(f, dict):
        if "$job" in f:
            io.error("ERROR: $job not supported yet")
            sys.exit(1)
        if "$expr" in f:
            if f["$expr"].strip() == "$job.allocatedResources.cpu":
                raw_value = "\$GALAXY_SLOTS"
            else:
                io.error("ERROR: Generic $expr not supported")
                sys.exit(1)
    else:
        raw_value = f
    return "%s%s" % (_effective_prefix(adapter), raw_value)


def _effective_prefix(adapter):
    p = adapter['prefix'] if 'prefix' in adapter else ''
    s = adapter['separator'] if 'separator' in adapter else ''
    return "%s%s" % (p, s)


def _tool_class(draft):
    if draft == DRAFT1:
        return draft1tool.Tool
    elif draft == DRAFT2:
        return draft2tool.Tool
    else:
        raise Exception("Unknown CWL draft %s" % draft)


def _docker_identifier(tool, draft):
    if draft == DRAFT1:
        requirements = tool.get("requirements", {})
        environment = requirements.get("environment", {})
        container = environment.get("container", {})
        container_type = container.get("type", "docker")
        if container_type != "docker":
            return None
        else:
            return container.get("uri", None)
    elif draft == DRAFT2:
        hints = tool.get("hints", [])
        for hint in hints:
            if hint.get("requirementType", None) == "DockerImage":
                if "dockerImageId" in hint:
                    return "%s:%s" % (hint["dockerPull"], hint["dockerImageId"])
                else:
                    return hint["dockerPull"]
        return None
    else:
        raise Exception("Unknown CWL draft %s" % draft)
