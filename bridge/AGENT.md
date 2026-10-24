# AGENT.md

Developer tooling for the bridge. Commands run from `bridge/`. Package manager is pnpm (version pinned in `package.json#packageManager`); do not use npm or yarn.

## Setup

```sh
corepack enable                               # or install the pinned pnpm another way
pnpm install --frozen-lockfile
pnpm exec playwright install chromium         # first time only
```

Node version is pinned in `.nvmrc` (24). `pnpm-workspace.yaml` sets `minimumReleaseAge` to two weeks, the same freshness rule as the Python side.

## Scripts

| Script           | What it does                                                       |
| ---------------- | ------------------------------------------------------------------ |
| `pnpm dev`       | Vite dev server at http://localhost:5173; the kit is at `/kit`     |
| `pnpm build`     | Typecheck then production build to `dist/`                         |
| `pnpm preview`   | Serve `dist/` locally                                              |
| `pnpm typecheck` | `tsc` (no emit)                                                    |
| `pnpm lint`      | ESLint, zero warnings, then Stylelint on `src/**/*.css`            |
| `pnpm format`    | Prettier write; `format:check` in CI                               |
| `pnpm test`      | Vitest, single run; `test:watch` for the loop                      |
| `pnpm e2e`       | Playwright against a built app (`vite preview`); `e2e:ui` to debug |
| `pnpm check`     | typecheck + lint + format:check + test; what CI runs               |

## Testing

- Vitest uses jsdom and `@testing-library/jest-dom` matchers, set up in `test/setup.ts`.
- Playwright config is `playwright.config.ts`; specs in `test/e2e/`. Motion is reduced so the Cascade is still.
- One unit file: `pnpm test src/mycroft/CommLine.test.tsx`. One e2e spec: `pnpm e2e test/e2e/kit.spec.ts`.

## Pre-commit

The root `.pre-commit-config.yaml` runs `pnpm lint` and `pnpm format:check` (through `corepack`, so no global pnpm is needed) when files under `bridge/` are staged. Do not bypass with `--no-verify`.

## Troubleshooting

- `Cannot find module` after pulling: `pnpm install`, then restart the TS server in the editor.
- Playwright `browserType.launch` errors: `pnpm exec playwright install chromium`.
- Port in use: `pnpm dev --port 5174`.
