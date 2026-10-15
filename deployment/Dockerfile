FROM python:3.12-slim

WORKDIR /app

# Copy context files first (these change less often)
COPY .github/instructions/ /app/.github/instructions/

# Copy MCP server code
COPY mcp_server/ /app/mcp_server/

# Copy scripts (for metadata generation)
COPY scripts/ /app/scripts/

# Install MCP server dependencies
RUN pip install --no-cache-dir -r /app/mcp_server/requirements.txt

# Set the working directory to the mcp_server folder for context_loader paths
WORKDIR /app/mcp_server

# Expose the default MCP port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8001/health')" || exit 1

# Run the MCP server with streamable-http transport
CMD ["python", "server.py", "--transport", "streamable-http", "--host", "0.0.0.0", "--port", "8001"]
