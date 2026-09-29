#!/usr/bin/env python3
"""Rewrites the weather block of README.md from the public anchors of
kvantixtech/weather-forecast-test. Runs daily in GitHub Actions. Standard library only.
Nothing is estimated: if there is no anchor yet, the static text stays."""
import csv, io, os, re, sys, urllib.request
from datetime import date, datetime, timezone

ANCHORS = "https://raw.githubusercontent.com/kvantixtech/weather-forecast-test/main/anchors/chain-heads.csv"
REPO = "https://github.com/kvantixtech/weather-forecast-test"
START = date(2026, 9, 28)          # first forecast collected 28 Sep 2026, 12:08 UTC
SCOREBOARD_DAY = 30                # first scoreboard after ~30 days
README = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "README.md")
BLOCK = re.compile(r"(<!-- weather:start -->\n)(.*?)(\n<!-- weather:end -->)", re.S)


def fetch_rows(url=ANCHORS):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "kvantixtech-profile"}), timeout=30) as r:
        return list(csv.DictReader(io.StringIO(r.read().decode("utf-8"))))


def render(rows, today=None):
    today = today or datetime.now(timezone.utc).date()
    day = (today - START).days + 1
    head = ("**Which weather forecast is right most often in Denmark?** DMI, MET Norway, OpenWeatherMap and the "
            "pilots' TAF for five Danish cities, locked four times a day before the weather happens.")
    if not rows:
        return None
    last = rows[-1]
    state = "intact" if last["chain_ok"] == "true" else "**BROKEN, see the anchors**"
    board = (f"First scoreboard in about {SCOREBOARD_DAY - day} days." if day < SCOREBOARD_DAY
             else "Scoreboard: [kvantix.tech/playground](https://kvantix.tech/playground/).")
    return (f"{head}\n\n"
            f"| Day | Downloads locked | Chain | Latest public anchor |\n|---|---|---|---|\n"
            f"| **{day}** | {int(last['runs']):,} | {state} | [`{last['chain_head'][:16]}…`]({REPO}/blob/main/anchors/chain-heads.csv) · {last['date_utc']} |\n\n"
            f"{board} Rules published 28 Sep 2026 at 07:57 UTC, four hours before the first forecast.")


def main():
    try:
        rows = fetch_rows()
    except Exception as e:  # network trouble: keep the README as it is
        print("could not fetch anchors:", e)
        return 0
    body = render(rows)
    if body is None:
        print("no anchors yet; README unchanged")
        return 0
    text = open(README, encoding="utf-8").read()
    new = BLOCK.sub(lambda m: m.group(1) + body + m.group(3), text)
    if new == text:
        print("README unchanged")
        return 0
    open(README, "w", encoding="utf-8", newline="\n").write(new)
    print("README updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
