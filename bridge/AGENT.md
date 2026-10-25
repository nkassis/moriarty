# AGENT.md

Developer tooling for the bridge. Commands run from `bridge/`. Package manager is pnpm (version pinned in `package.json#packageManager`); do not use npm or yarn.

## Setup

```sh
npm i -g pnpm@12.11.2                         # the version in package.json#packageManager
pnpm install --frozen-lockfile
pnpm exec playwright install chromium         # first time only
```

Or use pnpm's standalone installer: `curl -fsSL https://get.pnpm.io/install.sh | env PNPM_VERSION=12.11.2 sh -`. When `packageManager` changes, install the new version the same way. Corepack is not used: Node removes it from the distribution after Node 24.

Node version is pinned in `.nvmrc` (24). `pnpm-workspace.yaml` sets `minimumReleaseAge` to two weeks, the same freshness rule as the Python side.

## Scripts

| Script            | What it does                                                                |
| ----------------- | --------------------------------------------------------------------------- |
| `pnpm dev`        | Vite dev server at http://localhost:5173; the kit is at `/kit`              |
| `pnpm build`      | Typecheck then production build to `dist/`                                  |
| `pnpm preview`    | Serve `dist/` locally                                                       |
| `pnpm typecheck`  | `tsc` (no emit)                                                             |
| `pnpm lint`       | ESLint, zero warnings, then Stylelint on `src/**/*.css`                     |
| `pnpm format`     | Prettier write; `format:check` in CI                                        |
| `pnpm test`       | Vitest, single run; `test:watch` for the loop                               |
| `pnpm e2e`        | Playwright against a built app (`vite preview`); `e2e:ui` to debug          |
| `pnpm check`      | typecheck + lint + format:check + test + token drift; what CI runs          |
| `pnpm gen:tokens` | Regenerate `src/mycroft/tokens.{css,ts}`; `gen:tokens:check` fails on drift |

## Testing

- Vitest uses jsdom and `@testing-library/jest-dom` matchers, set up in `test/setup.ts`.
- Playwright config is `playwright.config.ts`; specs in `test/e2e/`. Motion is reduced so the Cascade is still.
- `test/e2e/kit.spec.ts` screenshots each theme section of `/kit?dialog=open` against the baselines in `test/e2e/kit.spec.ts-snapshots/` (Linux, Chromium). CI does not run e2e yet; run `pnpm e2e` locally when a component or the kit changes, and `pnpm e2e --update-snapshots` only for an intended visual change.
- One unit file: `pnpm test src/mycroft/CommLine.test.tsx`. One e2e spec: `pnpm e2e test/e2e/kit.spec.ts`.

## Tokens

`../docs/design/mycroft/tokens.json` is the source for colour (four themes), type, spacing, radius and layout. `scripts/tokens.ts` writes `src/mycroft/tokens.css` (custom properties per `[data-theme]`, type variables `--type-<style>-family|size|line|weight|tracking`, and the `.type-*` classes) and `src/mycroft/tokens.ts` (typed names and resolved values). Both are committed and read-only: change `tokens.json`, run `pnpm gen:tokens`, commit all three. Every theme block declares every colour, so `data-theme` on any wrapper resets everything below it, nested or not.

## Pre-commit

The root `.pre-commit-config.yaml` runs `pnpm lint` and `pnpm format:check` when files under `bridge/` are staged; `pnpm` must be on `PATH` (see Setup). Do not bypass with `--no-verify`.

## Troubleshooting

- `Cannot find module` after pulling: `pnpm install`, then restart the TS server in the editor.
- Playwright `browserType.launch` errors: `pnpm exec playwright install chromium`.
- Port in use: `pnpm dev --port 5174`.
