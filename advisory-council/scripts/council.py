#!/usr/bin/env python3
"""Scaffold, track, tally and check an advisory-council file set.

An advisory council session lives in one folder as a numbered set of Markdown files:

    council.json                 machine-readable roster (seats, weights)
    COUNCIL.md                   the decision, the roster and one persona card per seat
    DOSSIER-01-<slug>.md         the shared factual record every member works from
    ROUND1-<seat>.md             one independent position per voting seat
    VERIFICATION.md              persona-free check of load-bearing claims
    ADDENDUM-01A.md, 01B, ...    corrections only (created on demand with `addendum`)
    ROUND1-TALLY.md              positions, splits and lettered options, written after Round 1
    ROUND2-<seat>.md             one vote per seat on the tally's options
    RECOMMENDATION.md            recommendation with vote, dissent, risks, open questions, next steps

Every file starts as a stub carrying the marker `<!-- council:todo -->`; delete that line when the
file is written. Nothing here calls a model: the script only removes bookkeeping (file names,
roster tables, counting votes, checking the process rules).

Subcommands:
    init      create the folder, council.json and every stub (never overwrites a file)
    status    show which stage each file is at and what to do next
    addendum  create the next ADDENDUM-<NN><letter>.md and print the next item number
    tally     list Round 1 positions, or count Round 2 votes by option with weights
    check     check the file set against the council's process rules

Exit status: 0 ok, 1 usage or input error (the message says what to try), 3 the check or tally
found problems (listed on stdout, or in the JSON with --json).

Examples:
    python council.py init council --title "Launch a paid tier" \\
        --seat cfo:"Chief Financial Officer":C-suite \\
        --seat smb-owner:"Small-business owner (target segment)":Customers:2 \\
        --seat critic:"Consumer advocate (critic)":Critics
    python council.py status council
    python council.py addendum council
    python council.py tally council --round 2
    python council.py check council --final
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import string
import sys
from pathlib import Path

TODO_MARKER = "<!-- council:todo -->"
SCHEMA_VERSION = 1
SEAT_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
RESERVED_IDS = {"tally", "verifier", "verification", "recommendation", "council", "dossier"}
# A council smaller than 3 is a conversation; larger than 9 produces redundant voices
# (the method's first run found that only about 6 of 15 seats did distinct work).
RECOMMENDED_SEATS = (3, 9)
MAX_SEATS = 25
VERDICTS = ("CONFIRMED", "CONTRADICTED", "MISLEADING", "UNVERIFIED", "ESTIMATE")
RECOMMENDATION_HEADINGS = ("what to do", "why", "dissent", "risks", "open questions",
                           "next steps", "limits")
# Unfilled template placeholders look like "<one line, in this seat's own words>".
PLACEHOLDER_RE = re.compile(r"<(?!!--)[a-z][^<>\n]{3,}>")
FIELD_RE = r"^\*\*{name}:\*\*[ \t]*(?P<value>.*)$"

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "references" / "templates"


class CouncilError(Exception):
    """A usage or input error; the message says what to try next."""


# ----------------------------------------------------------------------------- helpers

def slugify(text: str, limit: int = 40) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    slug = slug[:limit].rstrip("-")
    return slug or "decision"


def two_digit(number: int) -> str:
    return f"{number:02d}"


def load_template(name: str) -> str:
    path = TEMPLATE_DIR / name
    if not path.is_file():
        raise CouncilError(f"template {path} is missing; reinstall the advisory-council skill folder "
                           "so references/templates/ sits beside scripts/")
    return path.read_text(encoding="utf-8")


def fill(template: str, values: dict) -> str:
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", str(value))
    return template


def format_weight(weight: float) -> str:
    return str(int(weight)) if float(weight).is_integer() else f"{weight:g}"


def parse_seat(spec: str) -> dict:
    """Parse ID:TITLE[:GROUP[:WEIGHT]]."""
    parts = spec.split(":")
    if len(parts) < 2 or not parts[0].strip() or not parts[1].strip():
        raise CouncilError(f"--seat {spec!r}: use ID:TITLE[:GROUP[:WEIGHT]], for example "
                           "cfo:\"Chief Financial Officer\":C-suite:1")
    if len(parts) > 4:
        raise CouncilError(f"--seat {spec!r}: too many ':' parts; titles cannot contain ':'")
    seat = {"id": parts[0].strip(), "title": parts[1].strip(),
            "group": parts[2].strip() if len(parts) > 2 else "", "weight": 1}
    if len(parts) == 4:
        try:
            seat["weight"] = float(parts[3])
        except ValueError:
            raise CouncilError(f"--seat {spec!r}: weight {parts[3]!r} is not a number") from None
    return seat


def validate_roster(roster: dict) -> list:
    """Return a list of error strings for a roster dict."""
    errors = []
    seats = roster.get("seats")
    if not isinstance(seats, list) or not seats:
        return ["council.json has no seats; add at least three voting seats"]
    if len(seats) > MAX_SEATS:
        errors.append(f"{len(seats)} seats is more than the limit of {MAX_SEATS}")
    seen = set()
    for index, seat in enumerate(seats):
        if not isinstance(seat, dict):
            errors.append(f"seat {index + 1} is not an object")
            continue
        seat_id = seat.get("id", "")
        if not isinstance(seat_id, str) or not SEAT_ID_RE.match(seat_id):
            errors.append(f"seat id {seat_id!r} must be lower-case kebab-case, e.g. 'cfo' or "
                          "'customer-smb'")
        elif seat_id in RESERVED_IDS:
            errors.append(f"seat id {seat_id!r} is reserved; choose another")
        elif seat_id in seen:
            errors.append(f"seat id {seat_id!r} appears twice")
        seen.add(seat_id)
        if not str(seat.get("title", "")).strip():
            errors.append(f"seat {seat_id!r} has no title")
        weight = seat.get("weight", 1)
        if isinstance(weight, bool) or not isinstance(weight, (int, float)) or weight < 0:
            errors.append(f"seat {seat_id!r} weight must be a number >= 0")
    if not any(s.get("weight", 1) > 0 for s in seats if isinstance(s, dict)
               and isinstance(s.get("weight", 1), (int, float))):
        errors.append("no seat has a weight above 0, so nobody votes")
    return errors


def load_roster(folder: Path) -> dict:
    path = folder / "council.json"
    if not path.is_file():
        raise CouncilError(f"{path} not found; run `council.py init {folder} --title ... --seat ...` "
                           "first")
    try:
        roster = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CouncilError(f"{path} is not valid JSON ({exc}); fix it or re-create it with init") \
            from None
    errors = validate_roster(roster)
    if errors:
        raise CouncilError(f"{path}: " + "; ".join(errors))
    roster.setdefault("dossier", 1)
    roster.setdefault("slug", slugify(roster.get("title", "decision")))
    return roster


def voting_seats(roster: dict) -> list:
    return [s for s in roster["seats"] if s.get("weight", 1) > 0]


def dossier_name(roster: dict) -> str:
    return f"DOSSIER-{two_digit(roster['dossier'])}-{roster['slug']}.md"


def file_state(path: Path) -> str:
    if not path.is_file():
        return "missing"
    return "todo" if TODO_MARKER in path.read_text(encoding="utf-8") else "done"


def read_field(text: str, name: str) -> str | None:
    match = re.search(FIELD_RE.format(name=re.escape(name)), text, re.MULTILINE)
    if not match:
        return None
    value = match.group("value").strip()
    if not value or PLACEHOLDER_RE.search(value):
        return None
    return value


def addendum_files(folder: Path, roster: dict) -> list:
    prefix = f"ADDENDUM-{two_digit(roster['dossier'])}"
    return sorted(p for p in folder.glob(prefix + "*.md")
                  if re.fullmatch(prefix + r"[A-Z]", p.stem))


# ----------------------------------------------------------------------------- init

def cmd_init(args) -> dict:
    folder = Path(args.folder)
    roster_path = folder / "council.json"
    created, kept = [], []

    if args.roster:
        source = Path(args.roster)
        if not source.is_file():
            raise CouncilError(f"--roster {source} not found")
        try:
            base = json.loads(source.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise CouncilError(f"--roster {source} is not valid JSON ({exc})") from None
        seats = base.get("seats", [])
    else:
        seats = [parse_seat(spec) for spec in args.seat or []]

    if roster_path.is_file():
        if seats or args.title:
            raise CouncilError(f"{roster_path} already exists; edit it by hand, or run init with only "
                               "the folder to create any missing stubs")
        roster = load_roster(folder)
    else:
        if not args.title:
            raise CouncilError("--title is required for a new council, e.g. --title \"Launch a "
                               "paid tier\"")
        if not seats:
            raise CouncilError("give the seats with --seat ID:TITLE[:GROUP[:WEIGHT]] (repeat it) or "
                               "reuse a roster with --roster path/to/council.json")
        roster = {
            "schema": SCHEMA_VERSION,
            "title": args.title,
            "slug": slugify(args.topic or args.title),
            "dossier": args.dossier,
            "date": args.date or _dt.date.today().isoformat(),
            "mode": args.mode,
            "seats": [{"id": s["id"], "title": s["title"], "group": s.get("group", ""),
                       "weight": s.get("weight", 1)} for s in seats],
        }
        errors = validate_roster(roster)
        if errors:
            raise CouncilError("; ".join(errors))
        folder.mkdir(parents=True, exist_ok=True)
        roster_path.write_text(json.dumps(roster, indent=2) + "\n", encoding="utf-8")
        created.append(roster_path.name)

    warnings = []
    n_voting = len(voting_seats(roster))
    low, high = RECOMMENDED_SEATS
    if not low <= n_voting <= high:
        warnings.append(f"{n_voting} voting seats; {low}-{high} is recommended (5-7 is typical)")

    nn = two_digit(roster["dossier"])
    common = {"title": roster["title"], "slug": roster["slug"], "nn": nn,
              "date": roster.get("date", ""), "mode": roster.get("mode", "parallel"),
              "seat_count": n_voting}

    def seat_values(seat):
        return {**common, "seat_id": seat["id"], "seat_title": seat["title"],
                "seat_group": seat.get("group") or "-",
                "seat_weight": format_weight(seat.get("weight", 1))}

    roster_table = "\n".join(
        f"| {s['id']} | {s['title']} | {s.get('group') or '-'} | {format_weight(s.get('weight', 1))} |"
        for s in roster["seats"])
    persona = load_template("PERSONA.md")
    cards = "\n".join(fill(persona, seat_values(s)) for s in roster["seats"])
    seat_rows = "\n".join(f"| {s['id']} | {format_weight(s.get('weight', 1))} | | | |"
                          for s in voting_seats(roster))
    seat_rows_unique = "\n".join(f"| {s['id']} | |" for s in voting_seats(roster))

    plan = [("COUNCIL.md", "COUNCIL.md",
             {**common, "roster_table": roster_table, "persona_cards": cards.rstrip("\n")}),
            (dossier_name(roster), "DOSSIER.md", common)]
    plan += [(f"ROUND1-{s['id']}.md", "ROUND1.md", seat_values(s)) for s in voting_seats(roster)]
    plan += [("VERIFICATION.md", "VERIFICATION.md", common),
             ("ROUND1-TALLY.md", "TALLY.md",
              {**common, "seat_rows": seat_rows, "seat_rows_unique": seat_rows_unique})]
    plan += [(f"ROUND2-{s['id']}.md", "ROUND2.md", seat_values(s)) for s in voting_seats(roster)]
    plan += [("RECOMMENDATION.md", "RECOMMENDATION.md", common)]

    for name, template, values in plan:
        path = folder / name
        if path.exists():
            kept.append(name)
            continue
        path.write_text(fill(load_template(template), values), encoding="utf-8", newline="\n")
        created.append(name)

    return {"ok": True, "folder": str(folder.resolve()), "created": created, "kept": kept,
            "warnings": warnings,
            "next": "fill COUNCIL.md persona cards, confirm the roster with the user, then write "
                    f"{dossier_name(roster)}"}


# ----------------------------------------------------------------------------- status

def stage_report(folder: Path, roster: dict) -> list:
    seats = voting_seats(roster)

    def group(prefix):
        states = {s["id"]: file_state(folder / f"{prefix}-{s['id']}.md") for s in seats}
        done = sum(1 for v in states.values() if v == "done")
        state = "done" if done == len(seats) else ("todo" if done or any(
            v == "todo" for v in states.values()) else "missing")
        pending = [k for k, v in states.items() if v != "done"]
        return state, f"{done}/{len(seats)}", pending

    stages = []
    for key, name in (("council", "COUNCIL.md"), ("dossier", dossier_name(roster))):
        stages.append({"stage": key, "files": [name], "state": file_state(folder / name)})
    state, count, pending = group("ROUND1")
    stages.append({"stage": "round1", "files": [f"ROUND1-{s['id']}.md" for s in seats],
                   "state": state, "done": count, "pending": pending})
    stages.append({"stage": "verification", "files": ["VERIFICATION.md"],
                   "state": file_state(folder / "VERIFICATION.md")})
    adds = addendum_files(folder, roster)
    stages.append({"stage": "addenda", "files": [p.name for p in adds], "optional": True,
                   "state": "done" if adds and all(file_state(p) == "done" for p in adds)
                   else ("todo" if adds else "none")})
    stages.append({"stage": "tally", "files": ["ROUND1-TALLY.md"],
                   "state": file_state(folder / "ROUND1-TALLY.md")})
    state, count, pending = group("ROUND2")
    stages.append({"stage": "round2", "files": [f"ROUND2-{s['id']}.md" for s in seats],
                   "state": state, "done": count, "pending": pending})
    stages.append({"stage": "recommendation", "files": ["RECOMMENDATION.md"],
                   "state": file_state(folder / "RECOMMENDATION.md")})
    return stages


NEXT_STEP = {
    "council": "fill the persona cards in COUNCIL.md and confirm the roster with the user",
    "dossier": "write the dossier: question, options, facts with sources, unknowns, questions",
    "round1": "run Round 1: each pending member writes its report without reading the others",
    "verification": "run the persona-free verifier on the dossier and Round 1 claims",
    "addenda": "publish corrections as an addendum (`council.py addendum`) or skip if none",
    "tally": "write ROUND1-TALLY.md: positions (`council.py tally --round 1`), splits, options",
    "round2": "run Round 2: each pending member reads the tally, addenda and reports, then votes",
    "recommendation": "count the votes (`council.py tally --round 2`) and write RECOMMENDATION.md",
}


def cmd_status(args) -> dict:
    folder = Path(args.folder)
    roster = load_roster(folder)
    stages = stage_report(folder, roster)
    next_step = "complete; run `council.py check --final` and report"
    for stage in stages:
        if stage.get("optional"):
            if stage["state"] == "todo":
                next_step = NEXT_STEP["addenda"]
                break
            continue
        if stage["state"] != "done":
            next_step = NEXT_STEP[stage["stage"]]
            if stage.get("pending"):
                next_step += " (pending: " + ", ".join(stage["pending"]) + ")"
            break
    return {"ok": True, "folder": str(folder.resolve()), "title": roster["title"],
            "stages": stages, "next": next_step}


# ----------------------------------------------------------------------------- addendum

def cmd_addendum(args) -> dict:
    folder = Path(args.folder)
    roster = load_roster(folder)
    existing = addendum_files(folder, roster)
    last_item = 0
    for path in existing:
        for match in re.finditer(r"^##\s+(\d+)\.", path.read_text(encoding="utf-8"), re.MULTILINE):
            last_item = max(last_item, int(match.group(1)))
    letters = [p.stem[-1] for p in existing]
    if letters and letters[-1] == "Z":
        raise CouncilError("26 addenda already exist; consolidate them into a new dossier")
    letter = string.ascii_uppercase[string.ascii_uppercase.index(letters[-1]) + 1] if letters else "A"
    addendum_id = f"{two_digit(roster['dossier'])}{letter}"
    path = folder / f"ADDENDUM-{addendum_id}.md"
    text = fill(load_template("ADDENDUM.md"),
                {"addendum_id": addendum_id, "nn": two_digit(roster["dossier"]),
                 "slug": roster["slug"], "title": roster["title"]})
    text = text.replace("## 1. <short title>", f"## {last_item + 1}. <short title>")
    path.write_text(text, encoding="utf-8", newline="\n")
    return {"ok": True, "created": path.name, "next_item": last_item + 1}


# ----------------------------------------------------------------------------- tally

def cmd_tally(args) -> dict:
    folder = Path(args.folder)
    roster = load_roster(folder)
    seats = voting_seats(roster)
    field = "Position" if args.round == 1 else "Vote"
    rows, missing = [], []
    for seat in seats:
        path = folder / f"ROUND{args.round}-{seat['id']}.md"
        state = file_state(path)
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        value = read_field(text, field) if state == "done" else None
        if value is None:
            missing.append(seat["id"])
            continue
        row = {"seat": seat["id"], "title": seat["title"], "weight": seat.get("weight", 1),
               field.lower(): value, "confidence": read_field(text, "Confidence") or "?"}
        if args.round == 2:
            match = re.match(r"^(?:[Oo]ption\s+)?\**([A-Z])\b", value)
            row["option"] = match.group(1) if match else "Other"
            row["changed"] = read_field(text, "Changed from round 1") or "?"
        rows.append(row)

    total_weight = sum(s.get("weight", 1) for s in seats)
    result = {"ok": not missing, "round": args.round, "seats": len(seats),
              "reported": len(rows), "missing": missing, "rows": rows}
    lines = []
    if args.round == 1:
        lines += ["| Seat | Weight | Position | Confidence |", "|---|---:|---|---|"]
        lines += [f"| {r['seat']} | {format_weight(r['weight'])} | {r['position']} | "
                  f"{r['confidence']} |" for r in rows]
    else:
        totals = {}
        for r in rows:
            entry = totals.setdefault(r["option"], {"option": r["option"], "seats": [],
                                                    "count": 0, "weight": 0})
            entry["seats"].append(r["seat"])
            entry["count"] += 1
            entry["weight"] += r["weight"]
        ordered = sorted(totals.values(), key=lambda t: (-t["weight"], -t["count"], t["option"]))
        result["totals"] = ordered
        result["changed"] = [r["seat"] for r in rows if r["changed"].lower().startswith("yes")]
        lines += ["| Seat | Weight | Vote | Changed from round 1 | Confidence |",
                  "|---|---:|---|---|---|"]
        lines += [f"| {r['seat']} | {format_weight(r['weight'])} | {r['vote']} | {r['changed']} | "
                  f"{r['confidence']} |" for r in rows]
        lines += ["", "| Option | Seats | Headcount | Weighted |", "|---|---|---:|---:|"]
        lines += [f"| {t['option']} | {', '.join(t['seats'])} | {t['count']} of {len(seats)} | "
                  f"{format_weight(t['weight'])} of {format_weight(total_weight)} |" for t in ordered]
    lines.append("")
    lines.append(f"Reported: {len(rows)} of {len(seats)} voting seats.")
    if missing:
        lines.append(f"INCOMPLETE: no filled {field} line from {', '.join(missing)}. "
                     "Do not tally until every seat has reported.")
    result["markdown"] = "\n".join(lines)
    return result


# ----------------------------------------------------------------------------- check

def cmd_check(args) -> dict:
    folder = Path(args.folder)
    roster = load_roster(folder)
    seats = voting_seats(roster)
    problems = []

    def problem(severity, where, message):
        problems.append({"severity": severity, "file": where, "message": message})

    def text_of(name):
        return (folder / name).read_text(encoding="utf-8")

    stages = {s["stage"]: s for s in stage_report(folder, roster)}

    for name in [p.name for p in sorted(folder.glob("*.md"))]:
        if file_state(folder / name) == "done":
            leftover = PLACEHOLDER_RE.findall(text_of(name))
            if leftover:
                problem("warning", name, f"{len(leftover)} unfilled placeholder(s), first: "
                                         f"{leftover[0]}")

    if stages["council"]["state"] == "done":
        text = text_of("COUNCIL.md")
        for seat in roster["seats"]:
            if not re.search(rf"^###\s+{re.escape(seat['id'])}\b", text, re.MULTILINE):
                problem("error", "COUNCIL.md", f"no persona card heading '### {seat['id']}: ...'")

    for seat in seats:
        name = f"ROUND1-{seat['id']}.md"
        if file_state(folder / name) != "done":
            continue
        text = text_of(name)
        for field in ("Position", "Confidence"):
            if read_field(text, field) is None:
                problem("error", name, f"missing or unfilled **{field}:** line")
        if "independent" not in text.lower():
            problem("warning", name, "no independence statement (Round 1 must be written without "
                                     "reading other members)")

    for seat in seats:
        name = f"ROUND2-{seat['id']}.md"
        if file_state(folder / name) != "done":
            continue
        text = text_of(name)
        for field in ("Vote", "Changed from round 1", "Confidence"):
            if read_field(text, field) is None:
                problem("error", name, f"missing or unfilled **{field}:** line")
        changed = read_field(text, "Changed from round 1") or ""
        if changed.lower().startswith("yes") and len(changed.strip(" :-.").split()) < 3:
            problem("error", name, "vote changed without naming the argument or evidence that "
                                   "changed it")

    for path in addendum_files(folder, roster):
        if file_state(path) != "done":
            continue
        text = path.read_text(encoding="utf-8")
        if re.search(r"^\*\*(Position|Vote):\*\*", text, re.MULTILINE):
            problem("error", path.name, "an addendum carries a member's position or vote; addenda "
                                        "hold corrections only (votes stay in the round files)")
        if "wins over" not in text.lower():
            problem("warning", path.name, "does not state which earlier file it wins over")

    if stages["verification"]["state"] == "done":
        if not any(v in text_of("VERIFICATION.md") for v in VERDICTS):
            problem("error", "VERIFICATION.md", "no verdicts (" + ", ".join(VERDICTS) + ")")

    if stages["tally"]["state"] == "done":
        if stages["round1"]["state"] != "done":
            problem("error", "ROUND1-TALLY.md", "tally written before every Round 1 report was in "
                    f"(pending: {', '.join(stages['round1']['pending'])})")
        text = text_of("ROUND1-TALLY.md")
        absent = [s["id"] for s in seats if not re.search(rf"\b{re.escape(s['id'])}\b", text)]
        if absent:
            problem("error", "ROUND1-TALLY.md", f"seats not accounted for: {', '.join(absent)}")
        if not re.search(r"^\s*[-*]\s+\*\*[A-Z]\.\*\*", text, re.MULTILINE):
            problem("warning", "ROUND1-TALLY.md", "no lettered options (- **A.** ...) for Round 2")

    if stages["round2"]["state"] in ("done", "todo") and stages["tally"]["state"] != "done":
        started = [s["id"] for s in seats
                   if file_state(folder / f"ROUND2-{s['id']}.md") == "done"]
        if started:
            problem("error", "ROUND2", "Round 2 reports written before the tally: "
                    + ", ".join(started))

    if stages["recommendation"]["state"] == "done":
        if stages["round2"]["state"] != "done":
            problem("error", "RECOMMENDATION.md", "written before every Round 2 vote was in "
                    f"(pending: {', '.join(stages['round2']['pending'])})")
        text = text_of("RECOMMENDATION.md")
        headings = [h.lower() for h in re.findall(r"^##\s+(?:\d+\.\s*)?(.+)$", text, re.MULTILINE)]
        for wanted in RECOMMENDATION_HEADINGS:
            if not any(wanted in h for h in headings):
                problem("error", "RECOMMENDATION.md", f"no '{wanted}' section")
        if read_field(text, "Council vote") is None:
            problem("error", "RECOMMENDATION.md", "missing or unfilled **Council vote:** line")

    incomplete = [s for s, info in stages.items()
                  if not info.get("optional") and info["state"] != "done"]
    if args.final and incomplete:
        for stage in incomplete:
            problem("error", stage, "stage not complete")

    errors = [p for p in problems if p["severity"] == "error"]
    return {"ok": not errors, "folder": str(folder.resolve()), "incomplete": incomplete,
            "problems": problems}


# ----------------------------------------------------------------------------- main

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="council.py", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init", help="create the folder, council.json and every stub",
                       description="Create FOLDER with council.json and a stub for every file in "
                                   "the session. Existing files are never overwritten, so running "
                                   "init again on a folder only adds missing stubs.")
    p.add_argument("folder", help="output folder, e.g. council or council/pricing")
    p.add_argument("--title", help="the decision in a few words (new council only)")
    p.add_argument("--topic", help="slug for the dossier file name (default: from --title)")
    p.add_argument("--seat", action="append", metavar="ID:TITLE[:GROUP[:WEIGHT]]",
                   help="a voting seat; repeat for each. ID is lower-case kebab-case. Weight 0 "
                        "seats an observer that does not vote")
    p.add_argument("--roster", help="reuse the seats of an existing council.json")
    p.add_argument("--dossier", type=int, default=1,
                   help="dossier number, for a follow-up question to the same council (default 1)")
    p.add_argument("--mode", choices=("parallel", "single"), default="parallel",
                   help="parallel: one subagent per member; single: one agent (default parallel)")
    p.add_argument("--date", help="convening date, YYYY-MM-DD (default today)")

    for name, text in (("status", "show each stage's state and the next step"),
                       ("addendum", "create the next ADDENDUM-<NN><letter>.md")):
        p = sub.add_parser(name, help=text, description=text)
        p.add_argument("folder")

    p = sub.add_parser("tally", help="list Round 1 positions or count Round 2 votes",
                       description="Round 1: a table of each seat's Position line, to paste into "
                                   "ROUND1-TALLY.md. Round 2: each seat's Vote (an option letter) "
                                   "counted by headcount and weight. Exits 3 if any voting seat "
                                   "has not reported, because a partial count is not a tally.")
    p.add_argument("folder")
    p.add_argument("--round", type=int, choices=(1, 2), required=True)

    p = sub.add_parser("check", help="check the file set against the process rules",
                       description="Checks what has been written so far: persona cards, Position / "
                                   "Vote lines, no votes in addenda, tally only after all Round 1 "
                                   "reports, vote changes that name their reason, required "
                                   "recommendation sections. --final also requires every stage to "
                                   "be complete. Exits 3 on any error.")
    p.add_argument("folder")
    p.add_argument("--final", action="store_true", help="require every stage to be complete")

    for sp in sub.choices.values():
        sp.add_argument("--json", action="store_true", help="print one JSON object instead of text")
    return parser


def render_text(command: str, result: dict) -> str:
    if command == "init":
        lines = [f"created {n}" for n in result["created"]] + [f"kept {n}" for n in result["kept"]]
        lines += [f"warning: {w}" for w in result["warnings"]]
        lines.append(f"next: {result['next']}")
    elif command == "status":
        lines = [f"{result['title']} ({result['folder']})"]
        for s in result["stages"]:
            extra = f" {s['done']}" if "done" in s else ""
            files = ", ".join(s["files"]) if s["files"] else "-"
            lines.append(f"  {s['stage']:<15}{s['state']:<8}{extra:<6} {files}")
        lines.append(f"next: {result['next']}")
    elif command == "addendum":
        lines = [f"created {result['created']}", f"number the first item {result['next_item']}"]
    elif command == "tally":
        lines = [result["markdown"]]
    else:
        lines = [f"{p['severity']}: {p['file']}: {p['message']}" for p in result["problems"]]
        if result["incomplete"]:
            lines.append("incomplete stages: " + ", ".join(result["incomplete"]))
        lines.append("ok" if result["ok"] else "problems found")
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    handlers = {"init": cmd_init, "status": cmd_status, "addendum": cmd_addendum,
                "tally": cmd_tally, "check": cmd_check}
    try:
        result = handlers[args.command](args)
    except CouncilError as exc:
        if getattr(args, "json", False):
            print(json.dumps({"ok": False, "error": str(exc)}))
        else:
            print(f"error: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, indent=None))
    else:
        print(render_text(args.command, result))
    return 0 if result.get("ok", True) else 3


if __name__ == "__main__":
    sys.exit(main())
