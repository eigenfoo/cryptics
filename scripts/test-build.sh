#!/bin/bash
set -euf -o pipefail

# Don't output anything during this script run
exec > /dev/null

function test_path {
  if ! datasette . --get $1
  then
    echo "Test failed on $1" >&2
    exit 1
  fi
}

test_path "/"
test_path "/datasheet"
