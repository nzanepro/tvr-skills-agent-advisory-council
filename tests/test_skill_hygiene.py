"""Packaging hygiene checks: --help output, SKILL.md frontmatter, and repo cleanliness.

Only sys.executable is ever launched (subprocess for --help). SKILL.md's YAML
frontmatter is read by a small strict parser in this file, which needs no extra
package and rejects anything a real YAML parser might read differently (such as
an unquoted value containing ": "). When PyYAML is installed (CI installs it),
the frontmatter is also parsed with yaml.safe_load and both results must agree.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import REPO_ROOT, SCRIPT_PATH, SKILL_DIR

SKILL_MD = SKILL_DIR / "SKILL.md"
PLUGIN_JSON = REPO_ROOT / ".claude-plugin" / "plugin.json"
MARKETPLACE_JSON = REPO_ROOT / ".claude-plugin" / "marketplace.json"


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

class FrontmatterError(ValueError):
    """The frontmatter is not in the strict subset of YAML this project uses."""


_KEY_LINE = re.compile(r"^(?P<indent> *)(?P<key>[A-Za-z_][A-Za-z0-9_-]*):(?: (?P<value>.*))?$")
# A plain (unquoted) YAML scalar may not start with one of these indicators.
_PLAIN_START_FORBIDDEN = tuple("[]{}#&*!|>'\"%@`,") + ("- ", "? ", ": ")
# Plain scalars YAML would read as something other than a string.
_NON_STRING_PLAIN = re.compile(
    r"^(?:~|null|Null|NULL|true|True|TRUE|false|False|FALSE|yes|Yes|YES|no|No|NO|on|On|ON|off|Off|OFF"
    r"|[-+]?(?:\d[\d_]*)(?:\.\d*)?(?:[eE][-+]?\d+)?|[-+]?\.(?:inf|Inf|INF)|\.(?:nan|NaN|NAN))$"
)


def _parse_scalar(value: str, where: str) -> str:
    """Parse one single-line scalar strictly and return its string value.

    Accepts a double-quoted string (read with JSON rules, which match YAML's for
    the escapes allowed here), a single-quoted string, or a plain scalar that
    YAML would read as exactly the same text. Rejects everything else, notably
    an unquoted value containing ": " or " #", which YAML parsers reject or
    truncate while a naive split on the first colon would accept.
    """
    if value.startswith('"'):
        if len(value) < 2 or not value.endswith('"'):
            raise FrontmatterError(f"{where}: unterminated double-quoted string")
        try:
            parsed = json.loads(value)
        except ValueError as exc:
            raise FrontmatterError(f"{where}: invalid double-quoted string ({exc})") from None
        if not isinstance(parsed, str):
            raise FrontmatterError(f"{where}: expected a string")
        return parsed
    if value.startswith("'"):
        inner = value[1:-1]
        if len(value) < 2 or not value.endswith("'") or "'" in inner.replace("''", ""):
            raise FrontmatterError(f"{where}: invalid single-quoted string")
        return inner.replace("''", "'")
    if value != value.strip():
        raise FrontmatterError(f"{where}: trailing whitespace in a plain value")
    if value.startswith(_PLAIN_START_FORBIDDEN) or value in ("-", "?", ":"):
        raise FrontmatterError(
            f"{where}: a plain value cannot start with {value[:2]!r}; quote it")
    if ": " in value or value.endswith(":"):
        raise FrontmatterError(
            f"{where}: an unquoted value cannot contain ': ' (YAML reads it as a mapping); "
            "wrap the value in double quotes")
    if " #" in value or "\t#" in value:
        raise FrontmatterError(
            f"{where}: an unquoted value cannot contain ' #' (YAML starts a comment there); "
            "wrap the value in double quotes")
    if _NON_STRING_PLAIN.match(value):
        raise FrontmatterError(
            f"{where}: {value!r} is not a string in YAML; quote it")
    return value


def parse_frontmatter(text: str) -> dict:
    """Parse this project's SKILL.md frontmatter with a small strict parser.

    Accepts only the subset of YAML the file needs: top-level `key: value` lines
    and blocks of two-space-indented `key: value` lines under a `key:` line, where
    every value is a single-line string scalar (see _parse_scalar). Anything
    outside that subset raises FrontmatterError instead of being guessed at, so a
    value that a YAML parser would reject or read differently fails the tests.
    """
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise FrontmatterError("SKILL.md must start with a '---' frontmatter fence")
    try:
        closing = lines[1:].index("---") + 1
    except ValueError:
        raise FrontmatterError("SKILL.md frontmatter has no closing '---' fence") from None
    body = lines[1:closing]

    data: dict = {}
    parent = None
    for number, raw_line in enumerate(body, start=2):
        where = f"frontmatter line {number}"
        if not raw_line.strip():
            continue
        if "\t" in raw_line[: len(raw_line) - len(raw_line.lstrip())]:
            raise FrontmatterError(f"{where}: tabs are not allowed in YAML indentation")
        if raw_line.lstrip().startswith("#"):
            continue
        match = _KEY_LINE.match(raw_line)
        if not match:
            raise FrontmatterError(f"{where}: expected 'key: value', got {raw_line!r}")
        indent, key, value = match.group("indent"), match.group("key"), match.group("value")
        if indent == "":
            if key in data:
                raise FrontmatterError(f"{where}: duplicate key {key!r}")
            if value is None or value == "":
                data[key] = {}
                parent = key
            else:
                data[key] = _parse_scalar(value, where)
                parent = None
        elif indent == "  ":
            if parent is None:
                raise FrontmatterError(f"{where}: indented line with no parent key")
            if key in data[parent]:
                raise FrontmatterError(f"{where}: duplicate key {parent}.{key}")
            if value is None or value == "":
                raise FrontmatterError(f"{where}: only one level of nesting is supported")
            data[parent][key] = _parse_scalar(value, where)
        else:
            raise FrontmatterError(f"{where}: indent nested keys by exactly two spaces")
    for key, value in data.items():
        if value == {}:
            raise FrontmatterError(f"{key!r} has no value and no nested keys")
    return data


@pytest.fixture(scope="module")
def frontmatter():
    return parse_frontmatter(SKILL_MD.read_text(encoding="utf-8"))


class TestFrontmatterParser:
    """The strict parser itself: it must reject what YAML parsers reject."""

    def test_unquoted_colon_space_in_a_value_is_rejected(self):
        # The 0.1.0 SKILL.md had exactly this shape and failed PyYAML.
        text = "---\nname: x\ndescription: Runs a council on a decision: seats personas\n---\n"
        with pytest.raises(FrontmatterError, match="': '"):
            parse_frontmatter(text)

    def test_quoted_colon_space_is_accepted(self):
        text = '---\nname: x\ndescription: "Runs a council on a decision: seats personas"\n---\n'
        assert parse_frontmatter(text)["description"] == "Runs a council on a decision: seats personas"

    def test_single_quoted_value_unescapes_doubled_quotes(self):
        text = "---\nname: x\ndescription: 'it''s: fine'\n---\n"
        assert parse_frontmatter(text)["description"] == "it's: fine"

    @pytest.mark.parametrize("value", [
        "text # a comment", "[a, b]", "- item", "> folded", "*alias", "true", "1.5", "",
        '"unterminated', "'bad ' quote'",
    ])
    def test_values_yaml_would_read_differently_are_rejected(self, value):
        text = f"---\nname: x\ndescription: {value}\n---\n"
        with pytest.raises(FrontmatterError):
            parse_frontmatter(text)

    def test_nested_block_and_semver_string(self):
        text = "---\nname: x\nmetadata:\n  version: 1.2.3\n---\n"
        assert parse_frontmatter(text)["metadata"] == {"version": "1.2.3"}

    def test_missing_closing_fence_is_rejected(self):
        with pytest.raises(FrontmatterError):
            parse_frontmatter("---\nname: x\n")


def test_frontmatter_parses_with_pyyaml_to_the_same_values(frontmatter):
    # CI installs PyYAML so this always runs there; locally it is optional.
    yaml = pytest.importorskip("yaml")
    lines = SKILL_MD.read_text(encoding="utf-8").splitlines()
    closing = lines[1:].index("---") + 1
    loaded = yaml.safe_load("\n".join(lines[1:closing]))
    assert isinstance(loaded, dict)
    assert loaded == frontmatter


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

    def test_metadata_version_matches_plugin_json(self, frontmatter):
        manifest = json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))
        assert manifest["version"] == frontmatter["metadata"]["version"]

    def test_metadata_version_matches_marketplace_json(self, frontmatter):
        data = json.loads(MARKETPLACE_JSON.read_text(encoding="utf-8"))
        skill_version = frontmatter["metadata"]["version"]
        assert data["version"] == skill_version
        # plugin.json carries the plugin's version; an entry version, if one is
        # ever added back, must agree with it.
        for plugin in data.get("plugins", []):
            if "version" in plugin:
                assert plugin["version"] == skill_version, plugin["name"]

    def test_metadata_version_matches_changelog(self, frontmatter):
        changelog = REPO_ROOT / "CHANGELOG.md"
        if not changelog.is_file():
            pytest.skip("no CHANGELOG.md in this repo yet")
        text = changelog.read_text(encoding="utf-8")
        versions = re.findall(r"^## \[(\d+\.\d+\.\d+)\]", text, re.MULTILINE)
        assert versions, "CHANGELOG.md has no '## [x.y.z]' entries"
        assert versions[0] == frontmatter["metadata"]["version"]


# --------------------------------------------------------------------------- plugin manifests

class TestPluginManifests:
    """plugin.json is the plugin's manifest; the marketplace entry only lists it.

    `claude plugin validate` does not catch the combination tested below: with a
    plugin.json present, an entry that sets "strict": false and also declares
    components (skills, commands, ...) makes the plugin fail to load with
    "conflicting manifests".
    """

    COMPONENT_KEYS = ("commands", "agents", "skills", "hooks", "outputStyles", "themes")

    @pytest.fixture(scope="class")
    def manifest(self):
        return json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))

    @pytest.fixture(scope="class")
    def entry(self):
        data = json.loads(MARKETPLACE_JSON.read_text(encoding="utf-8"))
        entries = [p for p in data["plugins"] if p["name"] == "council"]
        assert len(entries) == 1, "marketplace.json must list the council plugin once"
        return entries[0]

    def test_plugin_name_is_council(self, manifest, entry):
        # Users install council@<marketplace> and call /council:advisory-council.
        assert manifest["name"] == entry["name"] == "council"

    def test_plugin_json_declares_the_skill(self, manifest):
        assert manifest["skills"] == ["./advisory-council"]
        assert (REPO_ROOT / "advisory-council" / "SKILL.md").is_file()

    def test_entry_source_is_the_repo_root(self, entry):
        assert entry["source"] == "./"

    def test_entry_does_not_conflict_with_plugin_json(self, entry):
        declared = [key for key in self.COMPONENT_KEYS if key in entry]
        assert not declared, f"declare components in plugin.json, not the entry: {declared}"

    def test_required_metadata_is_set(self, manifest):
        for key in ("version", "description", "author", "license", "homepage", "repository",
                    "keywords"):
            assert manifest.get(key), key
        assert manifest["author"].get("name")
        assert manifest["license"] == "MIT"

    def test_entry_display_fields_match_plugin_json(self, manifest, entry):
        # Entry display fields win over plugin.json in listings, so keep them equal.
        for key in ("displayName", "description", "author", "homepage", "repository",
                    "license", "keywords"):
            if key in entry:
                assert entry[key] == manifest.get(key), key


# --------------------------------------------------------------------------- plugin icon

class TestPluginIcon:
    """The directory listing shows .claude-plugin/icon.svg (square, at least 128 px).

    The icon must be a plain, self-contained SVG: well-formed XML, a square viewBox,
    and nothing that runs or loads (no script, event handlers, external links,
    embedded images or foreign objects).
    """

    ICON = REPO_ROOT / ".claude-plugin" / "icon.svg"
    SVG_NS = "{http://www.w3.org/2000/svg}"

    @pytest.fixture(scope="class")
    def text(self):
        assert self.ICON.is_file(), "missing .claude-plugin/icon.svg"
        return self.ICON.read_text(encoding="utf-8")

    @pytest.fixture(scope="class")
    def root(self, text):
        # A DOCTYPE could declare entities; the icon has no need for one.
        assert "<!DOCTYPE" not in text.upper() and "<!ENTITY" not in text.upper()
        import xml.etree.ElementTree as ET
        return ET.fromstring(text)

    def test_icon_is_small_text(self, text):
        assert len(text.encode("utf-8")) < 16 * 1024

    def test_root_is_svg_with_a_square_viewbox_of_at_least_128(self, root):
        assert root.tag == self.SVG_NS + "svg"
        numbers = [float(n) for n in root.get("viewBox", "").replace(",", " ").split()]
        assert len(numbers) == 4, root.get("viewBox")
        width, height = numbers[2], numbers[3]
        assert width == height >= 128
        for attribute in ("width", "height"):
            if root.get(attribute) is not None:
                assert float(root.get(attribute).replace("px", "")) >= 128, attribute
        assert root.get("width") == root.get("height")

    def test_no_script_links_or_embedded_content(self, root, text):
        forbidden_tags = {"script", "foreignObject", "image", "use", "a", "iframe", "style"}
        for element in root.iter():
            tag = element.tag.replace(self.SVG_NS, "")
            assert tag not in forbidden_tags, tag
            for name, value in element.attrib.items():
                local = name.rsplit("}", 1)[-1]
                assert local != "href", f"{tag} has an href"
                assert not local.lower().startswith("on"), f"{tag} has an event handler {local}"
                assert "url(" not in value, f"{tag} {local} refers to a url()"
        # The SVG namespace declaration is the one URL the file may contain.
        lowered = text.lower().replace('xmlns="http://www.w3.org/2000/svg"', "")
        for needle in ("javascript:", "data:", "http://", "https://", "@import"):
            assert needle not in lowered, needle

    def test_plugin_json_points_at_the_icon(self):
        manifest = json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))
        assert manifest.get("icon") == "./.claude-plugin/icon.svg"


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
    # comments) and nowhere else.
    words = []
    path = REPO_ROOT / ".private-words"
    if path.is_file():
        words += [l.strip() for l in path.read_text(encoding="utf-8").splitlines()
                  if l.strip() and not l.strip().startswith("#")]
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
    roots = (SKILL_DIR, REPO_ROOT / "tests", REPO_ROOT / "evals", REPO_ROOT / ".claude-plugin",
             REPO_ROOT / ".github") + tuple(sorted(REPO_ROOT.glob("*.md")))
    offenders = []
    for path, text in _iter_text_files(*roots):
        for needle in forbidden:
            if needle in text:
                offenders.append((str(path.relative_to(REPO_ROOT)), needle))
    assert not offenders, offenders


# --------------------------------------------------------------------------- no shell variables

# A dollar sign before a name, an opening brace or an opening parenthesis (a variable
# or command substitution), PowerShell's env: drive after a dollar sign, and a cmd
# name between percent signs. The dollar sign is written as the class [$] so this
# line does not itself match.
_SHELL_VARIABLE = re.compile(r"[$](?:[A-Za-z_{(]|env:)|%[A-Za-z_][A-Za-z0-9_]*%")


def _iter_repo_text_files():
    # Every text file in the repo, this one included, except the CI workflows and what
    # .gitignore keeps out (dot directories other than .claude-plugin and .github, such
    # as .git, .venv and local worktrees; caches; council sessions; .private-words).
    import os
    skipped_dirs = {"__pycache__", ".pytest_cache", "council"}
    for directory, dirnames, filenames in os.walk(REPO_ROOT):
        here = Path(directory)
        dirnames[:] = sorted(
            name for name in dirnames
            if name not in skipped_dirs and not name.endswith(".egg-info")
            and (not name.startswith(".") or name in (".claude-plugin", ".github"))
            and here / name != REPO_ROOT / ".github" / "workflows")
        for name in sorted(filenames):
            if name == ".private-words" or name.endswith((".pyc", ".pyo", ".skill")):
                continue
            path = here / name
            try:
                yield path, path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue


def test_no_shell_variables_or_command_substitution_in_any_repo_file():
    # The plugin directory's scanner treats every file in the repo, tests included, as
    # plugin surface. It reads a variable such as the shell's current-directory
    # variable in a file that also spells a remote URL host as a credential from the
    # installer's machine that could be sent off it ("Uses a credential from the
    # user's machine"), and holds the plugin for review. Install commands use literal
    # paths instead, and comments describe such variables in words. The workflows
    # under .github/workflows are CI, not plugin content, and legitimately use them.
    offenders = []
    for path, text in _iter_repo_text_files():
        for number, line in enumerate(text.splitlines(), 1):
            if _SHELL_VARIABLE.search(line):
                offenders.append(f"{path.relative_to(REPO_ROOT)}:{number}: {line.strip()}")
    assert not offenders, offenders


def test_shell_variable_pattern_catches_each_form():
    # Fixtures are built by concatenation so this file never spells one itself.
    dollar, percent = "$", "%"
    for sample in (dollar + "NAME", dollar + "{NAME}", dollar + "(date)",
                   dollar + "env:NAME", percent + "NAME" + percent):
        assert _SHELL_VARIABLE.search("cd " + sample + "/x"), sample
    for sample in ("costs " + dollar + "5M", "50" + percent + " of seats", "a " + dollar + " b"):
        assert not _SHELL_VARIABLE.search(sample), sample


def _env_reads():
    # Built by concatenation so this file never spells one itself, nor even the bare
    # name of the Python mapping.
    name = "env" + "iron"
    return ["os." + name, "os." + "get" + "env", name + "[", name + ".get",
            "get" + "env" + "(", "import " + name, "process." + "env"]


def test_no_env_reads_in_any_repo_file():
    # The same scanner reads a file that reads the installer's process variables and
    # also spells a remote URL host (this file has the SVG namespace URL) as handing
    # all of them to that host, and holds the plugin for review. Nothing outside
    # .github/workflows reads them: private words come only from the .private-words
    # file, and a subprocess inherits them without naming them.
    needles = _env_reads()
    offenders = []
    for path, text in _iter_repo_text_files():
        for number, line in enumerate(text.splitlines(), 1):
            if any(needle in line for needle in needles):
                offenders.append(f"{path.relative_to(REPO_ROOT)}:{number}: {line.strip()}")
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
