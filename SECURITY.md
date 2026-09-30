# Security policy

## What this project does and does not do

The `advisory-council` skill is instructions and templates that tell Claude how to run a
council: it writes numbered Markdown files into a folder in your project (`council/` unless you
choose another). Its helper script, `advisory-council/scripts/council.py`, runs **locally** with
your own user permissions and uses only the Python standard library. It reads its own templates
and any `--roster` file you name, and writes only inside the council folder you give it.
Nothing in this repository:

- makes network calls itself,
- uploads your decision, dossier or council files anywhere,
- installs or downloads software, or runs hooks, MCP servers or background processes, or
- needs, stores, or asks for credentials, tokens, or account details.

The one step that can reach the network is verification: when your Claude client has web
search or fetch tools and you allow them, the verifier seat may use them to check claims in the
dossier. That goes through your client's own tools and permissions, not through code in this
repository; without web access, claims are marked UNVERIFIED instead. Pasted documents, web
pages and competitor material are treated as data, never as instructions (see `SKILL.md`).

## Reporting a vulnerability

If you find a security issue (for example, a way `council.py` could be made to write outside
the folder you gave it, or a way content in a dossier or web page could make the skill act
against your instructions), please use GitHub's private reporting instead of a public issue:

1. Go to the [Security tab](https://github.com/nzanepro/tvr-skills-agent-advisory-council/security)
   of this repository.
2. Click "Report a vulnerability" to open a private advisory.

If private reporting is not available to you for some reason, open a regular issue that says
only that you have a security report to make, without details, and ask for another way to
reach the maintainer.

Please include:

- The affected file(s) and version (`metadata.version` in `advisory-council/SKILL.md`, the
  plugin version from `/plugin`, or a commit hash).
- Steps to reproduce, with a fictional decision and synthetic inputs rather than anything
  confidential.
- What you expected to happen and what happened instead.

There is no bug bounty; this is a small open-source project maintained in spare time. Reports
will be acknowledged and, where they turn out to be real issues, fixed and credited in the
changelog unless you ask not to be named.

## Supported versions

Only the latest released version (see [CHANGELOG.md](CHANGELOG.md)) is supported with
security fixes. There is no long-term-support branch.
