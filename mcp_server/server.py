"""
Mock Lumen MCP Server – server.py

⚠️  POC NOTICE:
    This server is a proof-of-concept demonstration.
    It is NOT the official Lumen MCP service.
    The context format used here is a proposed POC schema, not a verified Lumen schema.

MCP SDK version: 2.x (MCPServer, renamed from FastMCP)
Transport: Streamable HTTP (POST /mcp)
Health endpoint: GET /health
"""
from __future__ import annotations

import asyncio
import logging
import sys
from typing import Any, Optional

# MCP 2.x SDK
from mcp.server.mcpserver import MCPServer

# Starlette for health endpoint + routing
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route

from context_loader import (
    load_all_context_files,
    load_context_file,
    load_freshness_metadata,
    search_context,
    CONTEXT_FILES,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("mock_lumen_mcp")

# ---------------------------------------------------------------------------
# Initialise the MCPServer
# ---------------------------------------------------------------------------

mcp = MCPServer(
    name="mock-lumen-mcp-poc",
    description=(
        "POC NOTICE: This is a demonstration MCP server for the mock-lumen-mcp-poc project. "
        "It is NOT the official Lumen service. "
        "The context files describe a Todo List web application built as a proof of concept."
    ),
    instructions=(
        "Use these tools to retrieve architectural, business, compliance, and freshness context "
        "about the Todo List POC application. All content is documentation-only; "
        "no live application data is returned."
    ),
)

logger.info("Mock Lumen MCP server initialized (POC, MCP 2.x)")


# ---------------------------------------------------------------------------
# Tool 1: get_application_context
# ---------------------------------------------------------------------------

@mcp.tool(
    description=(
        "Retrieve application context from the repository's .github/instructions files. "
        "Covers architecture, repository structure, implementation details, and API design. "
        "POC: This is a mock Lumen server, not the official Lumen service."
    )
)
def get_application_context(
    section: Optional[str] = None,
    query: Optional[str] = None,
) -> dict[str, Any]:
    """
    Retrieve architecture, repository, and implementation context.

    Args:
        section: Optional section key. Valid values: architecture, context, instruction,
                 ontology, policies, readme, rules, standards, or 'all'.
        query:   Optional search phrase. Searches across all context files.
    """
    logger.info("get_application_context called: section=%r, query=%r", section, query)

    response: dict[str, Any] = {
        "tool": "get_application_context",
        "poc_notice": (
            "This is a mock Lumen MCP server (POC). "
            "Context represents the Todo List demonstration application."
        ),
        "available_sections": list(CONTEXT_FILES.keys()),
    }

    if query:
        results = search_context(query)
        response["query"] = query
        response["search_results"] = results
        response["result_count"] = len(results)
        if not results:
            response["message"] = f"No context found matching query: {query!r}"
        return response

    if section and section.lower() != "all":
        ctx = load_context_file(section)
        response["section"] = ctx.get("section", section)
        response["source_file"] = ctx.get("source_file")
        response["found"] = ctx.get("found", False)
        if ctx.get("found"):
            response["content"] = ctx["content"]
        else:
            response["not_found"] = ctx.get("error")
            response["message"] = "Section not found. Check 'available_sections' for valid keys."
        return response

    all_ctx = load_all_context_files()
    found_sections = {k: v for k, v in all_ctx.items() if v.get("found")}
    missing_sections = [k for k, v in all_ctx.items() if not v.get("found")]

    response["sections"] = {
        k: {
            "source_file": v["source_file"],
            "content": v["content"],
            "found": v["found"],
        }
        for k, v in all_ctx.items()
    }
    response["found_count"] = len(found_sections)
    response["missing_sections"] = missing_sections
    return response


# ---------------------------------------------------------------------------
# Tool 2: get_business_context
# ---------------------------------------------------------------------------

@mcp.tool(
    description=(
        "Retrieve business domain information for the Todo List application: "
        "entities, workflows, capabilities, and business rules. "
        "POC: This is a mock Lumen server, not the official Lumen service."
    )
)
def get_business_context() -> dict[str, Any]:
    """
    Retrieve business domain context (ontology, rules, context sections).
    Distinguishes implemented features from planned features.
    """
    logger.info("get_business_context called")

    context_sections = ["context", "ontology", "rules"]
    sections_data: dict[str, Any] = {}
    missing: list[str] = []

    for key in context_sections:
        ctx = load_context_file(key)
        if ctx.get("found"):
            sections_data[key] = {
                "source_file": ctx["source_file"],
                "content": ctx["content"],
            }
        else:
            missing.append(key)

    return {
        "tool": "get_business_context",
        "poc_notice": (
            "This is a mock Lumen MCP server (POC). "
            "Business context describes the Todo List demonstration application only. "
            "This is NOT approved corporate business documentation."
        ),
        "application_name": "Todo List POC",
        "domain": "Task management",
        "sections_read": context_sections,
        "sections_found": list(sections_data.keys()),
        "missing_sections": missing,
        "content": sections_data,
    }


# ---------------------------------------------------------------------------
# Tool 3: get_compliance_context
# ---------------------------------------------------------------------------

@mcp.tool(
    description=(
        "Retrieve documented policies, constraints, and standards for the Todo List POC. "
        "POC ONLY: This is mock documentation - NOT approved corporate compliance guidance or legal advice."
    )
)
def get_compliance_context() -> dict[str, Any]:
    """
    Retrieve policies, rules, and coding standards context.
    All content is clearly identified as POC documentation.
    """
    logger.info("get_compliance_context called")

    compliance_sections = ["policies", "rules", "standards"]
    sections_data: dict[str, Any] = {}
    missing: list[str] = []

    for key in compliance_sections:
        ctx = load_context_file(key)
        if ctx.get("found"):
            sections_data[key] = {
                "source_file": ctx["source_file"],
                "content": ctx["content"],
            }
        else:
            missing.append(key)

    return {
        "tool": "get_compliance_context",
        "compliance_disclaimer": (
            "IMPORTANT: This is mock POC documentation for a demonstration application. "
            "It is NOT approved corporate compliance guidance, legal advice, or official "
            "security policy. Do not use this as a basis for production compliance decisions."
        ),
        "sections_read": compliance_sections,
        "sections_found": list(sections_data.keys()),
        "missing_sections": missing,
        "content": sections_data,
    }


# ---------------------------------------------------------------------------
# Tool 4: get_context_freshness
# ---------------------------------------------------------------------------

@mcp.tool(
    description=(
        "Report when the context files were last generated or updated. "
        "Returns ISO 8601 timestamps and version/commit information if available. "
        "Note: server startup time is not the same as context generation time."
    )
)
def get_context_freshness() -> dict[str, Any]:
    """
    Report context freshness metadata.
    Never claims context is fresh simply because the server is running.
    """
    logger.info("get_context_freshness called")

    freshness = load_freshness_metadata()

    return {
        "tool": "get_context_freshness",
        "poc_notice": (
            "This is a mock Lumen MCP server (POC). "
            "Freshness data reflects context file modification times, not production data pipelines."
        ),
        **freshness,
    }


# ---------------------------------------------------------------------------
# Health endpoint (Starlette)
# ---------------------------------------------------------------------------

async def health(request: Request) -> JSONResponse:
    """Simple health check endpoint required by Render.com and Copilot Studio."""
    return JSONResponse({
        "status": "ok",
        "service": "mock-lumen-mcp-poc",
        "transport": "streamable-http",
        "mcp_endpoint": "/mcp",
        "poc_notice": "This is a demonstration MCP server (POC), not the official Lumen service.",
    })


def build_app():
    """Build the combined Starlette application with health + MCP routes."""
    mcp_app = mcp.streamable_http_app()

    return Starlette(
        routes=[
            Route("/health", endpoint=health, methods=["GET"]),
            Mount("/", app=mcp_app),
        ]
    )


# ---------------------------------------------------------------------------
# Run the server
# ---------------------------------------------------------------------------

def main():
    import argparse
    import uvicorn

    parser = argparse.ArgumentParser(description="Mock Lumen MCP Server (POC)")
    parser.add_argument(
        "--transport",
        choices=["stdio", "streamable-http"],
        default="streamable-http",
        help="Transport mode",
    )
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8001)
    args = parser.parse_args()

    logger.info(
        "Starting Mock Lumen MCP Server (POC) | transport=%s | host=%s | port=%s",
        args.transport, args.host, args.port,
    )

    if args.transport == "stdio":
        asyncio.run(mcp.run_stdio_async())
    else:
        app = build_app()
        uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
