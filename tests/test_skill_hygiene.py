"""Packaging hygiene checks: --help output, SKILL.md frontmatter, and repo cleanliness.

Only sys.executable is ever launched (subprocess for --help). SKILL.md's YAML
frontmatter is parsed by hand (simple line parsing), since PyYAML is not a
dependency of this project.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys

import pytest

from conftest import REPO_ROOT, SCRIPT_PATH, SKILL_DIR

SKILL_MD = SKILL_DIR / "SKILL.md"


def _run_help(*args):
    return subprocess.run([sys.executable, str(SCRIPT_PATH), *args, "--help"],
                          capture_output=True, text=True, timeout=30)


# --------------------------------------------------------------------------- --help

class TestHelp:
    def test_top_level_help_exits_0(self):
        result = _run_help()
        assert result.returncode == 0

    def test_top_level_help_mentions_every_subcommand(self):
        result = _run_help()
        for name in ("init", "status", "addendum", "tally", "check"):
            assert name in result.stdout, name

    def test_top_level_help_mentions_exit_codes(self):
        result = _run_help()
        assert "0 ok" in result.stdout
        assert "1 usage" in result.stdout
        assert "3 the check" in result.stdout or "3" in result.stdout

    @pytest.mark.parametrize("subcommand", ["init", "status", "addendum", "tally", "check"])
    def test_subcommand_help_exits_0(self, subcommand):
        result = _run_help(subcommand)
        assert result.returncode == 0, result.stderr


# --------------------------------------------------------------------------- frontmatter

def parse_frontmatter(text: str) -> dict:
    """A small hand-rolled parser for this project's flat SKILL.md frontmatter.

    Handles simple `key: value` lines and one level of nesting (`metadata:` with
    indented `version: ...` under it). Good enough for this file; not a general
    YAML parser.
    """
    lines = text.splitlines()
    assert lines[0].strip() == "---", "SKILL.md must start with a '---' frontmatter fence"
    closing = lines[1:].index("---") + 1
    body = lines[1:closing]

    data: dict = {}
    current_key = None
    for raw_line in body:
        if not raw_line.strip():
            continue
        if raw_line[:1] in (" ", "\t"):
            assert current_key is not None, f"indented line with no parent key: {raw_line!r}"
            key, _, value = raw_line.strip().partition(":")
            data.setdefault(current_key, {})
            assert isinstance(data[current_key], dict), f"{current_key!r} has both a scalar and nested value"
            data[current_key][key.strip()] = value.strip()
        else:
            key, sep, value = raw_line.partition(":")
            assert sep, f"expected 'key: value', got {raw_line!r}"
            key = key.strip()
            value = value.strip()
            # An empty value (e.g. "metadata:") introduces a nested block on the
            # following indented lines, rather than a scalar.
            data[key] = {} if value == "" else value
            current_key = key
    return data


@pytest.fixture(scope="module")
def frontmatter():
    return parse_frontmatter(SKILL_MD.read_text(encoding="utf-8"))


class TestFrontmatter:
    ALLOWED_TOP_KEYS = {"name", "description", "license", "compatibility", "metadata"}
    ALLOWED_METADATA_KEYS = {"version"}

    def test_only_allowed_top_level_keys(self, frontmatter):
        assert set(frontmatter.keys()) <= self.ALLOWED_TOP_KEYS

    def test_only_allowed_metadata_keys(self, frontmatter):
        metadata = frontmatter.get("metadata", {})
        assert set(metadata.keys()) <= self.ALLOWED_METADATA_KEYS

    def test_name_matches_folder_name(self, frontmatter):
        assert frontmatter["name"] == SKILL_DIR.name == "advisory-council"

    def test_description_length_is_in_range(self, frontmatter):
        assert 200 <= len(frontmatter["description"]) <= 1024

    def test_description_has_no_angle_brackets(self, frontmatter):
        assert "<" not in frontmatter["description"]
        assert ">" not in frontmatter["description"]

    def test_metadata_version_matches_marketplace_json(self, frontmatter):
        marketplace = REPO_ROOT / ".claude-plugin" / "marketplace.json"
        if not marketplace.is_file():
            pytest.skip("no .claude-plugin/marketplace.json in this repo yet")
        data = json.loads(marketplace.read_text(encoding="utf-8"))
        plugins = data.get("plugins", [])
        assert plugins, "marketplace.json has no plugins entries"
        skill_version = frontmatter["metadata"]["version"]
        for plugin in plugins:
            if "advisory-council" in " ".join(plugin.get("skills", [])):
                assert plugin["version"] == skill_version
                return
        pytest.fail("no plugin in marketplace.json lists ./advisory-council as a skill")

    def test_metadata_version_matches_changelog(self, frontmatter):
        changelog = REPO_ROOT / "CHANGELOG.md"
        if not changelog.is_file():
            pytest.skip("no CHANGELOG.md in this repo yet")
        text = changelog.read_text(encoding="utf-8")
        versions = re.findall(r"^## \[(\d+\.\d+\.\d+)\]", text, re.MULTILINE)
        assert versions, "CHANGELOG.md has no '## [x.y.z]' entries"
        assert versions[0] == frontmatter["metadata"]["version"]


# --------------------------------------------------------------------------- SKILL.md content

class TestSkillContent:
    def test_skill_md_is_under_500_lines(self):
        lines = SKILL_MD.read_text(encoding="utf-8").splitlines()
        assert len(lines) < 500

    def test_every_referenced_references_path_exists(self):
        text = SKILL_MD.read_text(encoding="utf-8")
        mentioned = sorted(set(re.findall(r"references/[\w./-]+", text)))
        assert mentioned, "expected SKILL.md to mention at least one references/ path"
        missing = [rel for rel in mentioned if not (SKILL_DIR / rel).exists()]
        assert not missing, f"SKILL.md references paths that do not exist: {missing}"


# --------------------------------------------------------------------------- no personal paths

def _forbidden_substrings():
    # Built by concatenation so these literal strings never appear whole in this
    # test file's own source (a plain-text scan of this repo would otherwise flag it).
    return [
        "C:" + "\\Users",
        "/" + "Users/",
        "/" + "home/",
        "D:" + "\\",
        "G:" + "\\",
    ] + _private_words()


def _private_words():
    # Private words (user names, private project names) are never committed: they are
    # read from a git-ignored .private-words file at the repo root (one per line, "#"
    # comments) and from the REPO_CHECK_WORDS environment variable (comma-separated).
    import os
    words = []
    path = REPO_ROOT / ".private-words"
    if path.is_file():
        words += [l.strip() for l in path.read_text(encoding="utf-8").splitlines()
                  if l.strip() and not l.strip().startswith("#")]
    words += [w.strip() for w in os.environ.get("REPO_CHECK_WORDS", "").split(",") if w.strip()]
    return words


def _iter_text_files(*roots):
    this_file = __file__
    for root in roots:
        if not root.exists():
            continue
        paths = [root] if root.is_file() else sorted(root.rglob("*"))
        for path in paths:
            if not path.is_file():
                continue
            if str(path) == str(this_file):
                continue
            try:
                yield path, path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue


def test_no_personal_or_absolute_paths_in_shipped_content():
    forbidden = _forbidden_substrings()
    roots = (SKILL_DIR, REPO_ROOT / "tests", REPO_ROOT / "evals", REPO_ROOT / "README.md")
    offenders = []
    for path, text in _iter_text_files(*roots):
        for needle in forbidden:
            if needle in text:
                offenders.append((str(path.relative_to(REPO_ROOT)), needle))
    assert not offenders, offenders


# --------------------------------------------------------------------------- license / evals

def test_advisory_council_license_matches_repo_root_license_if_present():
    root_license = REPO_ROOT / "LICENSE"
    if not root_license.is_file():
        pytest.skip("no LICENSE file at the repo root")
    skill_license = SKILL_DIR / "LICENSE.txt"
    assert skill_license.is_file(), "repo has a root LICENSE but advisory-council/LICENSE.txt is missing"
    assert skill_license.read_text(encoding="utf-8") == root_license.read_text(encoding="utf-8")


def test_trigger_queries_have_at_least_eight_of_each():
    path = REPO_ROOT / "evals" / "trigger-queries.json"
    if not path.is_file():
        pytest.skip("no evals/trigger-queries.json in this repo yet")
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    for item in data:
        assert isinstance(item, dict)
        assert isinstance(item.get("query"), str)
        assert isinstance(item.get("should_trigger"), bool)
    should = sum(1 for item in data if item["should_trigger"] is True)
    should_not = sum(1 for item in data if item["should_trigger"] is False)
    assert should >= 8, f"only {should} should_trigger=true queries"
    assert should_not >= 8, f"only {should_not} should_trigger=false queries"


# --------------------------------------------------------------------------- python 3.9

def test_no_python_310_only_calls():
    # CI covers 3.9; these calls exist only from 3.10, and 3.9 has no syntax error for them.
    import re
    pattern = re.compile(r"(write_text|read_text)\([^)]*newline=|zip\([^)]*strict=|itertools\.pairwise|\.bit_count\(|kw_only=|slots=True")
    offenders = []
    for path in list(SKILL_DIR.rglob("*.py")) + list(REPO_ROOT.joinpath("tests").glob("*.py")):
        if path.name == "test_skill_hygiene.py":
            continue
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if pattern.search(line):
                offenders.append(f"{path.name}:{n}")
    assert not offenders, offenders
