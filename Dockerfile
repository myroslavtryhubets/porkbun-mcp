FROM python:3.12-slim

WORKDIR /usr/src/app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && \
    rm -f requirements.txt

# Copy application code
COPY ./src ./src
COPY ./services ./services

# Create version metadata
RUN mkdir -p ci && \
    echo '{"version": "1.0.0", "service": "porkbun-mcp-server"}' > ci/semver.json

# Configure environment
ENV PYTHONPATH="${PYTHONPATH}:/usr/src/app"
ENV MCP_PORT="${MCP_PORT:-8000}"

# Expose MCP server port
EXPOSE ${MCP_PORT:-8000}

# Run MCP server
CMD ["python", "-m", "src.main"]
