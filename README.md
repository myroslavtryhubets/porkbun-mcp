# Porkbun MCP Server

A production-ready Model Context Protocol (MCP) server that exposes the complete Porkbun domain and DNS management API to AI assistants like Claude and LibreChat.

## Features

**27 MCP Tools** providing comprehensive Porkbun API access:

### Authentication & General (2 tools)
- `porkbun_ping` - Test API connectivity and get your IP
- `porkbun_get_pricing` - Get domain pricing for all TLDs

### Domain Management (4 tools)
- `porkbun_list_domains` - List all domains in account
- `porkbun_check_domain` - Check domain availability
- `porkbun_update_nameservers` - Update nameservers at registry
- `porkbun_get_nameservers` - Get current nameservers

### URL Forwarding (3 tools)
- `porkbun_add_url_forward` - Create URL redirects (301/302)
- `porkbun_get_url_forwarding` - List URL forwards
- `porkbun_delete_url_forward` - Delete URL forwards

### Glue Records (4 tools)
- `porkbun_create_glue_record` - Create glue records
- `porkbun_update_glue_record` - Update glue records
- `porkbun_delete_glue_record` - Delete glue records
- `porkbun_get_glue_records` - List glue records

### DNS Records (8 tools)
- `porkbun_create_dns_record` - Create DNS records (A, AAAA, CNAME, MX, TXT, NS, SRV, etc.)
- `porkbun_edit_dns_record` - Edit DNS record by ID
- `porkbun_edit_dns_records_by_name_type` - Bulk edit by subdomain/type
- `porkbun_delete_dns_record` - Delete DNS record by ID
- `porkbun_delete_dns_records_by_name_type` - Bulk delete by subdomain/type
- `porkbun_retrieve_dns_records` - Get all or specific DNS records
- `porkbun_retrieve_dns_records_by_name_type` - Get records by subdomain/type

### DNSSEC (3 tools)
- `porkbun_create_dnssec_record` - Create DNSSEC records
- `porkbun_get_dnssec_records` - List DNSSEC records
- `porkbun_delete_dnssec_record` - Delete DNSSEC records

