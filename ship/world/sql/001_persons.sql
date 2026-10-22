-- world.persons: the seeded manifest (docs/decisions-m0.md, decision 13). Holodeck-writable truth.
CREATE SCHEMA IF NOT EXISTS world;

CREATE TABLE IF NOT EXISTS world.persons (
    run_id uuid NOT NULL,
    person_id text NOT NULL,
    name text NOT NULL,
    kind text NOT NULL CHECK (kind IN ('crew', 'passenger', 'unlisted')),
    deck integer NOT NULL CHECK (deck >= 1),
    section text NOT NULL,
    flags text[] NOT NULL DEFAULT '{}',
    expected_present boolean NOT NULL,
    PRIMARY KEY (run_id, person_id)
);

-- What Ship systems may read: everything except flags.
CREATE OR REPLACE VIEW world.persons_observable AS
SELECT run_id, person_id, name, kind, deck, section, expected_present
FROM world.persons;
