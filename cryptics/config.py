import os
import json


PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SITEMAPS_JSON = os.path.join(PROJECT_DIR, "sitemaps.json")
SQLITE_DATABASE = os.path.join(PROJECT_DIR, "cryptics.sqlite3")

with open(SITEMAPS_JSON, "r") as f:
    SITEMAPS = json.load(f)
