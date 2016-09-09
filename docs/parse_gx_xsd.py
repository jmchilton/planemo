# coding: utf-8
# TODO: Add examples, tables and best practice links to command
# TODO: Examples of truevalue, falsevalue
# TODO: Move documentation of multiple outputs into here or into planemo docs,
#       include a better, more updated link.

# TODO: Document repeat, conditional, and section in test param section as well
#       as metadata, extra_file, and discovered_dataset.


"""
Checklist to Transplant:

Transfered | Improved

[X][X] ``tool``
[X][X] ``tool`` > ``description``
[X][X] ``tool`` > ``version_command``
[X][X] ``tool`` > ``command``
[X][X] ``tool`` > ``inputs``
[X][X] ``tool`` > ``inputs`` > ``section``
[X][X] ``tool`` > ``inputs`` > ``repeat``
[X][X] ``tool`` > ``inputs`` > ``conditional``
[X][X] ``tool`` > ``inputs`` > ``conditional`` > ``when``
[X][X] ``tool`` > ``inputs`` > ``param``
[X][X] ``tool`` > ``inputs`` > ``param`` > ``validator``
[X][X] ``tool`` > ``inputs`` > ``param`` > ``option``
[X][X] ``tool`` > ``inputs`` > ``param`` > ``options``
[X][X] ``tool`` > ``inputs`` > ``param`` > ``options`` > ``column``
[X][X] ``tool`` > ``inputs`` > ``param`` > ``options`` > ``filter``
[X][X] ``tool`` > ``inputs`` > ``param`` > ``sanitizer``
[X][X] ``tool`` > ``inputs`` > ``param`` > ``sanitizer`` > ``valid``
[X][X] ``tool`` > ``inputs`` > ``param`` > ``sanitizer`` > ``valid`` > ``add``
[X][X] ``tool`` > ``inputs`` > ``param`` > ``sanitizer`` > ``valid`` > ``remove``
[X][X] ``tool`` > ``inputs`` > ``param`` > ``sanitizer`` > ``mapping``
[X][X] ``tool`` > ``inputs`` > ``param`` > ``sanitizer`` > ``mapping`` > ``add``
[X][X] ``tool`` > ``inputs`` > ``param`` > ``sanitizer`` > ``mapping`` > ``remove``
[X][X] ``tool`` > ``configfiles``
[X][X] ``tool`` > ``configfiles`` > ``configfile``
[X][X] *NEW* ``tool`` > ``configfiles`` > ``inputs``
[X][X] *NEW* ``tool`` > ``environment_variables``
[X][X] *NEW* ``tool`` > ``environment_variables`` > ``environment_variable``
[X][X] ``tool`` > ``outputs``
[X][X] ``tool`` > ``outputs`` > ``data``
[X][X] ``tool`` > ``outputs`` > ``data`` > ``filter``
[X][X] ``tool`` > ``outputs`` > ``data`` > ``change_format``
[X][X] ``tool`` > ``outputs`` > ``data`` > ``change_format`` >> ``when``
[X][ ] ``tool`` > ``outputs`` > ``data`` > ``discover_datasets``
[X][X] ``tool`` > ``outputs`` > ``data`` > ``actions``
[X][X] *NEW* ``tool`` > ``outputs`` > ``data`` > ``actions`` > ``conditional``
[X][X] *NEW* ``tool`` > ``outputs`` > ``data`` > ``actions`` > ``conditional`` > ``when``
[X][X] *NEW* ``tool`` > ``outputs`` > ``data`` > ``actions`` > ``action``
[X][X] *NEW* ``tool`` > ``outputs`` > ``collection``
[X][X] *NEW* ``tool`` > ``outputs`` > ``collection`` > ``filter``
[X][ ] *NEW* ``tool`` > ``outputs`` > ``collection`` > ``discover_datasets``
[X][X] ``tool`` > ``tests``
[X][X] ``tool`` > ``tests`` > ``test``
[X][ ] ``tool`` > ``tests`` > ``test`` > ``param``
[X][X] *NEW* ``tool`` > ``tests`` > ``test`` > ``repeat``
[X][X] *NEW* ``tool`` > ``tests`` > ``test`` > ``section``
[X][X] *NEW* ``tool`` > ``tests`` > ``test`` > ``conditional``
[X][ ] ``tool`` > ``tests`` > ``test`` > ``output``
[X][ ] *NEW* ``tool`` > ``tests`` > ``test`` > ``output`` > ``discover_dataset``
[X][ ] *NEW* ``tool`` > ``tests`` > ``test`` > ``output`` > ``metadata``
[X][X] ``tool`` > ``tests`` > ``test`` > ``assert_contents``
[X][X] *NEW* ``tool`` > ``tests`` > ``test`` > ``output_collection``
[X][X] *NEW* ``tool`` > ``tests`` > ``test`` > ``assert_stdout``
[X][X] *NEW* ``tool`` > ``tests`` > ``test`` > ``assert_stderr``
[X][X] *NEW* ``tool`` > ``tests`` > ``test`` > ``assert_command``
[X][X] ``tool`` > ``code``
[X][X] ``tool`` > ``requirements``
[X][X] ``tool`` > ``requirements`` > ``requirement``
[X][X] *NEW* ``tool`` > ``requirements`` > ``container``
[X][X] ``tool`` > ``stdio``
[X][X] ``tool`` > ``stdio`` > ``exit_code``
[X][X] ``tool`` > ``stdio`` > ``regex``
[X][X] ``tool`` > ``help``
[X][X] ``tool`` > ``citations``
[X][X] ``tool`` > ``citations`` > ``citation``
"""


