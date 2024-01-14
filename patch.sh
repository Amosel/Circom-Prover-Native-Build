#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

for i in $SCRIPT_DIR/patches/*.patch; do
    echo "Applying patch $i"
    git apply patch <$i
done
