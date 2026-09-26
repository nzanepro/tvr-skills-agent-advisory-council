# Changelog

All notable changes to this project are listed here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and versions follow
[Semantic Versioning](https://semver.org/). The version matches `metadata.version` in
`advisory-council/SKILL.md` and the marketplace entry.

## [0.1.0] - 2026-09-26

### Added

- `advisory-council` skill: frames a decision, proposes and confirms a council of stakeholder
  personas, writes a shared dossier, runs an independent Round 1, a persona-free verification
  with correction addenda, a tally with lettered options, a Round 2 vote, and a recommendation
  with dissent, risks, open questions and next steps. Parallel mode (one subagent per member)
  and a single-agent protocol.
- `advisory-council/scripts/council.py` (standard library only, Windows, macOS and Linux):
  `init` scaffolds the numbered file set, `status` shows the next step, `addendum` numbers
  corrections, `tally` counts positions and weighted votes and refuses a partial count, `check`
  enforces the process rules.
- References: council design and seat menus by domain (business and product, engineering,
  public policy, research), persona guide with ethics rules, dossier guide, round and tally
  procedure with member briefs, verification and addenda, facilitation rules against groupthink
  and sycophancy, file templates, and a complete worked example on a fictional product.
- Claude Code plugin marketplace (`.claude-plugin/marketplace.json`), trigger evals, tests and
  CI on Windows, macOS and Linux.

[0.1.0]: https://github.com/nzanepro/tvr-skills-agent-advisory-council/releases/tag/v0.1.0