### SSL Certificates (1 tool)
- `porkbun_retrieve_ssl_bundle` - Get SSL certificate bundle

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Porkbun API credentials from [porkbun.com/account/api](https://porkbun.com/account/api)
- API access must be enabled for your domains in the Porkbun dashboard

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/myroslavtryhubets/porkbun-mcp.git
cd porkbun-mcp
```

2. **Create environment configuration:**
```bash
make install
# Or manually:
cp .env.example .env
```

3. **Edit `.env` with your Porkbun API credentials:**
```bash
PORKBUN_API_KEY=your_api_key_here
PORKBUN_SECRET_API_KEY=your_secret_api_key_here
```

4. **Build and start the server:**
```bash
make build
make up
```

5. **Verify the server is running:**
```bash
make test
# Or manually:
curl http://localhost:8000/health
curl http://localhost:8000/
```

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PORKBUN_API_KEY` | Yes | - | Your Porkbun API key |
| `PORKBUN_SECRET_API_KEY` | Yes | - | Your Porkbun secret API key |
| `PORKBUN_BASE_URL` | No | `https://api.porkbun.com/api/json/v3` | Porkbun API base URL |
| `TIMEOUT` | No | `30` | Request timeout in seconds |
| `MCP_PORT` | No | `8000` | MCP server port |

### Getting Porkbun API Credentials

1. Log in to your Porkbun account
2. Go to [API Access](https://porkbun.com/account/api)
3. Create API keys
4. Enable API access for the domains you want to manage

## MCP Client Configuration

### LibreChat Configuration

**Method 1: Environment Variable**

Add to your LibreChat `.env` file:

```bash
MCP_SERVERS='{"porkbun":{"url":"http://localhost:8000/porkbun/mcp","name":"Porkbun Domain & DNS","type":"streamable-http","instructions":"You are an assistant with access to Porkbun domain and DNS management. Use these tools to help users manage their domains, configure DNS records, set up URL forwarding, and maintain domain security. Always confirm destructive operations before executing."}}'
```

**Method 2: Configuration File**

Add to `librechat.yaml`:

```yaml
mcpServers:
  porkbun:
    url: "http://localhost:8000/porkbun/mcp"
    name: "Porkbun Domain & DNS"
    type: streamable-http  # Use 'type', not 'transport'
    instructions: |
      You are an assistant with access to Porkbun domain and DNS management.
      
      Available capabilities:
      - Domain management (list, check availability, nameservers)
      - DNS record management (create, edit, delete A/AAAA/CNAME/MX/TXT/etc.)
      - URL forwarding setup
      - Glue record management
      - DNSSEC configuration
      - SSL certificate retrieval
      
      Always confirm destructive operations (delete, bulk operations) with the user first.
    timeout: 120000
```

### Claude Desktop Configuration

Add to `claude_desktop_config.json`:

**Location:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

**Configuration:**
```json
{
  "mcpServers": {
    "porkbun": {
      "url": "http://localhost:8000/porkbun/mcp",
      "transport": "http"
    }
  }
}
```

## Usage Examples

### Example Conversations with AI Assistant

**Check domain availability:**
```
User: "Is example.com available for registration?"
Assistant: [Uses porkbun_check_domain]
```

**List domains:**
```
User: "Show me all my domains"
Assistant: [Uses porkbun_list_domains]
```

**Create DNS record:**
```
User: "Add an A record for www.example.com pointing to 1.2.3.4"
Assistant: [Uses porkbun_create_dns_record with domain="example.com", record_type="A", content="1.2.3.4", name="www"]
```

**Set up URL forwarding:**
```
User: "Forward old-site.com to https://new-site.com with a permanent redirect"
Assistant: [Uses porkbun_add_url_forward with domain="old-site.com", location="https://new-site.com", forward_type="permanent"]
```

**View DNS records:**
```
User: "What are the DNS records for example.com?"
Assistant: [Uses porkbun_retrieve_dns_records]
```

## API Documentation

Once the server is running, access:

- **OpenAPI Documentation:** http://localhost:8000/docs
- **OpenAPI JSON:** http://localhost:8000/porkbun/openapi.json
- **Health Check:** http://localhost:8000/health
- **Server Info:** http://localhost:8000/

## Development

### Project Structure

```
porkbun-mcp/
├── src/
│   ├── __init__.py          # Package initialization
│   ├── main.py              # FastAPI app with MCP integration
│   └── models.py            # Pydantic configuration models
├── services/
│   ├── __init__.py
│   └── client.py            # Porkbun API client
├── ci/
│   └── semver.json          # Version metadata
├── Dockerfile               # Container build configuration
├── docker-compose.yml       # Service orchestration
├── requirements.txt         # Python dependencies
├── Makefile                 # Convenience commands
├── .env.example             # Environment template
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

### Makefile Commands

```bash
make help       # Show all available commands
make build      # Build Docker image
make up         # Start server
make down       # Stop server
make restart    # Restart server
make logs       # View server logs
make clean      # Remove containers and images
make test       # Test server endpoints
make install    # Create .env from template
```

### Running Without Docker

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your credentials
cp .env.example .env
# Edit .env with your API keys

# Run the server
python -m src.main
```

## Logging

Logs are written to:
- **Console:** Docker logs (view with `make logs`)
- **File:** `porkbun_mcp.log` (inside container)

Log format:
```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

Sensitive data (API keys) are automatically masked in logs.

## Security Best Practices

1. **Never commit `.env` file** - It contains your API credentials
2. **Restrict CORS in production** - Update `allow_origins` in `src/main.py`
3. **Use HTTPS in production** - Deploy behind a reverse proxy with SSL
4. **Rotate API keys regularly** - Generate new keys at porkbun.com/account/api
5. **Monitor API usage** - Check Porkbun dashboard for unusual activity
6. **Enable 2FA** - Protect your Porkbun account with two-factor authentication

## Troubleshooting

### Server won't start

**Check logs:**
```bash
make logs
```

**Common issues:**
- Missing API credentials in `.env`
- Port 8000 already in use (change `MCP_PORT` in `.env`)
- Invalid API keys (verify at porkbun.com/account/api)

### API calls fail

**Check API access:**
- Verify API access is enabled for your domains in Porkbun dashboard
- Test with ping endpoint: `curl http://localhost:8000/porkbun/mcp`
- Check that API keys have correct permissions

### MCP client can't connect

**LibreChat:**
- Verify `type: streamable-http` (not `transport`)
- Check URL matches server: `http://localhost:8000/porkbun/mcp`
- Restart LibreChat after configuration changes

**Claude Desktop:**
- Verify `transport: http` in config
- Check URL is accessible from Claude Desktop
- Restart Claude Desktop after configuration changes

## Rate Limits

Porkbun API has rate limits:
- **Domain checks:** Limited (rate limit info returned in response)
- **Other operations:** Generally generous limits

The server will return error messages if rate limits are exceeded.

## Architecture

This MCP server follows the **three-layer architecture pattern**:

1. **MCP Transport Layer** - FastAPI with `fastapi_mcp` for Streamable HTTP
2. **FastAPI Application Layer** - RESTful endpoints with Pydantic validation
3. **External API Client Layer** - Async `httpx` client for Porkbun API

### Key Technologies

- **FastAPI** - Modern async web framework
- **fastapi_mcp** - MCP protocol integration
- **httpx** - Async HTTP client
- **Pydantic** - Configuration and validation
- **uvicorn** - ASGI server
- **Docker** - Containerization

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

Copyright (c) 2025 Myroslav Tryhubets


## Changelog

### Version 1.0.0 (2025-10-29)

Initial release with 27 MCP tools:
- Complete Porkbun API coverage
- Domain management
- DNS record operations
- URL forwarding
- Glue records
- DNSSEC support
- SSL certificate retrieval
- Docker deployment
- LibreChat and Claude Desktop support
