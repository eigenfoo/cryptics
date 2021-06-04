import datetime
import json
import random
import time
import traceback

import bs4
import requests
from cryptic_info.parse import try_parse


headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)",
    "Accept-Encoding": "gzip",
}

with open("metadata.json", "r") as f:
    metadata = json.load(f)


while metadata["unindexed_urls"]:
    url = metadata["unindexed_urls"].pop()
    print(url)

    response = requests.get(url, headers=headers)
    soup = bs4.BeautifulSoup(response.text, features="lxml")
    print("Requested response")

    data = None
    try:
        data = try_parse(response, url)
    except Exception:
        print(traceback.format_exc())
    if data is None:
        print("Failed to parse")
        metadata["errored_urls"].append(url)
    else:
        print("Successfully parsed")
        with open("data.jsonl", "a+") as f:
            data.to_json(f, lines=True, orient="records")
            print("\n", file=f)
        metadata["indexed_urls"].append(url)

    metadata["last_run"] = (
        datetime.datetime.now().astimezone(datetime.timezone.utc).strftime("%c %Z")
    )
    with open("metadata.json", "w") as f:
        json.dump(metadata, f)
    print("Wrote metadata")

    print("Sleeping...")
    sleep_time = random.uniform(20, 40)
    # time.sleep(sleep_time)
    print(f"Slept for {sleep_time:.2f}s")
    print(78 * "=")
