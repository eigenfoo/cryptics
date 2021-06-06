import datetime
import json
import re

import requests
import bs4


SITEMAP_URL = "https://www.fifteensquared.net/wp-sitemap.xml"

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)",
    "Accept-Encoding": "gzip",
}


with open("metadata.json") as f:
    metadata = json.load(f)

known_urls = set(
    metadata["unindexed_urls"] + metadata["indexed_urls"] + metadata["errored_urls"]
)

response = requests.get(SITEMAP_URL, headers=headers)
soup = bs4.BeautifulSoup(response.text, "lxml")

# DONE: 8, 9 and 10
sitemaps = list(
    reversed(
        [
            sitemap.text
            for sitemap in soup.find_all("sitemap")
            if re.search(
                r"https://www.fifteensquared.net/wp-sitemap-posts-post-(8|9|10).xml",
                sitemap.text,
            )
        ]
    )
)

for sitemap in sitemaps:
    response = requests.get(sitemap, headers=headers)
    soup = bs4.BeautifulSoup(response.text, "lxml")
    urls = {url.text for url in soup.find_all("url")}
    new_urls = urls - known_urls
    metadata["unindexed_urls"].extend(list(new_urls))

with open("metadata.new.json", "w+") as f:
    json.dump(metadata, f)
