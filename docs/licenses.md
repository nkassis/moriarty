# Licenses

Moriarty is MIT licensed ([LICENSE](../LICENSE)). Current as of M0.

## Scope

`LICENSE` covers everything in this repository, including the design artboards in `docs/design/` and the Mycroft source bundle in `docs/design/mycroft/`. No beat or episode (Doyle) files exist yet; when they land under `scenarios/`, they are covered by the same license.

## Third-party dependencies

Runtime dependencies of `holodeck` and `ship`, from `uv run pip-licenses --from=mixed` against `uv.lock`:

| Package | License | Notes |
| --- | --- | --- |
| `psycopg`, `psycopg-binary` | LGPL-3.0-only | See below |
| `aio-pika`, `aiormq` | Apache-2.0 | |
| `pamqp` | BSD-3-Clause | |
| `pydantic`, `pydantic_core`, `annotated-types`, `typing-inspection` | MIT | |
| `typing_extensions` | PSF-2.0 | |
| `opentelemetry-*` | Apache-2.0 | |
| `grpcio`, `googleapis-common-protos` | Apache-2.0 | OTLP exporter, `ship` only |
| `protobuf` | BSD-3-Clause | |
| `multidict`, `yarl`, `propcache` | Apache-2.0 | |
| `idna` | BSD-3-Clause | |

`langgraph` (MIT) arrives with the reference crews; it is not a dependency yet.

Dev tooling (`black`, `ruff`, `pytest`, `testcontainers`, `pre-commit`, `pip-licenses` and their dependencies) is MIT, BSD, Apache-2.0 or PSF, except `certifi` and `pathspec`, which are MPL-2.0. Neither is shipped.

### Bridge

Runtime dependencies of `bridge/`, from `pnpm licenses list --prod`:

| Package | License | Notes |
| --- | --- | --- |
| `react`, `react-dom` | MIT | |
| `@tanstack/*`, `cookie-es` | MIT | Router and Query |
| `isbot` | Unlicense | Router dependency |
| `@fontsource/antonio`, `@fontsource/source-sans-3`, `@fontsource/jetbrains-mono` | OFL-1.1 | Font files, unmodified |

Dev tooling (Vite, TypeScript, ESLint, Stylelint, Prettier, Vitest, Playwright and their dependencies) is MIT, ISC, BSD, Apache-2.0, BlueOak, CC0, MIT-0 or Python-2.0, except three MPL-2.0 packages and one CC-BY-4.0 data package. None is shipped.

### Not permissive by default

- **psycopg** is LGPL-3.0-only, the version 3.3.6 metadata says so (not "or later"). Moriarty uses it as an unmodified dependency installed from PyPI, which the LGPL permits for MIT code. Do not vendor, copy or patch it. `psycopg[binary]` bundles `libpq`, which is under the PostgreSQL License (permissive).
- **OFL-1.1 fonts** (bridge). The Open Font License allows bundling the fonts with MIT code; the fonts must not be sold on their own, and a modified version may not keep a reserved font name. They are served unmodified.
- **certifi** and **pathspec** (MPL-2.0, dev only). MPL is file-level copyleft and applies only to modified copies of their files.

## CI check

The `check` workflow runs `pip-licenses` and fails on any GPL or AGPL package. LGPL and MPL pass. Matching is exact on license names, so the list in `.github/workflows/ci.yml` names each SPDX identifier and PyPI classifier spelling. A package that declares only a compound expression such as `MIT AND GPL-3.0-only` does not match. Check new dependencies' licenses by hand in review.

To run it locally, copy the `Licenses` step's command from `.github/workflows/ci.yml`.
