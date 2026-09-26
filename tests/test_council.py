"""Behavioural tests for council.py: helpers, init, status, addendum, tally and check.

All fixtures use a small fictional roster (a bakery owner, a head baker and a
neighborhood customer, weighted 2/1/1) so headcount and weighted tallies can
disagree. No real people or companies are named anywhere in this file.
"""
from __future__ import annotations

import json

import pytest

from conftest import (
    SEAT_IDS,
    SEAT_SPECS,
    TITLE,
    build_passing_session,
    fill_recommendation,
    fill_round1,
    fill_round2,
    fill_simple,
    init_council,
    set_fields,
    strip_todo,
)


# --------------------------------------------------------------------------- helpers

def test_slugify_lowercases_and_replaces_punctuation(council):
    assert council.slugify("Launch a Paid Tier!!!") == "launch-a-paid-tier"


def test_slugify_empty_text_falls_back_to_decision(council):
    assert council.slugify("   ???   ") == "decision"


def test_slugify_truncates_to_limit_and_strips_trailing_dash(council):
    assert council.slugify("a b c d e f", limit=5) == "a-b-c"


def test_two_digit_pads_single_digits(council):
    assert council.two_digit(1) == "01"
    assert council.two_digit(12) == "12"


class TestParseSeat:
    def test_minimal_id_and_title(self, council):
        seat = council.parse_seat("cfo:Chief Financial Officer")
        assert seat == {"id": "cfo", "title": "Chief Financial Officer", "group": "", "weight": 1}

    def test_with_group(self, council):
        seat = council.parse_seat("cfo:Chief Financial Officer:C-suite")
        assert seat["group"] == "C-suite"
        assert seat["weight"] == 1

    def test_with_group_and_weight(self, council):
        seat = council.parse_seat("cfo:Chief Financial Officer:C-suite:2")
        assert seat["group"] == "C-suite"
        assert seat["weight"] == 2.0

    def test_missing_title_raises(self, council):
        with pytest.raises(council.CouncilError, match="TITLE"):
            council.parse_seat("cfo:")

    def test_bad_weight_raises(self, council):
        with pytest.raises(council.CouncilError, match="not a number"):
            council.parse_seat("cfo:Title:Group:not-a-number")

    def test_too_many_colons_raises(self, council):
        with pytest.raises(council.CouncilError, match="too many"):
            council.parse_seat("a:b:c:d:e")

    def test_no_colon_raises(self, council):
        with pytest.raises(council.CouncilError):
            council.parse_seat("just-a-name")


class TestValidateRoster:
    def _roster(self, seats):
        return {"seats": seats}

    def test_valid_roster_has_no_errors(self, council):
        seats = [{"id": "cfo", "title": "CFO", "weight": 1},
                 {"id": "ops", "title": "Ops", "weight": 1},
                 {"id": "critic", "title": "Critic", "weight": 1}]
        assert council.validate_roster(self._roster(seats)) == []

    def test_bad_id_not_kebab_case(self, council):
        errors = council.validate_roster(self._roster(
            [{"id": "CFO", "title": "x", "weight": 1}]))
        assert any("kebab-case" in e for e in errors)

    def test_reserved_id(self, council):
        errors = council.validate_roster(self._roster(
            [{"id": "tally", "title": "x", "weight": 1}]))
        assert any("reserved" in e for e in errors)

    def test_duplicate_id(self, council):
        errors = council.validate_roster(self._roster(
            [{"id": "a", "title": "x", "weight": 1}, {"id": "a", "title": "y", "weight": 1}]))
        assert any("appears twice" in e for e in errors)

    def test_negative_weight(self, council):
        errors = council.validate_roster(self._roster(
            [{"id": "a", "title": "x", "weight": -1}]))
        assert any("weight must be a number >= 0" in e for e in errors)

    def test_all_zero_weights(self, council):
        errors = council.validate_roster(self._roster(
            [{"id": "a", "title": "x", "weight": 0}]))
        assert any("nobody votes" in e for e in errors)

    def test_too_many_seats(self, council):
        seats = [{"id": f"s{i}", "title": "x", "weight": 1} for i in range(council.MAX_SEATS + 1)]
        errors = council.validate_roster(self._roster(seats))
        assert any("more than the limit" in e for e in errors)


# --------------------------------------------------------------------------- init