from __future__ import print_function

# Things dropped from TOC (still documented inside schema).
#  - some stuff at the top of the tool xml document
#  - interpreter
#  - request_parameter_translation


from lxml import etree
from StringIO import StringIO


with open("docs/schema_template.md", "r") as f:
    MARKDOWN_TEMPLATE = f.read()

with open("planemo/xml/xsd/tool/galaxy.xsd", "r") as f:
    xmlschema_doc = etree.parse(f)

markdown_buffer = StringIO()


def main():
    """Entry point for the function that builds Markdown help for the Galaxy XSD."""
    for line in MARKDOWN_TEMPLATE.splitlines():
        if line.startswith("$tag:"):
            print(Tag(line).build_help())
        elif line.startswith("$toc"):
            print_toc()
        else:
            print(line)


def print_toc():
    tags = []
    for line in MARKDOWN_TEMPLATE.splitlines():
        if line.startswith("$tag:"):
            tags.append(Tag(line))

    for i, tag in enumerate(tags):
        try:
            next_tag = tags[i+1]
            next_count = next_tag.title.count("|")
        except IndexError:
            next_tag = None
            next_count = None
        line = ""
        count = tag.title.count("|")
        for c in range(count):
            if next_count is not None and c < next_count:
                if c == 0:
                    line += "├──"
                else:
                    line += "┼──"
            else:
                if c == 0:
                    line += "└──"
                else:
                    line += "┴──"
        line += "[``<" + tag.title.split("|")[-1] + ">``](#" + tag.title + ")  "
        print(line)


class Tag(object):

    def __init__(self, line):
        assert line.startswith("$tag:")
        line_parts = line.split(" ")
        first_part = line_parts[0]
        hide_attributes = False
        if len(line_parts) > 1:
            if "hide_attributes" in line_parts[1]:
                hide_attributes = True
        _, title, xpath = first_part.split(":")
        xpath = xpath.replace("/element", "/{http://www.w3.org/2001/XMLSchema}element")
        xpath = xpath.replace("/group", "/{http://www.w3.org/2001/XMLSchema}group")
        xpath = xpath.replace("/complexType", "/{http://www.w3.org/2001/XMLSchema}complexType")
        self.xpath = xpath
        self.hide_attributes = hide_attributes
        self.title = title

    def build_help(self):
        tag = xmlschema_doc.find(self.xpath)
        if tag is None:
            raise Exception("Could not find xpath for %s" % self.xpath)

        title = self.title
        tag_help = StringIO()
        tag_help.write("""\n<a name="%s"></a>\n""" % title)
        tag_help.write("## " + " > ".join(["``%s``" % p for p in title.split("|")]))
        tag_help.write("\n")
        tag_help.write(_build_tag(tag, self.hide_attributes))
        tag_help.write("\n\n")
        return tag_help.getvalue()


