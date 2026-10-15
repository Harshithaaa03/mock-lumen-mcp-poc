"""
context_loader.py – Reads the .github/instructions context files.

⚠️  POC NOTICE: This is a mock Lumen MCP server for demonstration purposes.
    It is NOT the official Lumen service or schema.
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Discover repo root relative to this file's location (mcp_server/../)
_THIS_DIR = Path(__file__).parent
REPO_ROOT = _THIS_DIR.parent

INSTRUCTIONS_DIR = REPO_ROOT / ".github" / "instructions"
METADATA_FILE = REPO_ROOT / ".github" / "instructions" / ".context_metadata.json"

CONTEXT_FILES: dict[str, str] = {
    "architecture": "architecture.instructions.md",
    "context": "context.instructions.md",
    "instruction": "instruction.instructions.md",
    "ontology": "ontology.instructions.md",
    "policies": "policies.instructions.md",
    "readme": "README.instructions.md",
    "rules": "rules.instructions.md",
    "standards": "standards.instructions.md",
}


def _read_file(path: Path) -> Optional[str]:
    """Read a file and return its content, or None if not readable."""
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.warning("Context file not found: %s", path)
        return None
    except OSError as exc:
        logger.error("Error reading %s: %s", path, exc)
        return None


def load_context_file(section: str) -> dict:
    """Load a single context file by section key or filename."""
    # Allow lookup by key or by filename stem
    key = section.lower().replace(".instructions.md", "").replace(".md", "")
    filename = CONTEXT_FILES.get(key)

    if filename is None:
        # Try matching by filename prefix
        for k, v in CONTEXT_FILES.items():
            if v.startswith(key) or k.startswith(key):
                filename = v
                key = k
                break

    if filename is None:
        available = list(CONTEXT_FILES.keys())
        return {
            "found": False,
            "section": section,
            "error": f"Unknown section {section!r}. Available sections: {available}",
            "content": None,
            "source_file": None,
        }

    path = INSTRUCTIONS_DIR / filename
    content = _read_file(path)

    return {
        "found": content is not None,
        "section": key,
        "source_file": str(path.relative_to(REPO_ROOT)).replace("\\", "/"),
        "content": content,
        "error": None if content is not None else f"File not found: {filename}",
    }


def load_all_context_files() -> dict:
    """Load all context files and return a combined dict."""
    results: dict[str, dict] = {}
    for key, filename in CONTEXT_FILES.items():
        path = INSTRUCTIONS_DIR / filename
        content = _read_file(path)
        results[key] = {
            "found": content is not None,
            "filename": filename,
            "source_file": f".github/instructions/{filename}",
            "content": content,
        }
    return results


def search_context(query: str) -> list[dict]:
    """Full-text search across all context files."""
    query_lower = query.lower()
    matches: list[dict] = []
    for key, filename in CONTEXT_FILES.items():
        path = INSTRUCTIONS_DIR / filename
        content = _read_file(path)
        if content is None:
            continue
        if query_lower in content.lower():
            # Collect matching snippets (up to 3 lines around each match)
            lines = content.splitlines()
            snippets: list[str] = []
            for i, line in enumerate(lines):
                if query_lower in line.lower():
                    start = max(0, i - 1)
                    end = min(len(lines), i + 2)
                    snippet = "\n".join(lines[start:end])
                    snippets.append(snippet)
                    if len(snippets) >= 5:
                        break
            matches.append({
                "section": key,
                "source_file": f".github/instructions/{filename}",
                "match_count": len(snippets),
                "snippets": snippets,
            })
    return matches


def load_freshness_metadata() -> dict:
    """
    Return context-generation metadata.

    Reads from .context_metadata.json if it exists.
    Does NOT claim freshness from server startup time alone.
    """
    meta = _read_file(METADATA_FILE)
    if meta:
        try:
            data = json.loads(meta)
            return {
                "metadata_available": True,
                "source": str(METADATA_FILE.relative_to(REPO_ROOT)).replace("\\", "/"),
                **data,
            }
        except json.JSONDecodeError as exc:
            return {
                "metadata_available": False,
                "error": f"Invalid JSON in metadata file: {exc}",
            }

    # Fallback: report file modification times
    file_times: dict[str, Optional[str]] = {}
    for key, filename in CONTEXT_FILES.items():
        path = INSTRUCTIONS_DIR / filename
        if path.exists():
            mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
            file_times[key] = mtime.isoformat()
        else:
            file_times[key] = None

    existing_times = [t for t in file_times.values() if t]
    oldest = min(existing_times) if existing_times else None
    newest = max(existing_times) if existing_times else None

    return {
        "metadata_available": False,
        "warning": (
            "No .context_metadata.json found. Reporting file modification times instead. "
            "Run scripts/generate_context_metadata.py to generate accurate metadata."
        ),
        "file_modification_times": file_times,
        "oldest_file_modified": oldest,
        "newest_file_modified": newest,
        "server_startup_time": datetime.now(timezone.utc).isoformat(),
        "note": "Server startup time is NOT the same as context generation time.",
    }
