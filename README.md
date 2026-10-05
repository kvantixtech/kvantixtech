<p align="center"><a href="https://kvantix.tech"><img src="assets/banner.png" alt="Kvantix: independent signal and forecast validation. Does your signal actually work?" width="100%"></a></p>

**Independent validation of trading signals and forecasts.** Seven statistical tests on your own data, and a written verdict from a person. We ran them on our own crypto engine first, in public. It failed.

The same method now runs in the open on everyday questions: weather forecasts, Energinet's data, offshore wind and rain, official economic forecasts, wastewater and nitrogen. Every collector, check and test commits its traces here, and **[kvantix.tech/playground](https://kvantix.tech/playground/)** shows them live.

Everything here follows one method:

1. **Lock it before the outcome.** A prediction or a method that can be edited afterwards proves nothing.
2. **Measure it honestly.** Every call counts, the misses too, against real outcomes and data nobody controls.
3. **Beat a dumb baseline.** "Tomorrow will be like today" is surprisingly hard to beat.

## In public right now

<!-- pulse:start -->
Every investigation, as of its latest public trace. This block is rewritten by [`tools/pulse.py`](tools/pulse.py) from the commits and Actions runs of the repositories below, the same data as the live view at **[kvantix.tech/playground](https://kvantix.tech/playground/)**. No results appear here before their test is finished and checked.

| Investigation | State | Last heartbeat | Where it stands | Next |
|---|---|---|---|---|
| [Weather forecasts](https://kvantix.tech/playground/weather/) | 🟢 Collecting | 5 Oct 16:20 UTC | 554 forecast downloads locked · 8 days running | First scoreboard, marked preliminary, ≈ 28 Oct |
| [Energinet's CO₂ forecast](https://kvantix.tech/playground/energy/) | 🟢 Collecting | 5 Oct 16:21 UTC | 136 CO₂ forecasts locked · 6 days running | First green-hour tally, marked preliminary, ≈ 30 Oct |
| [Electricity price list](https://kvantix.tech/playground/energy/) | 🟢 Collecting | 5 Oct 14:28 UTC | 12 price-list checks locked · 6 days running | – |
| [Energinet's wind and solar forecasts](https://kvantix.tech/playground/energy/) | 🔒 Waiting | 5 Oct 16:25 UTC | 2019–2026 scored · shown from 14 October at the earliest | Results may be published (right of reply ends), 14 Oct |
| [Offshore wind and coastal rain](https://kvantix.tech/playground/wind-rain/) | 🟡 Working | 5 Oct 12:27 UTC | 1 of 35 ERA5 years in · 4 of 8 steps done · now: fetching the weather model (ERA5) | – |
| [Economic forecasts](https://kvantix.tech/playground/experts/) | ⚪ Watching | 5 Oct 12:42 UTC | 60 forecasts scored · outcomes from Statistics Denmark | New edition with the 2026 outcomes, 2 Mar 2027 |
| [Denmark's wastewater](https://kvantix.tech/playground/wastewater/) | ⚪ Watching | 1 Oct 16:30 UTC | 98 municipalities and Christiansø · sources checked again every month | Next monthly check against the sources, 6 Oct |
| [Nitrogen sources](https://kvantix.tech/playground/nitrogen/) | 💤 Resting | – | Inconclusive reading · 46 stations | – |
| [Tools in your browser](https://kvantix.tech/playground/#kvx-pg-tools) | ⚪ Watching | 5 Oct 12:34 UTC | 3 tools · nothing you type is stored | – |

**Latest traces**

- 5 Oct 16:25 UTC · Wind & solar · [Coverage diagnostic for offshore wind: monthly forecast/outcome ratio, both outcomes (CHANGELOG #11)](https://github.com/kvantixtech/energinet-forecasts/commit/37f4e6303d1784bee8b10cf028f4c80cc40a37cd)
- 5 Oct 16:21 UTC · CO₂ forecast · [Watchdog: anchor and chain checked](https://github.com/kvantixtech/energinet-forecasts/actions/runs/37340144071)
- 5 Oct 16:20 UTC · Weather · [Watchdog: anchor, chain and code version checked](https://github.com/kvantixtech/weather-forecast-test/actions/runs/37340054632)
- 5 Oct 15:40 UTC · Wind & solar · [Score offshore wind also against parks >=100 MW (CHANGELOG #7); first scores unchanged](https://github.com/kvantixtech/energinet-forecasts/commit/d99a3a9ff154f025520a07db27a3f7a08061eb27)
- 5 Oct 15:31 UTC · CO₂ forecast · [CHANGELOG #7-10: Energinet's reply; offshore also scored against parks >=100 MW (before that scoring is run)](https://github.com/kvantixtech/energinet-forecasts/commit/bd2c0f8b2fae38c002e59a4e936804dd2c046ee6)
- 5 Oct 15:26 UTC · Nitrogen · [CHANGELOG: rule for the rerun with DCE's station catchments (fixed before the rerun)](https://github.com/kvantixtech/nitrogen-sources-denmark/commit/69048e77a41a95f49fa61a39212bc9c583fa0ad1)
<!-- pulse:end -->

## Repositories

**Collecting and testing now**

| | |
|---|---|
| 🌦️ [**weather-forecast-test**](https://github.com/kvantixtech/weather-forecast-test) | Which weather forecast is right most often in Denmark? DMI, MET Norway, OpenWeatherMap and the pilots' TAF for five cities, locked four times a day before the weather happens. Hash-chained and anchored on GitHub every day. |
| ⚡ [**energinet-forecasts**](https://github.com/kvantixtech/energinet-forecasts) | How good are Energinet's wind and solar forecasts, and does the green hour hold? Wind and solar scored against settled production, method committed before any data. Every hourly CO₂ forecast is saved and hash-chained before it is overwritten. |
| 🧾 [**energy-price-archive**](https://github.com/kvantixtech/energy-price-archive) | Denmark's published electricity price list, every grid tariff and the electricity tax, archived daily and hash-chained, so corrections and removals can be checked later. |
| 🌊 [**offshore-wind-rain**](https://github.com/kvantixtech/offshore-wind-rain) | Do offshore wind farms take the rain from the coast? 35 years of Danish and German rain gauges against every offshore turbine, method committed before any rain value is read. Plus a test of the new west-coast farms, rerun every year to 2029. |

**Finished checks, still watched**

| | |
|---|---|
| 📈 [**expert-forecasts**](https://github.com/kvantixtech/expert-forecasts) | Did Denmark's official forecasters get GDP and inflation right? 60 forecasts from 2015–2024, each quoted from its report, scored against Statistics Denmark and "next year like this year". Checked monthly for revisions. |
| 🚰 [**wastewater-denmark**](https://github.com/kvantixtech/wastewater-denmark) | Where Denmark's wastewater goes: treatment plants, sewer overflows and rainwater outlets in every municipality, from the national data. Only 36 of 4,195 overflows report measured flow and concentrations. |
| 🌾 [**nitrogen-sources-denmark**](https://github.com/kvantixtech/nitrogen-sources-denmark) | Can open data show farming's share of the nitrogen in Danish streams? 46 stations with measured flow, method committed before the first value. Reading: Inconclusive. |

**Tools and evidence**

| | |
|---|---|
| 🔒 [**lock-your-prediction**](https://github.com/kvantixtech/lock-your-prediction) | Seal a prediction with SHA-256 and a secret key. Spec, test vectors, and verifiers in Python, Node, the browser and plain `sha256sum`. |
| 🧪 [**validation-examples**](https://github.com/kvantixtech/validation-examples) | Six synthetic datasets where the truth is known, from a real-but-untradeable edge to a look-ahead bug that passes 7/7. Each has its full report. |
| 📄 [**kvantix-reports**](https://github.com/kvantixtech/kvantix-reports) | The reports on our own engine, unedited: KAS v1 **1/7**, KAS v2.1 **2/7**. |
| 🫀 [**kvantixtech**](https://github.com/kvantixtech/kvantixtech) (this page) | The pulse: [`tools/pulse.py`](tools/pulse.py) reads the public commits and runs of every repository above twice an hour and writes [`pulse/pulse.json`](pulse/pulse.json), which drives the live view on the site and the table above. |

Archived, kept for the record: `local-ccxt-wrapper`, `position-sizer`, `crypto-news-parser-lite`.

## Try it

- [**Data Playground**](https://kvantix.tech/playground/): the whole lab, live. Each investigation has its own page: [weather](https://kvantix.tech/playground/weather/), [energy](https://kvantix.tech/playground/energy/), [offshore wind and rain](https://kvantix.tech/playground/wind-rain/), [experts](https://kvantix.tech/playground/experts/), [wastewater](https://kvantix.tech/playground/wastewater/) and [nitrogen](https://kvantix.tech/playground/nitrogen/).
- **In your browser, nothing stored:** [Track record checker](https://kvantix.tech/playground/track-record/), [Luck or skill?](https://kvantix.tech/playground/luck-or-skill/) and [Lock your prediction](https://kvantix.tech/playground/lock-your-prediction/).
- [**Quick Check**](https://kvantix.tech/#kvx-toolkit): run the seven tests on your own CSV. Free, no login, the file is not kept.
- [**Validation Report**](https://kvantix.tech/#kvx-services): a written verdict on your claim. Same price whatever the verdict.

[kvantix.tech](https://kvantix.tech) · [LinkedIn](https://www.linkedin.com/company/kvantix/) · [X](https://x.com/KvantixTech) · validation@kvantix.tech · Hjørring, Denmark · CVR 46296036

<sub>Statistics, not advice. Kvantix sells no signals.</sub>
