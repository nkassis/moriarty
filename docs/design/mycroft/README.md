# Mycroft source bundle

The design system as exported from the design session, kept as the reference for the React port (NIM-41). Not loaded by any app; the port under `bridge/` is the live version.

- `tokens.json`: the source of truth for colour (four themes), type, spacing, radius and layout tokens, each with a usage note.
- `tokens.css`: generated from `tokens.json`; custom properties per theme (`[data-theme]`) and `.type-*` classes.
- `components/bundle.js`: vanilla implementations of Frame, Rail, Button, Status, Readout, Gauge, AgentCard, CommLine, Cascade, Timeline, Table, Dialog, AlertBanner, Tag, under `window.Mycroft`.
- `components/bundle.css`: their styles.

The canvases in `docs/design/*.dc.html` compose these components into the four screens.
