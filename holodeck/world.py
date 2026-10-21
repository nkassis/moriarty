"""World truth: applies the `world` SQL and writes the seeded manifest at run start."""

import random
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

from psycopg import AsyncConnection

from ship.contract.enums import PersonKind

SQL_DIR = Path(__file__).parents[1] / "ship" / "world" / "sql"

DECKS = (1, 2, 3, 4, 5)
SECTIONS = ("A", "B", "C", "D")
MANIFEST_SIZE = 40
GIVEN_NAMES = ("Avery", "Brook", "Corin", "Dale", "Ellis", "Fenn", "Gray", "Hollis", "Ives")
FAMILY_NAMES = ("Achterberg", "Basso", "Choi", "Dunmore", "Eze", "Falk", "Gorski", "Huang")


@dataclass(frozen=True)
class Person:
    person_id: str
    name: str
    kind: PersonKind
    deck: int
    section: str
    flags: tuple[str, ...]
    expected_present: bool


async def apply_world_sql(conn: AsyncConnection) -> None:
    """Create the `world` tables and views; idempotent."""
    for path in sorted(SQL_DIR.glob("*.sql")):
        await conn.execute(path.read_text().encode())


def generate_manifest(seed: int) -> list[Person]:
    """A deterministic crew and passenger manifest for `seed`."""
    rng = random.Random(seed)
    people: list[Person] = []
    for index in range(MANIFEST_SIZE):
        kind = PersonKind.CREW if index % 3 else PersonKind.PASSENGER
        people.append(
            Person(
                person_id=f"P-{index:04d}",
                name=f"{rng.choice(GIVEN_NAMES)} {rng.choice(FAMILY_NAMES)}",
                kind=kind,
                deck=rng.choice(DECKS),
                section=rng.choice(SECTIONS),
                flags=(),
                expected_present=True,
            )
        )
    return people


async def seed_manifest(conn: AsyncConnection, run_id: UUID, seed: int) -> list[Person]:
    """Write the manifest for this run into `world.persons`."""
    people = generate_manifest(seed)
    async with conn.cursor() as cur:
        await cur.executemany(
            "INSERT INTO world.persons"
            " (run_id, person_id, name, kind, deck, section, flags, expected_present)"
            " VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            [
                (
                    run_id,
                    p.person_id,
                    p.name,
                    p.kind.value,
                    p.deck,
                    p.section,
                    list(p.flags),
                    p.expected_present,
                )
                for p in people
            ],
        )
    return people


def expected_in_section(people: list[Person], deck: int, section: str) -> int:
    """How many people the manifest expects in a section; lifeform counts are checked against it."""
    return sum(1 for p in people if p.expected_present and (p.deck, p.section) == (deck, section))
