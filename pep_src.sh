#!/bin/bash

BASE_DIR="src/compiler/"

if [ -z "$1" ]; then
    echo "Usage: $0 <file-name>"
    exit 1
fi

FILE="$BASE_DIR$1"

if [ -f "$FILE" ]; then
    echo "Running autopep8 on $FILE..."
    autopep8 --in-place --aggressive --aggressive "$FILE"
else
    echo "File $FILE not found!"
    exit 1
fi
