#!/usr/bin/env python3
"""Builds pulse/pulse.json: what each Kvantix investigation is doing right now.
The live view on kvantix.tech/playground/ (and the strips on each experiment page) read this one file.

Reads only public sources:
  - commits on the main branch of the public kvantixtech repositories,
  - their GitHub Actions runs (watchdogs, live-site checks, the ERA5 job),
  - the status files the collectors commit themselves (anchors/chain-heads.csv, data/status.json).

It never contains results or raw measurements. The feed says THAT something happened, with a link
to the commit or run where anyone can check it. Standard library only. Runs hourly in GitHub Actions;
the file is committed only when something in it changed.
"""
import csv
import datetime as dt
import io
import json
import os
import re
import statistics
import sys
import time
import urllib.error
import urllib.request

OWNER = "kvantixtech"
SITE = "https://kvantix.tech/playground/"
FEED_DAYS = 14
FEED_MAX = 90
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pulse", "pulse.json")
BOT = "github-actions[bot]"

# Each investigation is a cell in the organism. "beat_h" is how often its heartbeat is due; the page
# turns the cell amber when a beat is 1.5x late and red at 3x. None = no heartbeat expected (resting).
NODES = [
    {"id": "weather", "name": "Weather forecasts", "short": "Weather",
     "question": "Which weather forecast is right most often?", "url": SITE + "weather/",
     "repo": "weather-forecast-test", "state": "collecting", "since": "2026-09-28", "beat_h": 24,
     "line": "DMI, MET Norway, OpenWeatherMap and the pilots' TAF, locked 4× a day before the weather happens",
     "next": {"what": "First scoreboard, marked preliminary", "date": "2026-10-28", "approx": True}},
    {"id": "co2", "name": "Energinet's CO₂ forecast", "short": "CO₂ forecast",
     "question": "Does the green hour hold?", "url": SITE + "energy/",
     "repo": "energinet-forecasts", "state": "collecting", "since": "2026-09-30", "beat_h": 24,
     "line": "Every hourly CO₂ forecast saved before it is overwritten",
     "next": {"what": "First green-hour tally, marked preliminary", "date": "2026-10-30", "approx": True}},
    {"id": "prices", "name": "Electricity price list", "short": "Price list",
     "question": "Tariffs and tax, saved before they change", "url": SITE + "energy/",
     "repo": "energy-price-archive", "state": "collecting", "since": "2026-09-30", "beat_h": 24,
     "line": "Every grid tariff and the electricity tax, checked daily and logged when they change", "next": None},
    {"id": "windgrid", "name": "Energinet's wind and solar forecasts", "short": "Wind & solar",
     "question": "How good are the wind and solar forecasts?", "url": SITE + "energy/",
     "repo": "energinet-forecasts", "state": "waiting", "since": "2026-09-29", "beat_h": None,
     "line": "Scored for 2019–2026. Energinet has until 14 October to reply before anything is shown",
     "next": {"what": "Results may be published (right of reply ends)", "date": "2026-10-14", "approx": False}},
    {"id": "windrain", "name": "Offshore wind and coastal rain", "short": "Wind & rain",
     "question": "Do offshore wind farms take the rain from the coast?", "url": SITE + "wind-rain/",
     "repo": "offshore-wind-rain", "state": "working", "since": "2026-10-02", "beat_h": 6,
     "line": "35 years of rain gauges against every offshore turbine, method locked before the data", "next": None},
    {"id": "experts", "name": "Economic forecasts", "short": "Experts",
     "question": "Did the experts get it right?", "url": SITE + "experts/",
     "repo": "expert-forecasts", "state": "watching", "since": "2026-09-29", "beat_h": 24 * 7,
     "line": "Scored. The live page is checked weekly and the outcomes monthly against Statistics Denmark",
     "next": {"what": "New edition with the 2026 outcomes", "date": "2027-03-02", "approx": False}},
    {"id": "wastewater", "name": "Denmark's wastewater", "short": "Wastewater",
     "question": "Where does Denmark's wastewater go?", "url": SITE + "wastewater/",
     "repo": "wastewater-denmark", "state": "watching", "since": "2026-10-01", "beat_h": 24 * 31,
     "line": "Published. The sources are downloaded again every month and compared", "next": None, "drift_day": 6},
    {"id": "nitrogen", "name": "Nitrogen sources", "short": "Nitrogen",
     "question": "Can open data show farming's share of the nitrogen?", "url": SITE + "nitrogen/",
     "repo": "nitrogen-sources-denmark", "state": "resting", "since": "2026-10-01", "beat_h": None,
     "line": "Finished. Method locked before the first value; the reading is published", "next": None},
    {"id": "tools", "name": "Tools in your browser", "short": "Tools",
     "question": "Luck or skill · Lock your prediction · Track record", "url": SITE + "#kvx-pg-lab",
     "repo": "lock-your-prediction", "state": "watching", "since": "2026-09-28", "beat_h": 24,
     "line": "They run in your browser and store nothing. The served files are checked daily against the code", "next": None},
]

