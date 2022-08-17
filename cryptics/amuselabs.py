import base64
import datetime
import json
import re
import requests
import sqlite3
import sys

from cryptics.config import SQLITE_DATABASE


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
    # The date The New Yorker published their first cryptic crossword.
    start_date = datetime.date(2021, 6, 27)
    sunday = start_date
    today = datetime.date.today()

    while sunday <= today:
        solver_url = f"https://www.newyorker.com/puzzles-and-games-dept/cryptic-crossword/{sunday.strftime('%Y/%m/%d')}"
        with sqlite3.connect(SQLITE_DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT EXISTS(SELECT 1 FROM raw WHERE location = '{solver_url}')"
            )
            scraped = bool(cursor.fetchone()[0])

        if scraped:
            sunday = sunday + datetime.timedelta(days=7)
            continue

        print(f"Requesting {solver_url}")

        # Get rawc
        solver_response = requests.get(solver_url)
        cdn_url = re.search(
            f"https?://\w*\.amuselabs\.com/[^ ]+embed=1", solver_response.text
        ).group()
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
            r'var e=function\(e\)\{var t="(.*?)"', js_response.content.decode("utf-8")
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
                "INSERT INTO raw (source, location, content_type, content) VALUES ('new_yorker', ?, 'json', ?)",
                (solver_url, json.dumps(puz_json)),
            )
            conn.commit()

        sunday = sunday + datetime.timedelta(days=7)
