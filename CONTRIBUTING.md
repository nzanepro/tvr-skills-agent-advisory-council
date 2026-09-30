# Contributing to tvr-skills-agent-advisory-council

Thanks for looking at this. The project is one Agent Skill, `advisory-council`, plus its
standard-library helper script (`advisory-council/scripts/council.py`), its references and
templates, and the Claude Code plugin files that ship it. Most contributions fall into one of:
a bug fix in `council.py`, a better seat menu or persona rule, a fix to a process rule the
skill protects (independent Round 1, corrections only in addenda, dissent kept), or a report
that the skill did not trigger when it should have (or triggered when it should not).

## Before you start

- Open an issue first for anything beyond a small fix, so the approach can be agreed before
  you write it.
- One change per pull request. Keep unrelated formatting out of a functional change.

## Running the tests

```bash
python -m pip install pytest pyyaml
python -m pytest tests -q
```

The tests exercise `council.py` directly on a small fictional roster and check the packaging:
the `SKILL.md` frontmatter (parsed strictly, and with PyYAML when it is installed), the plugin
and marketplace manifests, and the repository's hygiene rules. CI runs the same suite on
Windows, macOS and Linux with Python 3.9, 3.10 and 3.13; keep new tests OS-independent (no
hardcoded path separators, no assumption about which drive or home folder exists).

## Running the trigger evals

[`evals/trigger-queries.json`](evals/trigger-queries.json) holds prompts that should and should
not load the skill, in the [skill-creator trigger-eval format](https://github.com/anthropics/skills),
with a focus on near misses (one quick opinion, summarising real interviews, meeting minutes,
role-playing a named person). If you change the `description` in the `SKILL.md` frontmatter,
add or update entries so the change is checked, not just asserted in the pull request text.

## Validating the plugin

Before opening a pull request that touches `.claude-plugin/`, a `SKILL.md` or anything the
skill loads, run:

```bash
claude plugin validate . --strict
```

The plugin's manifest is `.claude-plugin/plugin.json`; `.claude-plugin/marketplace.json` only
lists it. Declare components (such as `skills`) in `plugin.json`, not in the marketplace entry.
Keep the plugin name `council`: users install `council@tvr-skills-agent-advisory-council` and
run `/council:advisory-council`, so a rename breaks every existing install.

`claude plugin validate` accepts some frontmatter that stricter YAML parsers reject, such as an
unquoted `description` containing `": "`. Quote a frontmatter value that contains a colon; the
tests catch the rest.

## Privacy rules for anything you contribute

This is a public repository. Please keep contributions free of:

- Personal file paths (home directories, usernames, machine names, drive letters that are not
  purely illustrative).
- Real email addresses, account names, or API keys and tokens, including in code comments,
  test fixtures and commit messages.
- Real named people as council members, in examples, evals or tests. The skill seats roles and
  organisation types, never a named individual; keep examples to that rule.
- Real companies' confidential or internal material, and real decisions you are not free to
  share. Use obviously fictional examples (the bakery roster in `tests/conftest.py` and the
  leak-sensor company in `advisory-council/references/example/` are good models).

The hygiene test flags common personal paths. To also check for private words (your own name,
a private project), list them one per line in a git-ignored `.private-words` file at the repo
root. Never commit that file.

If you are not sure whether something counts as personal or confidential, ask in the pull
request rather than posting it.

## Changing the council process

The references under `advisory-council/references/` explain why each rule exists (see
`facilitation.md`, `rounds.md` and `verification.md`). A good change:

- Says which failure it prevents (groupthink, a wrong shared fact, a lost dissent, a vote in an
  addendum) and shows it on a fictional example.
- Keeps `council.py check` in step: if a rule changes, the check and its tests change with it.
- Updates the worked example in `advisory-council/references/example/` when the file format
  changes, so `council.py check --final` still passes on it.

## Code style

- `SKILL.md` stays under 500 lines; put anything longer in `references/` and link to it.
- `council.py` and the tests run on Python 3.9 or later. Put `from __future__ import
  annotations` at the top of a file that uses `X | Y` or `list[str]` in annotations, and avoid
  newer runtime features such as `match`, `zip(strict=)` and `Path.write_text(newline=)`;
  `tests/test_skill_hygiene.py` flags the common ones, and CI runs the suite on 3.9.
- `council.py` uses only the Python standard library. Do not add a third-party dependency; the
  script has to run wherever the skill is installed.
- Every subcommand keeps `--json` output and meaningful exit codes (0 ok, 1 usage error, 3
  problems found). Follow that pattern for anything new.

## Versions and releases

A change users will notice bumps the version in four places that the tests keep in step:
`metadata.version` in `advisory-council/SKILL.md`, `version` in `.claude-plugin/plugin.json`,
`version` in `.claude-plugin/marketplace.json`, and a new section at the top of
[CHANGELOG.md](CHANGELOG.md). Plugin users only receive an update when the `plugin.json`
version changes. The maintainer tags releases; pushing a `vX.Y.Z` tag builds the skill zip and
the GitHub Release from the matching changelog section.

## Reporting a skill that did not trigger

"Did not trigger" reports are some of the most useful ones, because they usually mean the
`description` in `SKILL.md` needs a phrase. Please include:

- The exact prompt you typed.
- Which client (Claude Code, claude.ai, another Agent Skills client) and how the skill was
  installed (plugin marketplace, personal skill, project skill, uploaded zip).
- Whether another skill triggered instead.
