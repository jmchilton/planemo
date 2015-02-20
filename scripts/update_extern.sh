#!/bin/bash

PLANEMO_SCRIPTS_DIR=`dirname $0`
PLANEMO_ROOT="$PLANEMO_SCRIPTS_DIR/.."

cd "$PLANEMO_ROOT"

for file in 'rgToolFactory2.xml' 'rgToolFactory2.py' 'getlocalrpackages.py' 'LICENSE';
do
    wget "https://raw.githubusercontent.com/galaxyproject/tools-iuc/master/tools/tool_factory_2/$file"  --output-document "extern/tool_factory_2/$file"
done

for file in 'galaxy.xsd' 'citations.xsd' 'citation.xsd' 'LICENSE';
do
    wget "https://raw.githubusercontent.com/JeanFred/Galaxy-XSD/master/$file" --output-document "extern/xsd/$file"
done
