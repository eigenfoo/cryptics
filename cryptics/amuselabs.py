import base64
import json
import logging
import re
import requests
import sqlite3

from cryptics.config import SQLITE_DATABASE, AMUSELABS_SOURCES
from cryptics.utils import get_logger


# Taken from https://github.com/thisisparker/xword-dl/commit/3927a378e35666f09fff96f091d2f97584b9256e
def load_rawc(rawc, amuseKey=None):
    try:
        # the original case is just base64'd JSON
        return json.loads(base64.b64decode(rawc).decode("utf-8"))
    except:
        try:
            # case 2 is the first obfuscation
            E = rawc.split(".")
            A = list(E[0])
            H = E[1][::-1]
            F = [int(A, 16) + 2 for A in H]
            B, G = 0, 0
            while B < len(A) - 1:
                C = min(F[G % len(F)], len(A) - B)
                for D in range(C // 2):
                    A[B + D], A[B + C - D - 1] = A[B + C - D - 1], A[B + D]
                B += C
                G += 1
            newRawc = "".join(A)
            return json.loads(base64.b64decode(newRawc).decode("utf-8"))
        except:
            # case 3 is the most recent obfuscation
            def amuse_b64(e, amuseKey=None):
                e = list(e)
                H = amuseKey
                E = []
                F = 0
                while F < len(H):
                    J = H[F]
                    K = int(J, 16)
                    E.append(K)
                    F += 1
                A, G, I = 0, 0, len(e) - 1
                while A < I:
                    B = E[G]
                    B += 2
                    L = I - A + 1
                    C = A
                    B = min(B, L)
                    D = A + B - 1
                    while C < D:
                        M = e[D]
                        e[D] = e[C]
                        e[C] = M
                        D -= 1
                        C += 1
                    A += B
                    G = (G + 1) % len(E)
                return "".join(e)

            return json.loads(
                base64.b64decode(amuse_b64(rawc, amuseKey)).decode("utf-8")
            )


if __name__ == "__main__":
    logger = get_logger()

    for source, url_generator in AMUSELABS_SOURCES.items():
        for url in url_generator():
            # Skip URL if already scraped
            with sqlite3.connect(SQLITE_DATABASE) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    f"SELECT EXISTS(SELECT 1 FROM raw WHERE location = '{url}')"
                )
                if bool(cursor.fetchone()[0]):
                    continue

            logger.info(f"Requesting: {url}")

            # Get rawc
            solver_response = requests.get(url)
            try:
                cdn_url = re.search(
                    f"https?://\w*\.amuselabs\.com/[^ ]+embed=1", solver_response.text
                ).group()
            except AttributeError:
                logger.warning(
                    f"This URL appears to be AmuseLabs CDN URL, not a webpage with an AmuseLabs embed: {url}"
                )
                cdn_url = url
            cdn_response = requests.get(cdn_url)
            rawc = re.search(f"rawc\s*=\s*'([^']+)'", cdn_response.text).group(1)

            # Get the "key" from the JavaScript
            js_url = re.search(
                r'"([^"]+c-min.js[^"]+)"', cdn_response.content.decode("utf-8")
            ).groups()[0]
            base_url = "/".join(cdn_url.split("/")[:-1])
            js_url = base_url + "/" + js_url
            js_response = requests.get(js_url)
            matches = re.search(
                r'var e=function\(e\)\{var t="(.*?)"',
                js_response.content.decode("utf-8"),
            )
            amuseKey = None
            if matches is not None:
                amuseKey = matches.groups()[0]
                if amuseKey == "1":
                    amuseKey = None

            puz_json = load_rawc(rawc, amuseKey=amuseKey)

            with sqlite3.connect(SQLITE_DATABASE) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO raw (source, location, content_type, content) VALUES (?, ?, 'json', ?)",
                    (source, url, json.dumps(puz_json)),
                )
                conn.commit()
