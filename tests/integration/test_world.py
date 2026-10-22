from uuid import uuid4

import pytest
from psycopg import AsyncConnection

from holodeck.world import MANIFEST_SIZE, apply_world_sql, generate_manifest, seed_manifest

pytestmark = pytest.mark.integration


def test_manifest_is_deterministic_per_seed() -> None:
    assert generate_manifest(3) == generate_manifest(3)
    assert generate_manifest(3) != generate_manifest(4)


async def test_seeded_manifest_is_written_and_the_view_hides_flags(database_url: str) -> None:
    run_id = uuid4()
    async with await AsyncConnection.connect(database_url) as db:
        await apply_world_sql(db)
        await apply_world_sql(db)  # idempotent: applied at every run start
        await seed_manifest(db, run_id, seed=3)
        await db.commit()

        cur = await db.execute("SELECT count(*) FROM world.persons WHERE run_id = %s", (run_id,))
        assert await cur.fetchone() == (MANIFEST_SIZE,)

        cur = await db.execute(
            "SELECT column_name FROM information_schema.columns"
            " WHERE table_schema = 'world' AND table_name = 'persons_observable'"
        )
        columns = {row[0] for row in await cur.fetchall()}
        assert "flags" not in columns
        assert {"person_id", "deck", "section", "expected_present"} <= columns