# Real relations only: shared data or the same question seen from two sides.
EDGES = [
    ["windrain", "windgrid", "offshore wind"],
    ["co2", "windgrid", "Energinet data"],
    ["co2", "prices", "electricity"],
    ["nitrogen", "wastewater", "point sources"],
    ["weather", "windrain", "DMI data"],
]

# Scheduled checks that leave no commit: their runs are the heartbeat.
WORKFLOWS = [
    ("weather-forecast-test", "watchdog.yml", "weather", "Watchdog: anchor, chain and code version checked", "Watchdog alarm: see the run"),
    ("energinet-forecasts", "watchdog.yml", "co2", "Watchdog: anchor and chain checked", "Watchdog alarm: see the run"),
    ("energy-price-archive", "watchdog.yml", "prices", "Watchdog: anchor and chain checked", "Watchdog alarm: see the run"),
    ("offshore-wind-rain", "era5.yml", "windrain", "Weather-model run finished after {dur}", "Weather-model run stopped with an error after {dur}"),
    ("expert-forecasts", "live-site.yml", "experts", "Live page compared with the repository", "Live page differs from the repository"),
    ("wastewater-denmark", "drift.yml", "wastewater", "Monthly check: sources downloaded again and compared", "Monthly check failed: see the run"),
    ("lock-your-prediction", "live-site.yml", "tools", "Served sealing script compared byte for byte with the code", "Served script differs from the code"),
    ("kvantix-reports", "live-site.yml", "tools", "Published reports compared byte for byte with the live files", "Live reports differ from the repository"),
]
REPO_NODE = {"weather-forecast-test": "weather", "energinet-forecasts": "co2", "energy-price-archive": "prices",
             "offshore-wind-rain": "windrain", "expert-forecasts": "experts", "wastewater-denmark": "wastewater",
             "nitrogen-sources-denmark": "nitrogen", "lock-your-prediction": "tools", "kvantix-reports": "tools",
             "validation-examples": "tools"}
ANCHOR = re.compile(r"^anchor (\d{4}-\d{2}-\d{2}): chain head ([0-9a-f]+) \(run (\d+), (\d+) runs, chain_ok=(true|false)\)")
SEAL_TEXT = {"weather": "forecast downloads", "co2": "CO₂ forecasts", "prices": "price-list checks"}


# ------------------------------------------------------------------------------------------- fetching
def _get(url, accept="application/vnd.github+json"):
    hdr = {"User-Agent": "kvantixtech-pulse", "Accept": accept}
    tok = os.environ.get("GITHUB_TOKEN")
    if tok and "api.github.com" in url:
        hdr["Authorization"] = "Bearer " + tok
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=hdr), timeout=30) as r:
                return r.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            if e.code in (404, 410):
                return None
            if attempt == 2:
                raise
        except OSError:
            if attempt == 2:
                raise
        time.sleep(3 * (attempt + 1))


def api(path):
    t = _get("https://api.github.com" + path)
    return json.loads(t) if t else None


def raw(repo, path):
    return _get(f"https://raw.githubusercontent.com/{OWNER}/{repo}/main/{path}", accept="*/*")


