#!/bin/bash

set -eu -o pipefail

START_DATE='2021/06/27'  # The date The New Yorker published the first cryptic crossword.
TODAY=$(date +%Y/%m/%d)

sunday=${START_DATE}
while [[ "${sunday}" < "${TODAY}" ]]; do
    url="https://www.newyorker.com/puzzles-and-games-dept/cryptic-crossword/${sunday}"

    scraped=$(sqlite3 cryptics.sqlite3 "SELECT EXISTS(SELECT 1 FROM json WHERE url = '${url}')")
    if [[ ${scraped} -ne 0 ]]; then
        sunday=$(date +%Y/%m/%d -d "${sunday} + 7 days")
        continue
    fi

    echo "Requesting ${url}"
    json=$(
        curl -s ${url} \
            | rg -o "https?://\w*.amuselabs.com/[^ ]+embed=1" \
            | head -n 1 \
            | xargs curl -s \
            | rg -o "rawc\s*=\s*'([^']+)'" -r '$1' \
            | base64 --decode
    )
    sqlite3 cryptics.sqlite3 "INSERT INTO json (source, url, json)
        VALUES ('new_yorker', '${url}', '${json}')"

    sunday=$(date +%Y/%m/%d -d "${sunday} + 7 days")
done
