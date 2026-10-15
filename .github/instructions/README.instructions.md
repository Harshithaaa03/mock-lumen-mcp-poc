# README – Context Package

> **POC NOTICE:** This context package is part of the `mock-lumen-mcp-poc` project.
> It uses a **proposed context format** and is NOT an official Lumen schema or service.
> The Lumen team has not reviewed or approved this format.

## Purpose

The `.github/instructions/` directory contains **eight structured Markdown context files**
that describe the `mock-lumen-mcp-poc` Todo List application. These files are consumed by
the **Mock Lumen MCP Server** (`mcp_server/server.py`) to provide contextual responses
to AI agent queries via the Model Context Protocol (MCP).

## File Descriptions

| File | Purpose |
|------|---------|
| `architecture.instructions.md` | System architecture, components, APIs, and module dependencies |
| `context.instructions.md` | Application purpose, repository structure, domain, and feature inventory |
| `instruction.instructions.md` | Operating guidance for AI agents consuming this context package |
| `ontology.instructions.md` | Domain entity definitions, field specifications, and relationships |
| `policies.instructions.md` | Access control, data handling, MCP security, and sample recommendations |
| `README.instructions.md` | This file — describes the context package and its consumers |
| `rules.instructions.md` | Business logic, validation rules, status transitions, and invariants |
| `standards.instructions.md` | Coding conventions, API design, testing, and documentation standards |

## Intended Consumers

1. **Mock Lumen MCP Server** (`mcp_server/server.py`) – reads files at runtime via
   `mcp_server/context_loader.py` and serves them through 4 MCP tools.
2. **Microsoft Copilot Studio Agent** – sends MCP tool calls to the server and uses the
   returned context to answer business stakeholder questions about the application.
3. **Human developers** – these files serve as onboarding documentation.

## How Context Is Generated

Context files are hand-authored based on the actual source code of the application.
A generation timestamp is written by:

```bash
python scripts/generate_context_metadata.py
```

This script writes `.github/instructions/.context_metadata.json` with:
- `generated_at` (ISO 8601 UTC)
- `git_commit` (current HEAD commit hash, if available)
- `files_checksummed` (SHA-256 of each context file)

## How Context Is Maintained

- Re-run `generate_context_metadata.py` after modifying any context file.
- The script will warn if checksums differ from previous run (indicating manual changes).
- Context files should be updated whenever the application's source code changes materially.

## How Context Is Consumed

The `get_context_freshness` MCP tool reads `.context_metadata.json` to report when
context was last generated. If no metadata file exists, it falls back to file modification
timestamps.

```
MCP Client (Copilot Studio)
  → POST /mcp
  → MCPServer.get_application_context(section="architecture")
  → context_loader.load_context_file("architecture")
  → reads .github/instructions/architecture.instructions.md
  → returns content to MCP client
```

## Version History

| Version | Notes |
|---------|-------|
| 1.0.0 | Initial POC context package. Hand-authored from source code inspection. |
