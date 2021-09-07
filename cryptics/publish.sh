#!/bin/bash

set -e

rm -rf clues.sqlite3
sqlite3 cryptics.sqlite3 ".dump clues" | sqlite3 clues.sqlite3
sqlite3 clues.sqlite3 ".read queries/scrub.sql"
