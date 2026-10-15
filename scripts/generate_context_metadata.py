#!/usr/bin/env python3
"""
generate_context_metadata.py

Generates `.github/instructions/.context_metadata.json` with:
  - generation timestamp (ISO 8601 UTC)
  - git commit hash (if available)
  - SHA-256 checksums of each context file
  - comparison against previous checksums (warns on manual edits)

Run after modifying any context file:
    python scripts/generate_context_metadata.py

This script will NOT silently overwrite manual changes without warning.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INSTRUCTIONS_DIR = REPO_ROOT / ".github" / "instructions"
METADATA_FILE = INSTRUCTIONS_DIR / ".context_metadata.json"

CONTEXT_FILES = [
    "architecture.instructions.md",
    "context.instructions.md",
    "instruction.instructions.md",
    "ontology.instructions.md",
    "policies.instructions.md",
    "README.instructions.md",
    "rules.instructions.md",
    "standards.instructions.md",
]


def sha256(path: Path) -> str | None:
    """Compute SHA-256 of a file, or None if it doesn't exist."""
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def get_git_commit() -> str | None:
    """Return the current HEAD commit hash, or None."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except FileNotFoundError:
        pass
    return None


def main() -> None:
    print(f"📁 Instructions directory: {INSTRUCTIONS_DIR}")
    print(f"📄 Metadata file: {METADATA_FILE}")
    print()

    # --- Load previous metadata if it exists ---
    previous_checksums: dict[str, str | None] = {}
    if METADATA_FILE.exists():
        try:
            prev_meta = json.loads(METADATA_FILE.read_text(encoding="utf-8"))
            previous_checksums = prev_meta.get("file_checksums", {})
            print(f"📋 Found previous metadata (generated at: {prev_meta.get('generated_at', '?')})")
        except (json.JSONDecodeError, KeyError):
            print("⚠️  Previous metadata file exists but is invalid; regenerating.")

    # --- Compute current checksums ---
    current_checksums: dict[str, str | None] = {}
    missing_files: list[str] = []
    changed_files: list[str] = []

    for filename in CONTEXT_FILES:
        path = INSTRUCTIONS_DIR / filename
        checksum = sha256(path)
        current_checksums[filename] = checksum

        if checksum is None:
            missing_files.append(filename)
            print(f"  ❌ MISSING: {filename}")
        else:
            prev = previous_checksums.get(filename)
            if prev and prev != checksum:
                changed_files.append(filename)
                print(f"  🔄 CHANGED: {filename}")
            else:
                print(f"  ✅ OK:      {filename}")

    print()

    # --- Warn about changes ---
    if changed_files:
        print("⚠️  The following files have changed since the last metadata generation:")
        for f in changed_files:
            print(f"     - {f}")
        print("   This is expected if you edited them intentionally.")
        print()

    if missing_files:
        print("❌ The following files are MISSING:")
        for f in missing_files:
            print(f"     - {f}")
        print()

    # --- Build metadata ---
    metadata = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator": "scripts/generate_context_metadata.py",
        "git_commit": get_git_commit(),
        "context_format_version": "1.0.0-poc",
        "poc_notice": (
            "This metadata is part of the mock-lumen-mcp-poc project. "
            "It is NOT an official Lumen artifact."
        ),
        "file_checksums": current_checksums,
        "total_files_expected": len(CONTEXT_FILES),
        "total_files_found": len(CONTEXT_FILES) - len(missing_files),
        "missing_files": missing_files,
    }

    # --- Write ---
    METADATA_FILE.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(f"✅ Metadata written to: {METADATA_FILE}")
    print(f"   Timestamp: {metadata['generated_at']}")
    print(f"   Git commit: {metadata['git_commit'] or '(not available)'}")
    print(f"   Files found: {metadata['total_files_found']}/{metadata['total_files_expected']}")

    if missing_files:
        sys.exit(1)


if __name__ == "__main__":
    main()
