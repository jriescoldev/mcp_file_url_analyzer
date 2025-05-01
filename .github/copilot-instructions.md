<!--
INSTRUCTIONS FOR GITHUB COPILOT (project: mcp-file-url-analyzer)

**General Principles:**
- All code, comments, documentation, and commit messages must be in clear English.
- Code must strictly follow Pylint standards (using `.pylintrc` if present) and modern Python best practices (type hints, async/await, f-strings for formatting except in logging).
- Aim for a Pylint score >9.5/10. Address all errors (E) and critical warnings (W). Strive to fix convention (C) and refactor (R) suggestions.

**Project Scope:**
- This is a Python MCP server to analyze local files/directories and URLs (text and binary).
- Use only the official MCP Python SDK: https://github.com/modelcontextprotocol/python-sdk
- Implement exactly two tools: `analyze-path` (local files/dirs) and `analyze-url` (download/analyze URLs).
- Do NOT implement or reference any note-related tools/resources (e.g., `add-note`, `note://`, etc.).

**Best Practices:**
- Use `FastMCP` for the server, Pydantic models for all tool input/output, and modular code structure.
- Centralize configuration (Pydantic Settings, `.env`). Never commit secrets; `.env` must be in `.gitignore`.
- Enforce SSRF protection for URLs and reasonable size limits for files/URLs.
- Use secure, structured logging (`logger.info(\"msg %%s\", var)`, never f-strings in logger calls).
- Handle errors robustly and return clear MCP error responses.
- Prefer composition over inheritance. Avoid global state. Keep functions small and focused.

**Testing & Quality:**
- Write comprehensive async tests with `pytest` and `pytest-asyncio`. Mock all external dependencies.
- Aim for high test coverage, especially for edge cases and error handling.
- Keep dependencies up-to-date and pinned (`requirements.txt` or `pyproject.toml`).
- Use `with` statements for all resource management (files, network, subprocesses).

**Code Style:**
- Imports: 1. Standard library, 2. Third-party, 3. Local. No wildcards.
- Naming: `snake_case` for variables/functions, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants.
- Use PEP 484 type hints everywhere. Use Pydantic models for all data structures.

**Documentation & Version Control:**
- Keep `README.md` up to date (setup, usage, config, security, deployment).
- All public modules, classes, and functions must have clear English docstrings.
- Commit messages must be clear and descriptive (Conventional Commits recommended).

**Docker:**
- The `Dockerfile` must build a secure, efficient, reproducible image. Run as non-root. All config via env vars.

**What NOT to do:**
- Do NOT add any note-related tools/resources.
- Do NOT commit `.env` or secrets.
- Do NOT use wildcards in imports.
- Do NOT use f-strings in logger calls.

**If in doubt:**
- Consult the official MCP Python SDK documentation.
- Prefer explicit, readable, maintainable, and secure code over clever or complex solutions.
- Ask for clarification if requirements are ambiguous.
-->
