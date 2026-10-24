# Bridge

The React console for Moriarty: the screen a human watches while a crew works a scenario, built on the Mycroft design system. It shows what the crew sees plus the trace, and never the Holodeck's hidden state.

Read `../docs/architecture.md` § Bridge UI and the root `CLAUDE.md` before touching `src/`. `AGENT.md` has the tooling commands. When a question is not answered here or there, stop and ask; do not decide silently.

## Stack

- React 19, TypeScript strict, Vite. No class components, no `any`, no `@ts-ignore` (use `@ts-expect-error` with a reason when unavoidable).
- Routing: TanStack Router. Server state: TanStack Query. Both installed, not yet used: `/kit` is a plain page selected in `src/main.tsx`. Client state: React state and context first.
- Styling: the Mycroft design system in `src/mycroft/`, plain CSS with `my-*` class names. Tokens are generated from `../docs/design/mycroft/tokens.json` into `src/mycroft/tokens.css` and `tokens.ts`; never hard-code a colour, spacing or font value in a component. Stylelint and ESLint enforce it.
- Contract types: `src/contract/enums.ts` is a hand-copied stopgap from `docs/vocabulary.md`, replaced by types generated from `ship/contract/schema/` in NIM-19. Never edit generated types.
- Tests: Vitest + React Testing Library for units; Playwright for the kit screenshots now and the end-to-end flows in `../docs/user-stories.md` later.
- Lint and format: ESLint (typescript-eslint strict, react-hooks, jsx-a11y), Stylelint and Prettier; all run in CI and pre-commit.

## Layout

```
src/
  main.tsx         # entry; picks the page by path
  mycroft/         # the design system: tokens and one file per component; imports only React
  contract/        # contract enums (stopgap until NIM-19)
  kit/             # the /kit visual check: every component in every theme
scripts/           # Node scripts (token generator)
test/              # Vitest setup, Playwright specs and baselines
```

A file holds one component. Name files after the export: `CommLine.tsx`, `CommLine.css`, `CommLine.test.tsx`.

## Rules

- **`src/mycroft/` is self-contained.** It imports React, its own files, and `../contract/enums` as types only. No application logic, no data fetching, no WebSockets. ESLint enforces the import boundary.
- **Port, do not redesign.** Mycroft components follow `../docs/design/mycroft/components/` and the usage notes in `tokens.json`. A visual change starts in the design source.
- **Data flows down, events flow up.** Components receive data and callbacks as props.
- **Derive, don't sync.** A `useEffect` that sets state from other state is a bug. Effects are for the outside world and always clean up.
- **Accessibility is not optional.** Semantic elements first; ARIA only to fill a real gap. Every interactive element is keyboard reachable with a visible focus state. Tests query by role and label.
- **No premature abstraction**, and no `memo`, `useCallback` or virtualisation without a measurement.
- **No new dependency without saying why in the PR**, and never one that duplicates something already in `package.json`.

## Testing

- Unit tests sit next to the file and test behaviour through the DOM, not implementation.
- A bug fix comes with the test that would have caught it.
- Playwright screenshots of `/kit` are the visual check for Mycroft; update baselines only for an intended visual change, and say so in the PR.

## Conventions

- Commit messages and PRs follow the root `CLAUDE.md` (Linear key, imperative, one line).
- Run `pnpm check` (typecheck, lint, format, unit tests) before calling anything done; run `pnpm e2e` when a component or the kit changed.
- Generated files, lockfiles and screenshot baselines are committed; build output is not.

## Working with coding agents

- Read the relevant component, its test and the design source before changing them; match the existing patterns.
- Do not restructure, rename or reformat files you were not asked to change.
- When a design decision is needed (new dependency, new state shape, new route structure), stop and ask; record the answer in the current `../docs/decisions-<milestone>.md`.
- If a test fails after your change, fix the cause; do not delete or skip the test.