# --------------------------------------------------------------------------------------------- helpers
def utc(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(dt.timezone.utc)


def iso(t):
    return t.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def dur(a, b):
    m = max(1, round((b - a).total_seconds() / 60))
    return f"{m} min" if m < 90 else f"{m // 60} h {m % 60:02d} min"


def day_no(node, date_str):
    return (dt.date.fromisoformat(date_str) - dt.date.fromisoformat(node["since"])).days + 1


def ev(t, node, kind, text, url):
    return {"t": iso(t), "node": node, "kind": kind, "text": text, "url": url}


# ------------------------------------------------------------------------------------------- the feed
def commit_events(repo, since, nodes):
    out, page = [], 1
    while page <= 3:
        cs = api(f"/repos/{OWNER}/{repo}/commits?sha=main&since={iso(since)}&per_page=100&page={page}") or []
        for c in cs:
            msg = (c["commit"]["message"] or "").split("\n")[0].strip()
            who = c["commit"]["author"]["name"]
            t = utc(c["commit"]["committer"]["date"])
            url = c["html_url"]
            node = REPO_NODE.get(repo)
            if not node or msg.startswith("Merge "):
                continue
            m = ANCHOR.match(msg)
            if m:
                d, head, run, runs, ok = m.groups()
                n = nodes[node]
                out.append(ev(t, node, "seal" if ok == "true" else "alarm",
                              f"Day {day_no(n, d)} sealed: {int(runs):,} {SEAL_TEXT.get(node, 'downloads')} locked, chain "
                              + ("intact" if ok == "true" else "BROKEN"), url))
                continue
            if repo == "offshore-wind-rain":
                if msg.startswith("status ("):
                    continue
                if msg.startswith("era5: day windows"):
                    det = api(f"/repos/{OWNER}/{repo}/commits/{c['sha']}") or {}
                    yrs = sorted(int(x.group(1)) for f in det.get("files", [])
                                 if f.get("status") == "added" and (x := re.search(r"data/era5/gauge_days_(\d{4})\.csv\.xz$", f["filename"])))
                    if yrs:
                        out.append(ev(t, node, "data", "Weather model: " + ", ".join(map(str, yrs))
                                      + " reduced to the gauges' days (no rain-gauge value read)", url))
                    else:
                        out.append(ev(t, node, "log", "Weather-model run logged; a year is closed once the next one is in", url))
                    continue
            if repo == "expert-forecasts" and msg.startswith("drift: checked"):
                out.append(ev(t, node, "check", "Outcomes compared again with Statistics Denmark (monthly drift check)", url))
                continue
            if repo in ("energinet-forecasts",) and re.search(r"\b(part A|wind|solar)\b", msg, re.I):
                node = "windgrid"
            out.append(ev(t, node, "data" if who == BOT else "commit", msg, url))
        if len(cs) < 100:
            break
        page += 1
    return out


def run_events(since):
    out, active, era5_minutes = [], {}, []
    for repo, wf, node, ok_text, bad_text in WORKFLOWS:
        js = api(f"/repos/{OWNER}/{repo}/actions/workflows/{wf}/runs?per_page=30") or {}
        for r in js.get("workflow_runs", []):
            start = utc(r.get("run_started_at") or r["created_at"])
            if wf == "era5.yml" and r["status"] in ("in_progress", "completed") and utc(r["updated_at"]) >= since:
                # a run can wait hours in the concurrency queue: time the job itself
                jobs = (api(f"/repos/{OWNER}/{repo}/actions/runs/{r['id']}/jobs") or {}).get("jobs") or []
                if jobs and jobs[0].get("started_at"):
                    start = utc(jobs[0]["started_at"])
            if r["status"] == "in_progress":
                if node not in active or start < utc(active[node]["since"]):
                    active[node] = {"since": iso(start), "what": "Fetching the weather model (ERA5)" if wf == "era5.yml" else "Running a check",
                                    "url": r["html_url"]}
                continue
            if r["status"] != "completed" or r["conclusion"] not in ("success", "failure", "timed_out"):
                continue
            end = utc(r["updated_at"])
            if end < since:
                continue
            minutes = (end - start).total_seconds() / 60
            if wf == "era5.yml":
                if minutes < 3:          # idle hourly runs once every year is in
                    continue
                if r["conclusion"] == "success" and minutes > 30:
                    era5_minutes.append(minutes)
            good = r["conclusion"] == "success"
            out.append(ev(end, node, "check" if good else "alarm",
                          (ok_text if good else bad_text).format(dur=dur(start, end)), r["html_url"]))
    return out, active, era5_minutes


# ------------------------------------------------------------------------------------- node details
def last_anchor(repo):
    t = raw(repo, "anchors/chain-heads.csv")
    rows = [r for r in csv.DictReader(io.StringIO(t or "")) if re.fullmatch(r"[0-9a-f]{64}", r.get("chain_head", ""))]
    return rows[-2:] if rows else []


def next_monthly(day, now):
    y, m = now.year, now.month
    cand = dt.datetime(y, m, day, 7, tzinfo=dt.timezone.utc)
    if cand <= now:
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
        cand = dt.datetime(y, m, day, 7, tzinfo=dt.timezone.utc)
    return cand.date().isoformat()


def build(now=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    since = now - dt.timedelta(days=FEED_DAYS)
    nodes = {n["id"]: json.loads(json.dumps(n)) for n in NODES}
    feed = []
    for repo in sorted(set(REPO_NODE)):
        feed += commit_events(repo, since, nodes)
    rfeed, active, era5_minutes = run_events(since)
    feed += rfeed
    feed.sort(key=lambda e: e["t"], reverse=True)

    # anchors: counters, metabolism and chain state
    for nid in ("weather", "co2", "prices"):
        n = nodes[nid]
        rows = last_anchor(n["repo"])
        if not rows:
            continue
        a = rows[-1]
        runs = int(a["runs"])
        n["chain_ok"] = a["chain_ok"] == "true"
        n["counters"] = [[SEAL_TEXT[nid] + " locked", f"{runs:,}"], ["day", str(day_no(n, a["date_utc"]))]]
        if len(rows) == 2:
            n["rate"] = {"per_day": max(0, runs - int(rows[0]["runs"])), "unit": SEAL_TEXT[nid] + " a day"}
        n["anchor"] = {"date": a["date_utc"], "at": a["anchored_at_utc"], "head": a["chain_head"][:12]}

    # wind and rain: the test's own status file
    w = nodes["windrain"]
    try:
        st = json.loads(raw("offshore-wind-rain", "data/status.json") or "{}")
    except ValueError:
        st = {}
    e5 = st.get("era5", {})
    steps = st.get("steps", [])
    done = sum(1 for s in steps if s.get("status") == "done")
    w["counters"] = [["ERA5 years in", f"{e5.get('years_done', 0)} of {e5.get('years_total', 35)}"],
                     ["steps done", f"{done} of {len(steps) or 8}"],
                     ["rain-gauge values read", "1991–2001 only" if st.get("rain_values_read") else "0"]]
    now_step = next((s for s in steps if s.get("status") != "done"), None)
    if now_step:
        w["step"] = now_step.get("step")
    left = e5.get("years_total", 35) - e5.get("years_done", 0)
    if left > 0:
        per_year_h = (statistics.median(era5_minutes) / 60) if era5_minutes else 4.3
        eta = (now + dt.timedelta(hours=left * per_year_h + 2)).date()
        w["next"] = {"what": "Weather model complete for 1991–2025 (estimate at the current pace)", "date": eta.isoformat(), "approx": True}
        if era5_minutes:
            w["rate"] = {"per_day": round(24 / per_year_h, 1), "unit": "ERA5 years a day"}
    else:
        w["state"] = "working" if not any(s.get("key") == "result" and s.get("status") == "done" for s in steps) else "watching"
        w["next"] = {"what": "Power check on 1991–2001, before the farms", "date": None, "approx": True}

    # finished projects: published facts from their own repos
    try:
        ex = json.loads(raw("expert-forecasts", "results/results.json") or "{}")
        nodes["experts"]["counters"] = [["forecasts scored", str(len(ex.get("forecasts", [])))], ["checked against", "Statistics Denmark"]]
    except ValueError:
        pass
    try:
        nr = json.loads(raw("nitrogen-sources-denmark", "results/results.json") or "{}")
        nodes["nitrogen"]["counters"] = [["reading", str(nr.get("primary", {}).get("reading", "–"))], ["stations", str(nr.get("included", "–"))]]
    except ValueError:
        pass
    nodes["wastewater"]["next"] = {"what": "Next monthly check against the sources", "date": next_monthly(6, now), "approx": False}
    try:
        ww = json.loads(raw("wastewater-denmark", "results/site.json") or "{}")
        nodes["wastewater"]["counters"] = [["municipalities", str(len(ww.get("munis", [])))], ["checked", "monthly"]]
    except ValueError:
        pass
    nodes["tools"]["counters"] = [["tools", "3"], ["stored", "nothing"]]
    nodes["windgrid"]["counters"] = [["years scored", "2019–2026"], ["shown from", "14 Oct"]]

    # heartbeat = latest automatic event (seal, data, check, log, alarm) per cell; active runs
    for e in feed:
        n = nodes.get(e["node"])
        if n is not None and e["kind"] != "commit" and "beat" not in n:
            n["beat"] = e["t"]
        if n is not None and "touched" not in n:
            n["touched"] = e["t"]
    for n in nodes.values():
        n.setdefault("beat", n.get("touched"))
    for nid, a in active.items():
        nodes[nid]["active"] = a

    feed = feed[:FEED_MAX]
    milestones = sorted(({"node": n["id"], **n["next"]} for n in nodes.values() if n.get("next") and n["next"].get("date")),
                        key=lambda m: m["date"])
    return {
        "schema": 1,
        "about": "Kvantix pulse: what each investigation is doing, from public commits, runs and status files. "
                 "No results and no raw measurements. Built by tools/pulse.py in github.com/kvantixtech/kvantixtech.",
        "built_utc": iso(now),
        "nodes": list(nodes.values()),
        "edges": EDGES,
        "milestones": milestones,
        "feed": feed,
    }


def main():
    out = build()
    try:
        prev = json.load(open(OUT, encoding="utf-8"))
    except (OSError, ValueError):
        prev = None
    if prev and {k: v for k, v in prev.items() if k != "built_utc"} == {k: v for k, v in out.items() if k != "built_utc"}:
        print("pulse unchanged")
        return 0
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"pulse: {len(out['feed'])} events, {sum(1 for n in out['nodes'] if n.get('active'))} active runs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
