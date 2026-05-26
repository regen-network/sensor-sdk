# Contributing to regen-sensor-sdk

Thanks for your interest. This is the SDK that wraps real-world evidence sources as structured Output Records for the Regen Network Claims Engine. It's still very early — most of the design is happening live in the first few weeks of June 2026.

## Before you start

1. **Read the architectural context.** The Claims Engine Architecture v0.2.1 (Notion doc — ask in Slack for the link) is the source of truth for *why* this SDK exists. Reading it before writing code will save you several redirections later.
2. **Lurk in Slack `#claims-engine-build`.** Most design conversations happen there, in writing. You'll absorb the project shape quickly.
3. **Open an issue or draft PR early.** It's much easier to course-correct on a 50-line draft than a 500-line finished PR.

## Development setup

```bash
git clone https://github.com/regen-network/sensor-sdk.git
cd sensor-sdk
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

Python 3.11+ required; CI runs against 3.11 and 3.12.

## Pull request flow

1. Fork or branch from `main`.
2. Make your change. Add or update tests in `tests/`.
3. Run `pytest` locally — it should pass before you push.
4. Open a PR. CI must be green; CODEOWNERS will be auto-requested for review.
5. Once approved, squash-merge into `main`.

## What lives where

- `src/regen_sensor_sdk/` — the SDK itself
- `tests/` — pytest test suite
- `docs/` — design documents, ADRs, tutorials (TBD)
- `.github/workflows/` — CI
- `CHANGELOG.md` — every PR that changes user-visible behavior adds an entry under `## [Unreleased]`

## Code conventions

These will be decided collaboratively in the first weeks of the project (linter, formatter, type-checking strictness, doc tooling). For now: write clear code, write tests for it, and prefer small focused PRs.

## Code of Conduct

Be kind, be specific, assume good faith. Disagreement is welcome; condescension is not.

## License

By contributing, you agree that your contributions will be licensed under the [Apache License 2.0](LICENSE).
