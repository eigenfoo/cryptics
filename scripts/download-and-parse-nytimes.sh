#!/bin/bash
# Look up XWordInfo's directory of variety puzzles, download cryptic crosswords
# using xword-dl, and parse them. You may need to authenticate xword-dl; see
# https://github.com/thisisparker/xword-dl#new-york-times-authentication

set -euf pipefail

curl https://www.xwordinfo.com/SelectVariety \
    | rg '<td class="cryptic">' \
    | rg -o "https://www.nytimes.com/crosswords/game/variety/[\d/]+" \
    | xargs --max-lines=1 xword-dl

mkdir nytimes/
find . -name '*.puz' -exec mv -t nytimes/ {} +

python cryptics/puzzes.py --puz-glob="nytimes/*" --source="nytimes"

rm -rf nytimes/
