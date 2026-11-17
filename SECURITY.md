# Security policy

## Reporting a vulnerability

Please **do not** open a public issue for security problems.

Report them privately through GitHub instead:
**[Report a vulnerability](https://github.com/benmazzotta/pdf-porter/security/advisories/new)**
(Security tab → "Report a vulnerability").

Please include the pdf-porter version, how you run it (Claude Desktop, uvx, venv) and the steps to reproduce.
This is a one-person project, so replies may take a few days. There is no bug bounty.

## Supported versions

Only the latest release on [PyPI](https://pypi.org/project/pdf-porter/) receives fixes.

## Scope

pdf-porter is a local MCP server. It reads PDF files that the MCP client asks it to read and, when asked, writes Markdown files to a chosen directory.
Problems in Docling or the MCP SDK themselves should go to those projects; we will update our pins once they ship a fix.