class TestInit:
    def test_creates_full_stub_set(self, run, tmp_path):
        folder = init_council(run, tmp_path)
        names = {p.name for p in folder.iterdir()}
        assert "council.json" in names
        assert "COUNCIL.md" in names
        assert any(n.startswith("DOSSIER-01-") for n in names)
        assert "VERIFICATION.md" in names
        assert "ROUND1-TALLY.md" in names
        assert "RECOMMENDATION.md" in names
        for seat_id in SEAT_IDS:
            assert f"ROUND1-{seat_id}.md" in names
            assert f"ROUND2-{seat_id}.md" in names
        for name in names - {"council.json"}:
            assert council_todo_marker_present(folder / name)

    def test_all_stubs_carry_the_todo_marker(self, run, tmp_path, council):
        folder = init_council(run, tmp_path)
        for path in folder.glob("*.md"):
            assert council.TODO_MARKER in path.read_text(encoding="utf-8"), path.name

    def test_zero_weight_seat_gets_no_round_files_but_is_in_council(self, run, tmp_path):
        seats = SEAT_SPECS + ["observer:Silent Observer:Advisors:0"]
        folder = init_council(run, tmp_path, seats=seats)
        names = {p.name for p in folder.iterdir()}
        assert "ROUND1-observer.md" not in names
        assert "ROUND2-observer.md" not in names
        text = (folder / "COUNCIL.md").read_text(encoding="utf-8")
        assert "### observer: Silent Observer" in text

    def test_topic_controls_slug(self, run, tmp_path):
        folder = init_council(run, tmp_path, extra=["--topic", "Bakery Expansion"])
        names = {p.name for p in folder.iterdir()}
        assert any(n == "DOSSIER-01-bakery-expansion.md" for n in names)

    def test_dossier_number_controls_dossier_and_addendum_naming(self, run, tmp_path):
        folder = init_council(run, tmp_path, extra=["--dossier", "2"])
        names = {p.name for p in folder.iterdir()}
        assert any(n.startswith("DOSSIER-02-") for n in names)
        assert not any(n.startswith("DOSSIER-01-") for n in names)
        exit_code, out = run(["addendum", str(folder), "--json"])
        assert exit_code == 0
        assert json.loads(out)["created"] == "ADDENDUM-02A.md"

    def test_rerun_creates_missing_stubs_without_overwriting_edited_files(self, run, tmp_path):
        folder = init_council(run, tmp_path)
        (folder / "VERIFICATION.md").unlink()
        edited = "# My hand-written council notes\nNo marker here.\n"
        (folder / "COUNCIL.md").write_text(edited, encoding="utf-8")

        exit_code, out = run(["init", str(folder), "--json"])
        result = json.loads(out)
        assert exit_code == 0
        assert "VERIFICATION.md" in result["created"]
        assert "COUNCIL.md" in result["kept"]
        assert (folder / "COUNCIL.md").read_text(encoding="utf-8") == edited
        assert (folder / "VERIFICATION.md").is_file()

    def test_init_with_seat_on_existing_council_json_is_an_error(self, run, tmp_path):
        folder = init_council(run, tmp_path)
        exit_code, out = run(["init", str(folder), "--seat", "extra:Extra Seat"])
        assert exit_code == 1

    def test_missing_title_is_an_error(self, council, capsys, tmp_path):
        folder = tmp_path / "council"
        exit_code = council.main(["init", str(folder), "--seat", "cfo:CFO"])
        assert exit_code == 1
        assert "--title" in capsys.readouterr().err

    def test_missing_seats_is_an_error(self, council, capsys, tmp_path):
        folder = tmp_path / "council"
        exit_code = council.main(["init", str(folder), "--title", "Some decision"])
        assert exit_code == 1
        assert "--seat" in capsys.readouterr().err

    def test_roster_reuses_seats_from_another_council_json(self, run, tmp_path):
        first = init_council(run, tmp_path, name="first")
        second_folder = tmp_path / "second"
        exit_code, out = run(["init", str(second_folder), "--title", "Follow-up decision",
                              "--roster", str(first / "council.json")])
        assert exit_code == 0
        roster = json.loads((second_folder / "council.json").read_text(encoding="utf-8"))
        assert [s["id"] for s in roster["seats"]] == SEAT_IDS

    def test_warns_when_fewer_than_three_voting_seats(self, run, tmp_path):
        exit_code, out = run(["init", str(tmp_path / "council"), "--title", "Small decision",
                              "--seat", "cfo:CFO", "--json"])
        result = json.loads(out)
        assert any("voting seats" in w for w in result["warnings"])

    def test_warns_when_more_than_nine_voting_seats(self, run, tmp_path):
        seats = [f"s{i}:Seat {i}" for i in range(10)]
        exit_code, out = run(["init", str(tmp_path / "council"), "--title", "Big decision", "--json"]
                             + [a for spec in seats for a in ("--seat", spec)])
        result = json.loads(out)
        assert any("voting seats" in w for w in result["warnings"])

    def test_json_output_is_valid_json(self, run, tmp_path):
        exit_code, out = run(["init", str(tmp_path / "council"), "--title", TITLE, "--json"]
                             + [a for spec in SEAT_SPECS for a in ("--seat", spec)])
        result = json.loads(out)
        assert result["ok"] is True
        assert exit_code == 0


