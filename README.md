<p align="center"><a href="https://kvantix.tech"><img src="assets/banner.png" alt="Kvantix: independent signal and forecast validation. Does your signal actually work?" width="100%"></a></p>

**Independent validation of trading signals and forecasts.** Seven statistical tests on your own data, and a written verdict from a person. We ran them on our own crypto engine first, in public. It failed.

Everything here follows one method:

1. **Lock it before the outcome.** A prediction that can be edited afterwards proves nothing.
2. **Measure it honestly.** Every call counts, the misses too, against real outcomes and real costs.
3. **Beat a dumb baseline.** "Tomorrow will be like today" is surprisingly hard to beat.

## In public right now

<!-- weather:start -->
**Which weather forecast is right most often in Denmark?** DMI, MET Norway, OpenWeatherMap and the pilots' TAF for five Danish cities, locked four times a day before the weather happens.

| Day | Downloads locked | Chain | Latest public anchor |
|---|---|---|---|
| **2** | 70 | intact | [`b6ce9f7570cc1fb0…`](https://github.com/kvantixtech/weather-forecast-test/blob/main/anchors/chain-heads.csv) · 2026-09-29 |

First scoreboard in about 28 days. Rules published 28 Sep 2026 at 07:57 UTC, four hours before the first forecast. [Live status →](https://kvantix.tech/playground/weather/)
<!-- weather:end -->

## Repositories

| | |
|---|---|
| 🌦️ [**weather-forecast-test**](https://github.com/kvantixtech/weather-forecast-test) | The weather collector and scoring rules, fixed before the first forecast. Hash-chained downloads, anchored here daily. Python, standard library only. |
| 🔒 [**lock-your-prediction**](https://github.com/kvantixtech/lock-your-prediction) | Seal a prediction with SHA-256 and a secret key. Spec, test vectors, and verifiers in Python, Node, the browser and plain `sha256sum`. |
| 🧪 [**validation-examples**](https://github.com/kvantixtech/validation-examples) | Six synthetic datasets where the truth is known, from a real-but-untradeable edge to a look-ahead bug that passes 7/7. Each has its full report. |
| 📄 [**kvantix-reports**](https://github.com/kvantixtech/kvantix-reports) | The reports on our own engine, unedited: KAS v1 **1/7**, KAS v2.1 **2/7**. |

## Try it

- [**Quick Check**](https://kvantix.tech/#kvx-toolkit): run the seven tests on your own CSV. Free, no login, the file is not kept.
- [**Data Playground**](https://kvantix.tech/playground/): [weather test status](https://kvantix.tech/playground/weather/), [Track record checker](https://kvantix.tech/playground/track-record/), [Luck or skill?](https://kvantix.tech/playground/luck-or-skill/) and [Lock your prediction](https://kvantix.tech/playground/lock-your-prediction/).
- [**Validation Report**](https://kvantix.tech/#kvx-services): a written verdict on your claim. Same price whatever the verdict.

[kvantix.tech](https://kvantix.tech) · [X](https://x.com/KvantixTech) · validation@kvantix.tech · Hjørring, Denmark · CVR 46296036

<sub>Statistics, not advice. Kvantix sells no signals.</sub>
