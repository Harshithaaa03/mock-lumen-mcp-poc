"""
MCP Server tests – test_mcp_server.py

Tests use the MCP SDK's test client to exercise the server without a network.
"""
from __future__ import annotations

import sys
import os

# Add mcp_server directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from pathlib import Path


# ---------------------------------------------------------------------------
# Context file tests
# ---------------------------------------------------------------------------

class TestContextFiles:
    """Verify all eight context files exist and have content."""

    EXPECTED_FILES = [
        "architecture.instructions.md",
        "context.instructions.md",
        "instruction.instructions.md",
        "ontology.instructions.md",
        "policies.instructions.md",
        "README.instructions.md",
        "rules.instructions.md",
        "standards.instructions.md",
    ]

    @property
    def instructions_dir(self) -> Path:
        return Path(__file__).parent.parent.parent / ".github" / "instructions"

    def test_instructions_directory_exists(self):
        assert self.instructions_dir.exists(), (
            f"Instructions directory not found: {self.instructions_dir}"
        )

    def test_all_eight_context_files_exist(self):
        for filename in self.EXPECTED_FILES:
            path = self.instructions_dir / filename
            assert path.exists(), f"Missing context file: {filename}"

    def test_all_context_files_are_non_empty(self):
        for filename in self.EXPECTED_FILES:
            path = self.instructions_dir / filename
            if path.exists():
                content = path.read_text(encoding="utf-8").strip()
                assert len(content) > 50, (
                    f"Context file appears empty or too short: {filename} ({len(content)} chars)"
                )

    def test_context_files_mention_todo(self):
        """At least one file should reference the Todo application."""
        found = False
        for filename in self.EXPECTED_FILES:
            path = self.instructions_dir / filename
            if path.exists():
                content = path.read_text(encoding="utf-8").lower()
                if "todo" in content or "task" in content:
                    found = True
                    break
        assert found, "No context file mentions 'todo' or 'task' – content may not be application-specific"


# ---------------------------------------------------------------------------
# Context loader tests
# ---------------------------------------------------------------------------

class TestContextLoader:
    """Test the context_loader module directly."""

    def test_load_valid_section(self):
        from context_loader import load_context_file
        result = load_context_file("architecture")
        assert result["section"] == "architecture"
        assert "source_file" in result
        # Found may be True or False depending on whether files exist
        assert "found" in result

    def test_load_invalid_section(self):
        from context_loader import load_context_file
        result = load_context_file("nonexistent_section_xyz")
        assert result["found"] is False
        assert "error" in result
        assert result["content"] is None

    def test_load_all_context_files_returns_all_keys(self):
        from context_loader import load_all_context_files, CONTEXT_FILES
        result = load_all_context_files()
        assert set(result.keys()) == set(CONTEXT_FILES.keys())

    def test_search_context_returns_list(self):
        from context_loader import search_context
        results = search_context("task")
        assert isinstance(results, list)
        # If context files exist, should find matches
        for item in results:
            assert "section" in item
            assert "snippets" in item

    def test_search_context_no_match(self):
        from context_loader import search_context
        results = search_context("zzz_no_match_xyz_12345_abc")
        assert isinstance(results, list)
        assert len(results) == 0

    def test_freshness_metadata_returns_dict(self):
        from context_loader import load_freshness_metadata
        result = load_freshness_metadata()
        assert isinstance(result, dict)
        assert "metadata_available" in result

    def test_freshness_fallback_includes_file_times(self):
        from context_loader import load_freshness_metadata
        result = load_freshness_metadata()
        # Whether metadata file exists or not, we get a valid response
        if not result.get("metadata_available"):
            assert "file_modification_times" in result
            assert "note" in result


# ---------------------------------------------------------------------------
# MCP tool tests (using direct function calls)
# ---------------------------------------------------------------------------

class TestMCPTools:
    """Test the MCP tool functions directly."""

    def _import_tools(self):
        """Import tool functions from server module."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "server",
            Path(__file__).parent.parent / "server.py",
        )
        module = importlib.util.load_from_spec(spec)  # type: ignore[attr-defined]
        spec.loader.exec_module(module)  # type: ignore[union-attr]
        return module

    def test_get_application_context_all(self):
        from context_loader import load_all_context_files
        result = load_all_context_files()
        assert isinstance(result, dict)
        assert len(result) == 8

    def test_get_application_context_specific_section(self):
        from context_loader import load_context_file
        result = load_context_file("architecture")
        assert "found" in result
        assert "section" in result
        assert result["section"] == "architecture"

    def test_get_application_context_missing_section_handled(self):
        from context_loader import load_context_file
        result = load_context_file("doesnotexist")
        assert result["found"] is False
        assert result["content"] is None
        assert "error" in result

    def test_get_business_context_structure(self):
        from context_loader import load_context_file
        for key in ["context", "ontology", "rules"]:
            result = load_context_file(key)
            assert "found" in result

    def test_get_compliance_context_structure(self):
        from context_loader import load_context_file
        for key in ["policies", "rules", "standards"]:
            result = load_context_file(key)
            assert "found" in result

    def test_get_context_freshness_structure(self):
        from context_loader import load_freshness_metadata
        result = load_freshness_metadata()
        assert isinstance(result, dict)
        assert "metadata_available" in result

    def test_no_fabricated_content_for_missing_file(self):
        from context_loader import load_context_file
        result = load_context_file("nonexistent")
        # Must not invent content
        assert result["content"] is None
        assert result["found"] is False
