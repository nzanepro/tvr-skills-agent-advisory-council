"""Shared fixtures for the council.py tests.

council.py is a standalone script (not part of an installed package), so it is
loaded by file path with importlib rather than a normal import.
"""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = REPO_ROOT / "advisory-council"
SCRIPT_PATH = SKILL_DIR / "scripts" / "council.py"

# A small, fictional, three-seat roster used across most tests. Weights are
# unequal (2, 1, 1) so headcount and weighted tallies can disagree.
SEAT_SPECS = [
    "cfo:Bakery Owner:Leadership:2",
    "ops:Head Baker:Operations",
    "critic:Neighborhood Customer:Customers",
]
SEAT_IDS = ["cfo", "ops", "critic"]
TITLE = "Open a second Riverside Bakery location across town"


def _load_council():
    spec = importlib.util.spec_from_file_location("council", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def council():
    """A fresh import of council.py for each test."""
    return _load_council()


@pytest.fixture()
def run(council, capsys):
    """Call council.main([...]) and return (exit_code, stdout) for the call."""

    def _run(argv):
        exit_code = council.main(argv)
        out = capsys.readouterr().out
        return exit_code, out

    return _run


def init_council(run, tmp_path, name="council", seats=None, title=TITLE, extra=None):
    """Run `init` with a small fictional bakery roster and return the folder."""
    folder = tmp_path / name
    args = ["init", str(folder), "--title", title]
    for spec in (seats if seats is not None else SEAT_SPECS):
        args += ["--seat", spec]
    args += extra or []
    exit_code, out = run(args)
    assert exit_code == 0, out
    return folder


def strip_todo(text: str) -> str:
    """Remove the `<!-- council:todo -->` marker line from stub text."""
    lines = [ln for ln in text.splitlines() if ln.strip() != "<!-- council:todo -->"]
    return "\n".join(lines) + "\n"


def set_fields(text: str, **fields: str) -> str:
    """Replace `**Name:** ...` lines with real values, one per keyword arg.

    Keyword names use underscores for spaces, e.g. set_fields(t, Changed_from_round_1="no").
    """
    for name, value in fields.items():
        field_name = name.replace("_", " ")
        pattern = re.compile(rf"^\*\*{re.escape(field_name)}:\*\*.*$", re.MULTILINE)
        text, count = pattern.subn(f"**{field_name}:** {value}", text, count=1)
        assert count == 1, f"field {field_name!r} not found to fill in"
    return text


def fill_file(path: Path, **fields: str) -> str:
    """Strip the todo marker and set the given **Field:** lines; write and return the text."""
    text = strip_todo(path.read_text(encoding="utf-8"))
    if fields:
        text = set_fields(text, **fields)
    path.write_text(text, encoding="utf-8")
    return text


def fill_round1(folder: Path, seat_id: str, position="Launch in one region first",
                confidence="medium") -> None:
    fill_file(folder / f"ROUND1-{seat_id}.md", Position=position, Confidence=confidence)


def fill_round2(folder: Path, seat_id: str, vote="B", changed="no", confidence="medium") -> None:
    fill_file(folder / f"ROUND2-{seat_id}.md", Vote=vote, **{"Changed_from_round_1": changed},
              Confidence=confidence)


def fill_recommendation(folder: Path, council_vote="Option B: 2 of 3 seats, weighted 3 of 4.") \
        -> None:
    fill_file(folder / "RECOMMENDATION.md", **{"Council_vote": council_vote})


def fill_simple(path: Path) -> None:
    """Strip the todo marker only; used for files with no required **Field:** lines."""
    fill_file(path)


def build_passing_session(run, tmp_path, name="council", seats=None, seat_ids=None) -> Path:
    """A minimal session that satisfies `council.py check --final`.

    council, dossier, verification and the tally are filled by stripping the todo
    marker only (their required content is already present from `init`); Round 1,
    Round 2 and the recommendation need real field values.
    """
    folder = init_council(run, tmp_path, name=name, seats=seats)
    ids = seat_ids if seat_ids is not None else SEAT_IDS
    roster = __import__("json").loads((folder / "council.json").read_text(encoding="utf-8"))
    dossier_name = f"DOSSIER-{roster['dossier']:02d}-{roster['slug']}.md"

    fill_simple(folder / "COUNCIL.md")
    fill_simple(folder / dossier_name)
    for seat_id in ids:
        fill_round1(folder, seat_id)
    fill_simple(folder / "VERIFICATION.md")
    fill_simple(folder / "ROUND1-TALLY.md")
    for seat_id in ids:
        fill_round2(folder, seat_id)
    fill_recommendation(folder)
    return folder
