# regen-sensor-sdk

> The universal ingestion layer for Regen Network's Claims Engine.

`regen-sensor-sdk` is a Python SDK for building **sensors** — components that pull evidence from real-world sources (meeting transcripts, ROS-driven hardware sensors, public RSS/news feeds, GitHub webhooks, anything else) and emit structured **Output Records** that the downstream [Claims Engine](https://github.com/gaiaaiagent/koi-processor) consumes, enriches, and anchors on-chain.

> 🚧 **Status:** Greenfield. v0.0.0 scaffold, June 2026. First reference sensor (Otter transcript) targeted for July 2026, v0.1.0 release for September 2026.

## What this is

The Claims Engine pipeline is:

```
EVIDENCE  →  INGESTION  →  ENRICHMENT  →  PUBLICATION  →  ACTION
              ↑
        (this SDK)
```

The Ingestion layer is where messy real-world evidence becomes structured data the rest of the pipeline can trust. Different evidence sources have wildly different shapes — a meeting transcript is not a soil moisture reading is not a GitHub PR event — but the *Output Record contract* is uniform. This SDK exists so any new source can be wrapped in a sensor that emits Output Records, without each one reinventing the schema, the auth, the retry logic, or the anchoring path.

## Why it exists

Regen Network's Claims Engine needs to ingest evidence from a growing set of sources. Without a shared SDK, each source becomes a one-off integration that duplicates schema decisions and accumulates technical debt. With one, every new sensor inherits the same contract, the same tests, and the same observability — and the senior engineering team can maintain the substrate going forward.

This SDK is the **WP4** deliverable in the Claims Engine Architecture v0.2.1 roadmap.

## Quick start

> Not yet installable. Check back after v0.0.1 (target: mid-June 2026).

```bash
# pip install regen-sensor-sdk  # coming soon
```

## Project structure

```
src/regen_sensor_sdk/    # the SDK
tests/                   # pytest test suite
docs/                    # (TBD — design + tutorial docs)
.github/workflows/       # CI
CHANGELOG.md             # Keep a Changelog
CODEOWNERS               # who reviews what
CONTRIBUTING.md          # how to contribute
```

## For contributors

If you're landing here as a new contributor:

1. Read **[CONTRIBUTING.md](CONTRIBUTING.md)** first.
2. The architectural context lives in the [Claims Engine Architecture v0.2.1](https://www.notion.so) Notion doc (ask in Slack `#claims-engine-build` for the link).
3. The Output Record contract — what every sensor must emit — is being designed in the first weeks of the project. See open ADRs and the design doc in `docs/` once they land.
4. Open an issue or draft PR early; conversation beats guessing.

## Development setup

```bash
git clone https://github.com/regen-network/sensor-sdk.git
cd sensor-sdk
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

Tested against Python 3.11 and 3.12.

## Team

- **Maintainer (technical lead):** [@DarrenZal](https://github.com/DarrenZal)
- **Primary author (Constellations Fellowship, Summer 2026):** Mahashri Ranjith Kumar — handle pending
- **Program lead:** Christian Shearer ([@CShear](https://github.com/CShear))

See [CODEOWNERS](CODEOWNERS) for review responsibilities.

## License

[Apache License 2.0](LICENSE) — Copyright 2026 Regen Network Development, PBC.
