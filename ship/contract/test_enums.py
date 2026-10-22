import re
from enum import StrEnum
from pathlib import Path

from ship.contract.enums import CONTRACT_ENUMS

VOCABULARY = Path(__file__).parents[2] / "docs" / "vocabulary.md"


def vocabulary_enums() -> dict[str, list[str]]:
    """The `## Contract enums` table, keyed by class name (`Agent state` -> `AgentState`)."""
    section = VOCABULARY.read_text().split("## Contract enums", 1)[1].split("\n## ", 1)[0]
    table: dict[str, list[str]] = {}
    for line in section.splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 2 or cells[0] in ("Thing", "---"):
            continue
        name = "".join(word.capitalize() for word in cells[0].split())
        table[name] = re.findall(r"`([^`]+)`", cells[1])
    return table


def code_enums() -> dict[str, list[str]]:
    return {enum.__name__: [member.value for member in enum] for enum in CONTRACT_ENUMS}


def test_vocabulary_table_parses() -> None:
    assert "AgentState" in vocabulary_enums()


def test_enums_match_vocabulary() -> None:
    assert code_enums() == vocabulary_enums()


def test_enums_are_str_enums() -> None:
    assert all(issubclass(enum, StrEnum) for enum in CONTRACT_ENUMS)