def council_todo_marker_present(path):
    if path.suffix != ".md":
        return True
    return "<!-- council:todo -->" in path.read_text(encoding="utf-8")


# --------------------------------------------------------------------------- status

class TestStatus:
    def test_next_step_moves_through_every_stage(self, run, tmp_path):
        folder = init_council(run, tmp_path)

        def next_step():
            exit_code, out = run(["status", str(folder), "--json"])
            assert exit_code == 0
            return json.loads(out)["next"]

        assert next_step() == "fill the persona cards in COUNCIL.md and confirm the roster with the user"

        fill_simple(folder / "COUNCIL.md")
        assert "dossier" in next_step()

        roster = json.loads((folder / "council.json").read_text(encoding="utf-8"))
        dossier_name = f"DOSSIER-{roster['dossier']:02d}-{roster['slug']}.md"
        fill_simple(folder / dossier_name)
        step = next_step()
        assert "Round 1" in step
        assert "cfo, ops, critic" in step

        fill_round1(folder, "cfo")
        step = next_step()
        assert "ops, critic" in step
        assert "cfo" not in step.split("pending:")[1]

        fill_round1(folder, "ops")
        fill_round1(folder, "critic")
        assert "verifier" in next_step().lower()

        fill_simple(folder / "VERIFICATION.md")
        assert "tally" in next_step().lower()

        fill_simple(folder / "ROUND1-TALLY.md")
        step = next_step()
        assert "Round 2" in step
        assert "cfo, ops, critic" in step

        for seat_id in SEAT_IDS:
            fill_round2(folder, seat_id)
        assert "recommendation" in next_step().lower() or "RECOMMENDATION" in next_step()

        fill_recommendation(folder)
        assert next_step() == "complete; run `council.py check --final` and report"

    def test_addendum_todo_stub_is_the_next_step(self, run, tmp_path):
        folder = init_council(run, tmp_path)
        fill_simple(folder / "COUNCIL.md")
        roster = json.loads((folder / "council.json").read_text(encoding="utf-8"))
        dossier_name = f"DOSSIER-{roster['dossier']:02d}-{roster['slug']}.md"
        fill_simple(folder / dossier_name)
        for seat_id in SEAT_IDS:
            fill_round1(folder, seat_id)
        fill_simple(folder / "VERIFICATION.md")

        exit_code, out = run(["addendum", str(folder)])
        assert exit_code == 0

        exit_code, out = run(["status", str(folder), "--json"])
        result = json.loads(out)
        assert "addendum" in result["next"]


# --------------------------------------------------------------------------- addendum

class TestAddendum:
    def test_first_addendum_is_A_second_is_B(self, run, tmp_path):
        folder = init_council(run, tmp_path)
        exit_code, out = run(["addendum", str(folder), "--json"])
        assert json.loads(out)["created"] == "ADDENDUM-01A.md"
        exit_code, out = run(["addendum", str(folder), "--json"])
        assert json.loads(out)["created"] == "ADDENDUM-01B.md"

    def test_next_item_continues_from_highest_heading_in_earlier_addenda(self, run, tmp_path):
        folder = init_council(run, tmp_path)
        run(["addendum", str(folder)])
        addendum_a = folder / "ADDENDUM-01A.md"
        text = addendum_a.read_text(encoding="utf-8")
        text = text.replace("## 1. <short title>", "## 7. A much later item")
        addendum_a.write_text(text, encoding="utf-8")

        exit_code, out = run(["addendum", str(folder), "--json"])
        result = json.loads(out)
        assert result["created"] == "ADDENDUM-01B.md"
        assert result["next_item"] == 8
        assert "## 8. <short title>" in (folder / "ADDENDUM-01B.md").read_text(encoding="utf-8")


# --------------------------------------------------------------------------- tally round 1

