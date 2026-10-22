"""The decision logs keep the shape set in `.claude/rules/decision-log.md`."""

import re
from dataclasses import dataclass
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
LOGS = sorted((ROOT / "docs").glob("decisions-*.md"))
README = ROOT / "README.md"
FIELDS = ("**Why:**", "**Instead of:**", "**Cost:**", "**Status:**")
MAX_WORDS = 150


@dataclass(frozen=True)
class Entry:
    log: Path
    number: int
    title: str
    body: str

    @property
    def status(self) -> str:
        match = re.search(r"\*\*Status:\*\* (.+)", self.body)
        return match.group(1) if match else ""

    @property
    def accepted(self) -> bool:
        return self.status.startswith("Accepted")


def entries(log: Path) -> list[Entry]:
    """Each `### N. Title` heading and the text up to the next heading or the Retired line."""
    text = log.read_text().split("\nRetired:", 1)[0]
    found: list[Entry] = []
    for block in re.split(r"\n(?=#{2,3} )", text):
        match = re.match(r"### (\d+)\. (.+)\n", block)
        if match:
            body = block[match.end() :].strip()
            found.append(Entry(log, int(match.group(1)), match.group(2), body))
    return found


def retired(log: Path) -> set[int]:
    match = re.search(r"^Retired: ([\d, ]+)\.", log.read_text(), re.MULTILINE)
    return {int(n) for n in match.group(1).split(",")} if match else set()


def github_anchor(heading: str) -> str:
    """GitHub's heading slug: lowercase, punctuation dropped, spaces to hyphens."""
    return re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")


ALL = [entry for log in LOGS for entry in entries(log)]


def test_logs_have_entries() -> None:
    assert LOGS
    assert all(entries(log) for log in LOGS)


@pytest.mark.parametrize("log", LOGS, ids=lambda p: p.name)
def test_numbers_are_unique_and_retired_ones_unused(log: Path) -> None:
    numbers = [entry.number for entry in entries(log)]
    assert len(numbers) == len(set(numbers))
    assert not set(numbers) & retired(log)


@pytest.mark.parametrize("entry", ALL, ids=lambda e: f"{e.log.stem}-{e.number}")
def test_entry_is_under_word_limit(entry: Entry) -> None:
    assert len(f"{entry.title} {entry.body}".split()) < MAX_WORDS


@pytest.mark.parametrize("entry", ALL, ids=lambda e: f"{e.log.stem}-{e.number}")
def test_entry_has_status(entry: Entry) -> None:
    assert re.fullmatch(r"Accepted\.|Superseded by .+", entry.status)


@pytest.mark.parametrize(
    "entry", [e for e in ALL if e.accepted], ids=lambda e: f"{e.log.stem}-{e.number}"
)
def test_accepted_entry_has_every_field(entry: Entry) -> None:
    for field in FIELDS:
        assert field in entry.body, f"{field} missing"


def test_readme_lists_each_accepted_decision_once() -> None:
    section = README.read_text().split("\n## Decisions\n", 1)[1].split("\n## ", 1)[0]
    links = re.findall(
        r"^- \[(\d+)\. (.+)\]\((docs/decisions-[\w-]+\.md)#([\w-]+)\)$", section, re.M
    )
    expected = {
        (str(e.number), e.title, f"docs/{e.log.name}", github_anchor(f"{e.number}. {e.title}"))
        for e in ALL
        if e.accepted
    }
    assert len(links) == len(set(links))
    assert set(links) == expected
