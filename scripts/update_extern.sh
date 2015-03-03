#!/bin/bash

set -e

PLANEMO_SCRIPTS_DIR=`dirname $0`
PLANEMO_ROOT="$PLANEMO_SCRIPTS_DIR/.."

EXTERN_DIR="$PLANEMO_ROOT/planemo_ext"
cd "$PLANEMO_ROOT"

# Update CWL external code.
CWL_PATH="$EXTERN_DIR/cwltool"
rm -rf /tmp/cwl
git clone -b draft-2-pa git@github.com:common-workflow-language/common-workflow-language.git /tmp/cwl
rm -rf $CWL_PATH
cp -r "/tmp/cwl/reference/cwltool" "$CWL_PATH"
rm -rf "$CWL_PATH/schemas"
cp -r "/tmp/cwl/schemas" "$CWL_PATH"
cp -r "/tmp/cwl/LICENSE.txt" "$CWL_PATH"
cp -r "/tmp/cwl/LICENSE.txt" "$CWL_PATH"

# TODO: ideally I would bring in CWL reference implementation via PIP.

# Update tool factory external code.
TOOL_FACTORY_PATH="$EXTERN_DIR/tool_factory_2"
mkdir -p $TOOL_FACTORY_PATH
for file in 'rgToolFactory2.xml' 'rgToolFactory2.py' 'getlocalrpackages.py' 'LICENSE';
do
    wget "https://raw.githubusercontent.com/galaxyproject/tools-iuc/master/tools/tool_factory_2/$file"  --output-document "$TOOL_FACTORY_PATH/$file"
done