class TestTallyRound1:
    def test_incomplete_when_a_seat_is_missing(self, run, tmp_path):
        folder = init_council(run, tmp_path)
        fill_round1(folder, "cfo")
        fill_round1(folder, "ops")
        # critic left as a stub

        exit_code, out = run(["tally", str(folder), "--round", "1", "--json"])
        result = json.loads(out)
        assert exit_code == 3
        assert result["missing"] == ["critic"]
        exit_code, out = run(["tally", str(folder), "--round", "1"])
        assert "INCOMPLETE" in out

    def test_row_per_seat_once_all_report(self, run, tmp_path):
        folder = init_council(run, tmp_path)
        for seat_id in SEAT_IDS:
            fill_round1(folder, seat_id, position=f"Position from {seat_id}")

        exit_code, out = run(["tally", str(folder), "--round", "1", "--json"])
        result = json.loads(out)
        assert exit_code == 0
        assert result["missing"] == []
        assert {r["seat"] for r in result["rows"]} == set(SEAT_IDS)
        cfo_row = next(r for r in result["rows"] if r["seat"] == "cfo")
        assert cfo_row["position"] == "Position from cfo"

    def test_placeholder_position_counts_as_unfilled(self, run, tmp_path):
        folder = init_council(run, tmp_path)
        fill_round1(folder, "cfo")
        fill_round1(folder, "ops")
        # critic: strip the marker but leave the Position placeholder untouched.
        path = folder / "ROUND1-critic.md"
        path.write_text(strip_todo(path.read_text(encoding="utf-8")), encoding="utf-8")

        exit_code, out = run(["tally", str(folder), "--round", "1", "--json"])
        result = json.loads(out)
        assert exit_code == 3
        assert result["missing"] == ["critic"]


# --------------------------------------------------------------------------- tally round 2

class TestTallyRound2:
    def test_votes_parsed_by_letter_or_other(self, run, tmp_path):
        folder = init_council(run, tmp_path)
        fill_round2(folder, "cfo", vote="B")
        fill_round2(folder, "ops", vote="Other: try a pop-up first")
        fill_round2(folder, "critic", vote="b")  # lower-case, no letter match -> Other

        exit_code, out = run(["tally", str(folder), "--round", "2", "--json"])
        result = json.loads(out)
        assert exit_code == 0
        by_seat = {r["seat"]: r["option"] for r in result["rows"]}
        assert by_seat["cfo"] == "B"
        assert by_seat["ops"] == "Other"
        assert by_seat["critic"] == "Other"

    def test_capitalized_option_word_and_bold_letter_count_as_the_letter(self, run, tmp_path):
        """"Option B - reason" and "**B**" are counted as option B, not Other."""
        folder = init_council(run, tmp_path)
        fill_round2(folder, "cfo", vote="Option B - reason")
        fill_round2(folder, "ops", vote="**B**")
        fill_round2(folder, "critic", vote="B")

        exit_code, out = run(["tally", str(folder), "--round", "2", "--json"])
        result = json.loads(out)
        by_seat = {r["seat"]: r["option"] for r in result["rows"]}
        assert by_seat == {"cfo": "B", "ops": "B", "critic": "B"}

    def test_headcount_and_weighted_totals_with_unequal_weights(self, run, tmp_path):
        folder = init_council(run, tmp_path)
        # cfo weight=2, ops weight=1, critic weight=1 (see SEAT_SPECS)
        fill_round2(folder, "cfo", vote="B")
        fill_round2(folder, "ops", vote="B")
        fill_round2(folder, "critic", vote="Other: keep the single shop")

        exit_code, out = run(["tally", str(folder), "--round", "2", "--json"])
        result = json.loads(out)
        totals = {t["option"]: t for t in result["totals"]}
        assert totals["B"]["count"] == 2
        assert totals["B"]["weight"] == 3
        assert totals["Other"]["count"] == 1
        assert totals["Other"]["weight"] == 1
        # ordered by weight descending, so B (the majority) is listed first
        assert result["totals"][0]["option"] == "B"

    def test_changed_list_contains_seats_that_changed_their_vote(self, run, tmp_path):
        folder = init_council(run, tmp_path)
        fill_round2(folder, "cfo", vote="B", changed="no")
        fill_round2(folder, "ops", vote="B",
                   changed="yes: convinced by the addendum's revised cost estimate")
        fill_round2(folder, "critic", vote="B", changed="no")

        exit_code, out = run(["tally", str(folder), "--round", "2", "--json"])
        result = json.loads(out)
        assert result["changed"] == ["ops"]

    def test_rows_ordered_by_roster_order(self, run, tmp_path):
        folder = init_council(run, tmp_path)
        for seat_id in SEAT_IDS:
            fill_round2(folder, seat_id)
        exit_code, out = run(["tally", str(folder), "--round", "2", "--json"])
        result = json.loads(out)
        assert [r["seat"] for r in result["rows"]] == SEAT_IDS


