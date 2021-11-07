#!/bin/bash

set -eu -o pipefail

cd ~/cryptics
source venv/bin/activate
git pull origin main
make update deploy
