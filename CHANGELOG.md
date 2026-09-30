# Changelog

All notable changes to this project are listed here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and versions follow
[Semantic Versioning](https://semver.org/). The version matches `metadata.version` in
`advisory-council/SKILL.md`, `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`.

## [0.2.1] - 2026-09-29

### Added

- A plugin icon for the Claude plugin directory listing: a council of seats around a table
  with the shared dossier, in the colours of the README diagram. It is a square SVG in
  .claude-plugin/, and `icon` in `plugin.json` points to it. A test checks that it is
  well-formed, square and self-contained (no script, links or embedded images).

### Fixed

- README: the manual install commands for a linked copy used shell variables (the current
  folder and, in PowerShell, the user profile folder). The plugin directory's scan reads a
  variable beside the `git clone` URL as a credential from the installer's machine and held the
  plugin for review. The personal and linked copies now clone into your home folder and use
  literal paths, and create `~/.claude/skills` if it is missing. A test keeps shell variables
  and command substitution out of the shipped docs.

## [0.2.0] - 2026-09-29

### Added

- `.claude-plugin/plugin.json`, the plugin's own manifest: name `council`, version,
  description, author, license, links, keywords and the `advisory-council` skill, as the Claude
  plugin directory expects. The install commands and `/council:advisory-council` are unchanged.
- README: how to update the plugin (**Update now** in `/plugin`, or `claude plugin update`),
  install commands for the shell, what the plugin writes, runs and sends, and a Support section;
  the plugin description links to it too. GitHub Sponsor button.
- `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md` (private reports through GitHub's
  "Report a vulnerability"), issue forms and a pull request template.
- Release workflow: pushing a `vX.Y.Z` tag builds `advisory-council-X.Y.Z.zip` from
  `advisory-council/` and publishes the GitHub Release with this file's matching section.
- CI job that runs `claude plugin validate --strict` on the marketplace and plugin manifests.

### Changed

- `council.py` supports Python 3.9 (was 3.10 or later); CI runs the tests on 3.9, 3.10 and
  3.13.
- The marketplace entry no longer sets `"strict": false` or lists the skill; `plugin.json`
  declares it. The entry keeps the catalog fields (source, description, category, tags).
- Tests parse the `SKILL.md` frontmatter with a strict parser, and with PyYAML when it is
  installed (CI installs it), instead of splitting lines on the first colon.

### Fixed

- `council.py init` and `council.py addendum` failed on Python 3.9, where `Path.write_text()`
  has no `newline=` argument. They now write LF files on every supported version.
- The `SKILL.md` frontmatter was not valid YAML: the unquoted `description` contained `": "`,
  which strict parsers such as PyYAML reject. The description is now quoted; its text is
  unchanged.

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

[0.2.1]: https://github.com/nzanepro/tvr-skills-agent-advisory-council/releases/tag/v0.2.1
[0.2.0]: https://github.com/nzanepro/tvr-skills-agent-advisory-council/releases/tag/v0.2.0
[0.1.0]: https://github.com/nzanepro/tvr-skills-agent-advisory-council/releases/tag/v0.1.0