# --------------------------------------------------------------------------- check

class TestCheck:
    def test_fully_filled_session_passes_final_check(self, run, tmp_path):
        folder = build_passing_session(run, tmp_path)
        exit_code, out = run(["check", str(folder), "--final", "--json"])
        result = json.loads(out)
        assert exit_code == 0
        assert result["ok"] is True
        assert not any(p["severity"] == "error" for p in result["problems"])

    def test_missing_persona_card_heading(self, run, tmp_path):
        folder = build_passing_session(run, tmp_path)
        path = folder / "COUNCIL.md"
        # Renaming the id itself (not just appending to it) breaks the "### cfo" match,
        # since a trailing "-renamed" would still satisfy the \b word boundary check.
        text = path.read_text(encoding="utf-8").replace("### cfo:", "### finance-lead:")
        path.write_text(text, encoding="utf-8")

        exit_code, out = run(["check", str(folder), "--json"])
        result = json.loads(out)
        assert exit_code == 3
        assert any("persona card heading" in p["message"] for p in result["problems"])

    def test_round1_missing_position(self, run, tmp_path):
        folder = build_passing_session(run, tmp_path)
        path = folder / "ROUND1-cfo.md"
        text = path.read_text(encoding="utf-8")
        text = text.replace("**Position:** Launch in one region first",
                            "**Position:** <one line, in this seat's own words>")
        path.write_text(text, encoding="utf-8")

        exit_code, out = run(["check", str(folder), "--json"])
        result = json.loads(out)
        assert exit_code == 3
        assert any(p["file"] == "ROUND1-cfo.md" and "Position" in p["message"]
                   for p in result["problems"])

    def test_round2_changed_vote_with_no_reason(self, run, tmp_path):
        folder = build_passing_session(run, tmp_path)
        path = folder / "ROUND2-ops.md"
        text = path.read_text(encoding="utf-8")
        text = set_fields(text, **{"Changed_from_round_1": "yes"})
        path.write_text(text, encoding="utf-8")

        exit_code, out = run(["check", str(folder), "--json"])
        result = json.loads(out)
        assert exit_code == 3
        assert any(p["file"] == "ROUND2-ops.md" and "without naming" in p["message"]
                   for p in result["problems"])

    def test_addendum_with_a_vote_line(self, run, tmp_path):
        folder = build_passing_session(run, tmp_path)
        run(["addendum", str(folder)])
        path = folder / "ADDENDUM-01A.md"
        text = strip_todo(path.read_text(encoding="utf-8"))
        text += "\n**Vote:** B\n"
        path.write_text(text, encoding="utf-8")

        exit_code, out = run(["check", str(folder), "--json"])
        result = json.loads(out)
        assert exit_code == 3
        assert any(p["file"] == "ADDENDUM-01A.md" and "position or vote" in p["message"]
                   for p in result["problems"])

    def test_verification_without_any_verdict_word(self, run, tmp_path):
        folder = build_passing_session(run, tmp_path)
        path = folder / "VERIFICATION.md"
        path.write_text("# VERIFICATION\n\nEverything looked fine, no notes.\n", encoding="utf-8")

        exit_code, out = run(["check", str(folder), "--json"])
        result = json.loads(out)
        assert exit_code == 3
        assert any(p["file"] == "VERIFICATION.md" and "no verdicts" in p["message"]
                   for p in result["problems"])

    def test_tally_written_while_a_round1_is_still_a_stub(self, run, tmp_path):
        folder = init_council(run, tmp_path)
        fill_simple(folder / "ROUND1-TALLY.md")
        # ROUND1-*.md files are all left as stubs.

        exit_code, out = run(["check", str(folder), "--json"])
        result = json.loads(out)
        assert exit_code == 3
        assert any(p["file"] == "ROUND1-TALLY.md" and "before every Round 1" in p["message"]
                   for p in result["problems"])

    def test_tally_omitting_a_seat_id(self, run, tmp_path):
        folder = build_passing_session(run, tmp_path)
        path = folder / "ROUND1-TALLY.md"
        text = path.read_text(encoding="utf-8").replace("cfo", "")
        path.write_text(text, encoding="utf-8")

        exit_code, out = run(["check", str(folder), "--json"])
        result = json.loads(out)
        assert exit_code == 3
        assert any(p["file"] == "ROUND1-TALLY.md" and "cfo" in p["message"]
                   for p in result["problems"])

    def test_round2_done_before_tally(self, run, tmp_path):
        folder = init_council(run, tmp_path)
        fill_round2(folder, "cfo")
        # ROUND1-TALLY.md is left as a stub.

        exit_code, out = run(["check", str(folder), "--json"])
        result = json.loads(out)
        assert exit_code == 3
        assert any(p["file"] == "ROUND2" and "cfo" in p["message"] for p in result["problems"])

    def test_recommendation_before_all_round2_votes(self, run, tmp_path, council):
        folder = build_passing_session(run, tmp_path)
        # Put the marker back so the round2 stage is genuinely incomplete (not just a
        # seat with an unfilled field, which file_state would still count as "done").
        path = folder / "ROUND2-critic.md"
        text = path.read_text(encoding="utf-8")
        path.write_text(council.TODO_MARKER + "\n" + text, encoding="utf-8")

        exit_code, out = run(["check", str(folder), "--json"])
        result = json.loads(out)
        assert exit_code == 3
        assert any(p["file"] == "RECOMMENDATION.md" and "before every Round 2" in p["message"]
                   for p in result["problems"])

    def test_recommendation_missing_required_section(self, run, tmp_path):
        folder = build_passing_session(run, tmp_path)
        path = folder / "RECOMMENDATION.md"
        text = path.read_text(encoding="utf-8").replace("## 3. Dissent", "## 3. Feedback")
        path.write_text(text, encoding="utf-8")

        exit_code, out = run(["check", str(folder), "--json"])
        result = json.loads(out)
        assert exit_code == 3
        assert any(p["file"] == "RECOMMENDATION.md" and "'dissent'" in p["message"]
                   for p in result["problems"])

    def test_recommendation_missing_council_vote_line(self, run, tmp_path):
        folder = build_passing_session(run, tmp_path)
        path = folder / "RECOMMENDATION.md"
        text = path.read_text(encoding="utf-8")
        text = text.replace("**Council vote:** Option B: 2 of 3 seats, weighted 3 of 4.",
                            "**Council vote:** <option X: n of 3 seats, weighted w of W>.")
        path.write_text(text, encoding="utf-8")

        exit_code, out = run(["check", str(folder), "--json"])
        result = json.loads(out)
        assert exit_code == 3
        assert any(p["file"] == "RECOMMENDATION.md" and "Council vote" in p["message"]
                   for p in result["problems"])

    def test_unfilled_placeholder_in_a_done_file_is_only_a_warning(self, run, tmp_path):
        folder = init_council(run, tmp_path)
        fill_simple(folder / "COUNCIL.md")  # placeholders remain in section 1, only marker removed

        exit_code, out = run(["check", str(folder), "--json"])
        result = json.loads(out)
        assert exit_code == 0
        assert any(p["severity"] == "warning" and p["file"] == "COUNCIL.md"
                   for p in result["problems"])

    def test_final_with_incomplete_stages(self, run, tmp_path):
        folder = init_council(run, tmp_path)  # nothing filled in at all

        exit_code, out = run(["check", str(folder), "--final", "--json"])
        result = json.loads(out)
        assert exit_code == 3
        assert result["incomplete"]
        assert any(p["message"] == "stage not complete" for p in result["problems"])


# --------------------------------------------------------------------------- error paths

class TestErrorPaths:
    @pytest.mark.parametrize("command", [
        ["status", "{folder}"],
        ["tally", "{folder}", "--round", "1"],
        ["check", "{folder}"],
    ])
    def test_missing_council_json_is_exit_1(self, run, tmp_path, command):
        folder = tmp_path / "empty"
        folder.mkdir()
        argv = [a.format(folder=str(folder)) for a in command]
        exit_code, out = run(argv)
        assert exit_code == 1

    def test_missing_council_json_message_mentions_init(self, run, tmp_path, council):
        folder = tmp_path / "empty"
        folder.mkdir()
        with pytest.raises(council.CouncilError, match="init"):
            council.load_roster(folder)

    def test_invalid_json_is_exit_1(self, run, tmp_path):
        folder = tmp_path / "council"
        folder.mkdir()
        (folder / "council.json").write_text("{not valid json", encoding="utf-8")
        exit_code, out = run(["status", str(folder)])
        assert exit_code == 1