def _build_tag(tag, hide_attributes):
    tag_el = _find_tag_el(tag)
    attributes = _find_attributes(tag)
    tag_help = StringIO()
    annotation_el = tag_el.find("{http://www.w3.org/2001/XMLSchema}annotation")
    text = annotation_el.find("{http://www.w3.org/2001/XMLSchema}documentation").text
    for line in text.splitlines():
        if line.startswith("$attribute_list:"):
            attributes_str = line.split(":", 1)[1]
            attribute_names = attributes_str.split(",")
            text = text.replace(line, _build_attributes_table(tag, attributes, attribute_names=attribute_names))
        if line.startswith("$assertions"):
            assertions_tag = xmlschema_doc.find("//{http://www.w3.org/2001/XMLSchema}complexType[@name='TestAssertions']")
            assertion_tag = xmlschema_doc.find("//{http://www.w3.org/2001/XMLSchema}group[@name='TestAssertion']")
            assertions_buffer = StringIO()
            assertions_buffer.write(_doc_or_none(assertions_tag))
            assertions_buffer.write("\n\n")
            assertions_buffer.write("Child Element/Assertion | Details \n")
            assertions_buffer.write("--- | ---\n")
            elements = assertion_tag.findall("{http://www.w3.org/2001/XMLSchema}choice/{http://www.w3.org/2001/XMLSchema}element")
            for element in elements:
                doc = _doc_or_none(element).strip()
                assertions_buffer.write("``%s`` | %s\n" % (element.attrib["name"], doc))
            text = text.replace(line, assertions_buffer.getvalue())
    tag_help.write(text)
    best_practices = _get_bp_link(annotation_el)
    if best_practices:
        tag_help.write("\n\n### Best Practices\n")
        tag_help.write("""
Find the Intergalactic Utilities Commision suggested best practices for this
element [here](%s).""" % best_practices)
    tag_help.write(_build_attributes_table(tag, attributes, hide_attributes))

    return tag_help.getvalue()


def _get_bp_link(annotation_el):
    anchor = annotation_el.attrib.get("{http://galaxyproject.org/xml/1.0}best_practices", None)
    link = None
    if anchor:
        link = "http://planemo.readthedocs.io/en/latest/standards/docs/best_practices/tool_xml.html#%s" % anchor
    return link


def _build_attributes_table(tag, attributes, hide_attributes=False, attribute_names=None):
    attribute_table = StringIO()
    attribute_table.write("\n\n")
    if attributes and not hide_attributes:
        attribute_table.write("\n### Attributes\n")
        attribute_table.write("Attribute | Details | Required\n")
        attribute_table.write("--- | --- | ---\n")
        for attribute in attributes:
            name = attribute.attrib["name"]
            if attribute_names and name not in attribute_names:
                continue
            details = _doc_or_none(attribute)
            if details is None:
                type_el = _type_el(attribute)
                details = _doc_or_none(type_el)
                annotation_el = type_el.find("{http://www.w3.org/2001/XMLSchema}annotation")
            else:
                annotation_el = attribute.find("{http://www.w3.org/2001/XMLSchema}annotation")

            use = attribute.attrib.get("use", "optional") == "required"
            if "|" in details:
                raise Exception("Cannot build Markdown table")
            details = details.replace("\n", " ").strip()
            best_practices = _get_bp_link(annotation_el)
            if best_practices:
                details += """ Find the Intergalactic Utilities Commision suggested best practices for this element [here](%s).""" % best_practices

            attribute_table.write("``%s`` | %s | %s\n" % (name, details, use))
    return attribute_table.getvalue()


def _find_attributes(tag):
    return tag.findall("{http://www.w3.org/2001/XMLSchema}attribute") or \
        tag.findall("{http://www.w3.org/2001/XMLSchema}complexType/{http://www.w3.org/2001/XMLSchema}attribute") or \
        tag.findall("{http://www.w3.org/2001/XMLSchema}complexContent/{http://www.w3.org/2001/XMLSchema}extension/{http://www.w3.org/2001/XMLSchema}attribute") or \
        tag.findall("{http://www.w3.org/2001/XMLSchema}simpleContent/{http://www.w3.org/2001/XMLSchema}extension/{http://www.w3.org/2001/XMLSchema}attribute")


def _find_tag_el(tag):
    if _doc_or_none(tag) is not None:
        return tag

    return _type_el(tag)


def _type_el(tag):
    element_type = tag.attrib["type"]
    type_el = xmlschema_doc.find("//{http://www.w3.org/2001/XMLSchema}complexType/[@name='%s']" % element_type) or \
        xmlschema_doc.find("//{http://www.w3.org/2001/XMLSchema}simpleType/[@name='%s']" % element_type)
    return type_el


def _doc_or_none(tag):
    doc_el = tag.find("{http://www.w3.org/2001/XMLSchema}annotation/{http://www.w3.org/2001/XMLSchema}documentation")
    if doc_el is None:
        return None
    else:
        return doc_el.text

if __name__ == '__main__':
    main()
