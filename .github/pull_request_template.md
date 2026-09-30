<!--
Thanks for the pull request. Please fill in every section below and delete this comment.
See CONTRIBUTING.md for the test and eval commands and the privacy rules for anything you add
(no personal paths, no real named people, fictional examples only).
-->

## What this changes and why

<!-- One or two sentences. Link the issue this addresses, if there is one. -->

## What it touches

- [ ] The skill (`advisory-council/SKILL.md`, references or templates)
- [ ] `council.py`
- [ ] Plugin files (`.claude-plugin/`)
- [ ] Repository-wide (docs, CI, templates, etc.)

## Testing

- [ ] `python -m pytest tests -q` passes locally
- [ ] `claude plugin validate . --strict` passes (only needed if you touched `.claude-plugin/` or `SKILL.md`)
- [ ] Ran a council with the change: <!-- client, mode (parallel or single-agent), or "not applicable" -->
- [ ] Added or updated tests for the behavior this changes
- [ ] Added or updated trigger-eval entries in `evals/` (only needed if the `SKILL.md` `description` changed)

## Version bump

- [ ] `metadata.version` in `advisory-council/SKILL.md`, `version` in `.claude-plugin/plugin.json` and `version` in `.claude-plugin/marketplace.json` were bumped together
- [ ] `CHANGELOG.md` has an entry (or the maintainer will add one)
- [ ] Not applicable (docs-only / internal change with no user-facing effect)

## Checklist

- [ ] No personal file paths, usernames, machine names, emails, or tokens in code, tests, or commit messages
- [ ] No real named people as council members or in examples; decisions and companies are fictional
- [ ] `SKILL.md` stays under 500 lines, with longer material in `references/`
