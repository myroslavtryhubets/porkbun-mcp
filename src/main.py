"""
Porkbun MCP Server - FastAPI with Streamable HTTP transport using fastapi_mcp

This MCP server exposes the Porkbun domain and DNS management API to AI assistants,
enabling domain operations, DNS record management, DNSSEC, and SSL certificate retrieval.
"""

import json
import logging
import os
from typing import Dict, Any, Optional, List

from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi_mcp import FastApiMCP
import uvicorn

from src.models import PorkbunConfig
from services.client import PorkbunAPIClient

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("porkbun_mcp.log")
    ]
)
logger = logging.getLogger(__name__)

# Configuration
VERSION = "1.0.0"
MCP_PORT = int(os.environ.get("MCP_PORT", "8000"))

# Initialize configuration
try:
    config = PorkbunConfig()
    logger.info("Configuration loaded successfully")
except Exception as e:
    logger.error(f"Failed to load configuration: {e}")
    raise

# Initialize Porkbun API client
api_client = PorkbunAPIClient(config)

# Create FastAPI application
app = FastAPI(
    title="Porkbun MCP Server",
    description="MCP server providing Porkbun domain and DNS management for AI assistants",
    version=VERSION,
    openapi_url="/porkbun/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create router for MCP tools
router = APIRouter()

# ===== AUTHENTICATION & GENERAL =====

@router.get("/ping", operation_id="porkbun_ping")
async def porkbun_ping() -> Dict[str, Any]:
    """
    Test Porkbun API connectivity and authentication.
    
    This tool verifies that your API credentials are valid and returns
    your current IP address. Use this to test the connection before
    performing other operations.
    
    Returns:
        API status and your IP address
    
    Example:
        "Test my Porkbun API connection"
        → porkbun_ping()
    """
    try:
        result = await api_client.ping()
        return result
    except Exception as e:
        logger.error(f"Error in porkbun_ping: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/pricing", operation_id="porkbun_get_pricing")
async def porkbun_get_pricing() -> Dict[str, Any]:
    """
    Get domain pricing information for all supported TLDs.
    
    This tool returns registration, renewal, and transfer pricing
    for all top-level domains supported by Porkbun.
    
    Returns:
        Pricing information for all TLDs
    
    Example:
        "What are the domain prices for .com and .net?"
        → porkbun_get_pricing()
    """
    try:
        result = await api_client.get_pricing()
        return result
    except Exception as e:
        logger.error(f"Error in porkbun_get_pricing: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ===== DOMAIN MANAGEMENT =====

@router.post("/domain/update-nameservers", operation_id="porkbun_update_nameservers")
async def porkbun_update_nameservers(
    domain: str,
    nameservers: List[str]
) -> Dict[str, Any]:
    """
    Update the name servers for a domain.
    
    This tool updates the authoritative name servers for a domain
    at the registry level. Changes may take time to propagate.
    
    Args:
        domain: Domain name (e.g., "example.com")
        nameservers: List of name server hostnames (e.g., ["ns1.example.com", "ns2.example.com"])
    
    Returns:
        Success status
    
    Example:
        "Update nameservers for example.com to ns1.cloudflare.com and ns2.cloudflare.com"
        → porkbun_update_nameservers(domain="example.com", nameservers=["ns1.cloudflare.com", "ns2.cloudflare.com"])
    """
    try:
        result = await api_client.update_nameservers(domain, nameservers)
        return result
    except Exception as e:
        logger.error(f"Error in porkbun_update_nameservers: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/domain/get-nameservers", operation_id="porkbun_get_nameservers")
async def porkbun_get_nameservers(domain: str) -> Dict[str, Any]:
    """
    Get the authoritative name servers for a domain.
    
    This tool retrieves the current name servers registered at the
    registry for the specified domain.
    
    Args:
        domain: Domain name (e.g., "example.com")
    
    Returns:
        List of name server hostnames
    
    Example:
        "What are the nameservers for example.com?"
        → porkbun_get_nameservers(domain="example.com")
    """
    try:
        result = await api_client.get_nameservers(domain)
        return result
    except Exception as e:
        logger.error(f"Error in porkbun_get_nameservers: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/domain/list", operation_id="porkbun_list_domains")
async def porkbun_list_domains(
    start: int = 0,
    include_labels: bool = False
) -> Dict[str, Any]:
    """
    List all domains in the account.
    
    This tool retrieves domains in chunks of 1000. Use the start parameter
    to paginate through all domains.
    
    Args:
        start: Index to start at (default: 0, increment by 1000 for next page)
        include_labels: Include label/tag information if available
    
    Returns:
        List of domains with details (status, expiry, settings)
    
    Example:
        "List all my domains"
        → porkbun_list_domains()
        
        "Show me my domains with their labels"
        → porkbun_list_domains(include_labels=true)
    """
    try:
        result = await api_client.list_domains(start, include_labels)
        return result
    except Exception as e:
        logger.error(f"Error in porkbun_list_domains: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/domain/check", operation_id="porkbun_check_domain")
async def porkbun_check_domain(domain: str) -> Dict[str, Any]:
    """
    Check domain availability for registration.
    
    This tool checks if a domain is available for registration and returns
    pricing information. Note: Domain checks are rate limited.
    
    Args:
        domain: Domain name to check (e.g., "example.com")
    
    Returns:
        Availability status and pricing information
    
    Example:
        "Is example.com available for registration?"
        → porkbun_check_domain(domain="example.com")
    """
    try:
        result = await api_client.check_domain(domain)
        return result
    except Exception as e:
        logger.error(f"Error in porkbun_check_domain: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ===== URL FORWARDING =====

@router.post("/domain/url-forward/add", operation_id="porkbun_add_url_forward")
async def porkbun_add_url_forward(
    domain: str,
    location: str,
    forward_type: str = "temporary",
    subdomain: str = "",
    include_path: str = "no",
    wildcard: str = "no"
) -> Dict[str, Any]:
    """
    Add URL forwarding for a domain or subdomain.
    
    This tool sets up HTTP redirects from your domain to another URL.
    You can configure temporary (302) or permanent (301) redirects.
    
    Args:
        domain: Domain name (e.g., "example.com")
        location: Target URL for forwarding (e.g., "https://newsite.com")
        forward_type: "temporary" (302) or "permanent" (301) redirect
        subdomain: Subdomain to forward (empty for root domain)
        include_path: Include URI path in redirection ("yes" or "no")
        wildcard: Also forward all subdomains ("yes" or "no")
    
    Returns:
        Success status
    
    Example:
        "Forward example.com to https://newsite.com with a temporary redirect"
        → porkbun_add_url_forward(domain="example.com", location="https://newsite.com", forward_type="temporary")
        
        "Forward blog.example.com to https://medium.com/@user permanently"
        → porkbun_add_url_forward(domain="example.com", location="https://medium.com/@user", subdomain="blog", forward_type="permanent")
    """
    try:
        result = await api_client.add_url_forward(
            domain, location, forward_type, subdomain, include_path, wildcard
        )
        return result
    except Exception as e:
        logger.error(f"Error in porkbun_add_url_forward: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/domain/url-forward/get", operation_id="porkbun_get_url_forwarding")
async def porkbun_get_url_forwarding(domain: str) -> Dict[str, Any]:
    """
    Get URL forwarding configuration for a domain.
    
    This tool retrieves all URL forwarding rules configured for
    the specified domain.
    
    Args:
        domain: Domain name (e.g., "example.com")
    
    Returns:
        List of URL forwarding rules with IDs, targets, and settings
    
    Example:
        "Show me all URL forwards for example.com"
        → porkbun_get_url_forwarding(domain="example.com")
    """
    try:
        result = await api_client.get_url_forwarding(domain)
        return result
    except Exception as e:
        logger.error(f"Error in porkbun_get_url_forwarding: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/domain/url-forward/delete", operation_id="porkbun_delete_url_forward")
async def porkbun_delete_url_forward(
    domain: str,
    record_id: str
) -> Dict[str, Any]:
    """
    Delete a URL forward rule.
    
    This tool removes a specific URL forwarding rule by its ID.
    Use porkbun_get_url_forwarding to find the record ID.
    
    Args:
        domain: Domain name (e.g., "example.com")
        record_id: ID of the forward record to delete
    
    Returns:
        Success status
    
    Example:
        "Delete the URL forward with ID 22049216 for example.com"
        → porkbun_delete_url_forward(domain="example.com", record_id="22049216")
    """
    try:
        result = await api_client.delete_url_forward(domain, record_id)
        return result
    except Exception as e:
        logger.error(f"Error in porkbun_delete_url_forward: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ===== GLUE RECORDS =====

@router.post("/domain/glue/create", operation_id="porkbun_create_glue_record")
async def porkbun_create_glue_record(
    domain: str,
    glue_host: str,
    ips: List[str]
) -> Dict[str, Any]:
    """
    Create a glue record for a domain.
    
    Glue records are required when you use nameservers that are subdomains
    of the domain itself (e.g., ns1.example.com for example.com).
    
    Args:
        domain: Domain name (e.g., "example.com")
        glue_host: Glue host subdomain (e.g., "ns1")
        ips: List of IP addresses (IPv4 and/or IPv6)
    
    Returns:
        Success status
    
    Example:
        "Create glue record ns1.example.com pointing to 192.168.1.1"
        → porkbun_create_glue_record(domain="example.com", glue_host="ns1", ips=["192.168.1.1"])
    """
    try:
        result = await api_client.create_glue_record(domain, glue_host, ips)
        return result
    except Exception as e:
        logger.error(f"Error in porkbun_create_glue_record: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/domain/glue/update", operation_id="porkbun_update_glue_record")
async def porkbun_update_glue_record(
    domain: str,
    glue_host: str,
    ips: List[str]
) -> Dict[str, Any]:
    """
    Update a glue record for a domain.
    
    This tool replaces the existing IP addresses with new ones for
    the specified glue host.
    
    Args:
        domain: Domain name (e.g., "example.com")
        glue_host: Glue host subdomain (e.g., "ns1")
        ips: List of IP addresses (IPv4 and/or IPv6)
    
    Returns:
        Success status
    
    Example:
        "Update ns1.example.com glue record to 192.168.1.2"
        → porkbun_update_glue_record(domain="example.com", glue_host="ns1", ips=["192.168.1.2"])
    """
    try:
        result = await api_client.update_glue_record(domain, glue_host, ips)
        return result
    except Exception as e:
        logger.error(f"Error in porkbun_update_glue_record: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/domain/glue/delete", operation_id="porkbun_delete_glue_record")
async def porkbun_delete_glue_record(
    domain: str,
    glue_host: str
) -> Dict[str, Any]:
    """
    Delete a glue record for a domain.
    
    This tool removes the glue record for the specified glue host.
    
    Args:
        domain: Domain name (e.g., "example.com")
        glue_host: Glue host subdomain (e.g., "ns1")
    
    Returns:
        Success status
    
    Example:
        "Delete glue record ns1.example.com"
        → porkbun_delete_glue_record(domain="example.com", glue_host="ns1")
    """
    try:
        result = await api_client.delete_glue_record(domain, glue_host)
        return result
    except Exception as e:
        logger.error(f"Error in porkbun_delete_glue_record: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/domain/glue/list", operation_id="porkbun_get_glue_records")
async def porkbun_get_glue_records(domain: str) -> Dict[str, Any]:
    """
    Get all glue records for a domain.
    
    This tool retrieves all glue records configured for the specified domain.
    
    Args:
        domain: Domain name (e.g., "example.com")
    
    Returns:
        List of glue records with their IP addresses
    
    Example:
        "Show me all glue records for example.com"
        → porkbun_get_glue_records(domain="example.com")
    """
    try:
        result = await api_client.get_glue_records(domain)
        return result
    except Exception as e:
        logger.error(f"Error in porkbun_get_glue_records: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ===== DNS RECORDS =====

@router.post("/dns/create", operation_id="porkbun_create_dns_record")
async def porkbun_create_dns_record(
    domain: str,
    record_type: str,
    content: str,
    name: str = "",
    ttl: int = 600,
    prio: Optional[str] = None,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a DNS record for a domain.
    
    This tool creates a new DNS record. Supported types include:
    A, AAAA, CNAME, MX, TXT, NS, SRV, TLSA, CAA, ALIAS, HTTPS, SVCB, SSHFP.
    
    Args:
        domain: Domain name (e.g., "example.com")
        record_type: Record type (A, AAAA, CNAME, MX, TXT, etc.)
        content: Record content/answer (e.g., IP address, hostname)
        name: Subdomain (empty for root, "*" for wildcard)
        ttl: Time to live in seconds (minimum 600)
        prio: Priority for MX/SRV records
        notes: Optional notes for the record
    
    Returns:
        Success status and record ID
    
    Example:
        "Create an A record for www.example.com pointing to 1.1.1.1"
        → porkbun_create_dns_record(domain="example.com", record_type="A", content="1.1.1.1", name="www")
        
        "Add a TXT record for domain verification"
        → porkbun_create_dns_record(domain="example.com", record_type="TXT", content="verification-code-here", name="")
    """
    try:
        result = await api_client.create_dns_record(
            domain, record_type, content, name, ttl, prio, notes
        )
        return result
    except Exception as e:
        logger.error(f"Error in porkbun_create_dns_record: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/dns/edit", operation_id="porkbun_edit_dns_record")
async def porkbun_edit_dns_record(
    domain: str,
    record_id: str,
    record_type: str,
    content: str,
    name: str = "",
    ttl: int = 600,
    prio: Optional[str] = None,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Edit a DNS record by domain and record ID.
    
    This tool updates an existing DNS record. Use porkbun_retrieve_dns_records
    to find the record ID.
    
    Args:
        domain: Domain name (e.g., "example.com")
        record_id: DNS record ID
        record_type: Record type
        content: Record content/answer
        name: Subdomain
        ttl: Time to live in seconds
        prio: Priority for MX/SRV records
        notes: Notes (empty string to clear, null for no change)
    
    Returns:
        Success status
    
    Example:
        "Update DNS record 106926659 to point to 1.1.1.2"
        → porkbun_edit_dns_record(domain="example.com", record_id="106926659", record_type="A", content="1.1.1.2", name="www")
    """
    try:
        result = await api_client.edit_dns_record(
            domain, record_id, record_type, content, name, ttl, prio, notes
        )
        return result
    except Exception as e:
        logger.error(f"Error in porkbun_edit_dns_record: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/dns/edit-by-name-type", operation_id="porkbun_edit_dns_records_by_name_type")
async def porkbun_edit_dns_records_by_name_type(
    domain: str,
    record_type: str,
    content: str,
    subdomain: str = "",
    ttl: int = 600,
    prio: Optional[str] = None,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Edit all DNS records matching subdomain and type.
    
    This tool updates all records that match the specified subdomain and type.
    Useful for bulk updates.
    
    Args:
        domain: Domain name (e.g., "example.com")
        record_type: Record type (A, AAAA, CNAME, etc.)
        content: New record content
        subdomain: Subdomain (empty for root)
        ttl: Time to live in seconds
        prio: Priority for MX/SRV records
        notes: Optional notes
    
    Returns:
        Success status
    
    Example:
        "Update all A records for www.example.com to point to 2.2.2.2"
        → porkbun_edit_dns_records_by_name_type(domain="example.com", record_type="A", content="2.2.2.2", subdomain="www")
    """
    try:
        result = await api_client.edit_dns_records_by_name_type(
            domain, record_type, content, subdomain, ttl, prio, notes
        )
        return result
    except Exception as e:
        logger.error(f"Error in porkbun_edit_dns_records_by_name_type: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/dns/delete", operation_id="porkbun_delete_dns_record")
async def porkbun_delete_dns_record(
    domain: str,
    record_id: str
) -> Dict[str, Any]:
    """
    Delete a specific DNS record by ID.
    
    This tool removes a DNS record. Use porkbun_retrieve_dns_records
    to find the record ID.
    
    Args:
        domain: Domain name (e.g., "example.com")
        record_id: DNS record ID
    
    Returns:
        Success status
    
    Example:
        "Delete DNS record 106926659 from example.com"
        → porkbun_delete_dns_record(domain="example.com", record_id="106926659")
    """
    try:
        result = await api_client.delete_dns_record(domain, record_id)
        return result
    except Exception as e:
        logger.error(f"Error in porkbun_delete_dns_record: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/dns/delete-by-name-type", operation_id="porkbun_delete_dns_records_by_name_type")
async def porkbun_delete_dns_records_by_name_type(
    domain: str,
    record_type: str,
    subdomain: str = ""
) -> Dict[str, Any]:
    """
    Delete all DNS records matching subdomain and type.
    
    This tool removes all records that match the specified subdomain and type.
    Use with caution as it affects multiple records.
    
    Args:
        domain: Domain name (e.g., "example.com")
        record_type: Record type (A, AAAA, CNAME, etc.)
        subdomain: Subdomain (empty for root)
    
    Returns:
        Success status
    
    Example:
        "Delete all A records for www.example.com"
        → porkbun_delete_dns_records_by_name_type(domain="example.com", record_type="A", subdomain="www")
    """
    try:
        result = await api_client.delete_dns_records_by_name_type(
            domain, record_type, subdomain
        )
        return result
    except Exception as e:
        logger.error(f"Error in porkbun_delete_dns_records_by_name_type: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/dns/retrieve", operation_id="porkbun_retrieve_dns_records")
async def porkbun_retrieve_dns_records(
    domain: str,
    record_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Retrieve DNS records for a domain.
    
    This tool retrieves all DNS records for a domain, or a specific record
    if you provide a record ID.
    
    Args:
        domain: Domain name (e.g., "example.com")
        record_id: Optional record ID to retrieve specific record
    
    Returns:
        List of DNS records with details (type, content, TTL, priority, notes)
    
    Example:
        "Show me all DNS records for example.com"
        → porkbun_retrieve_dns_records(domain="example.com")
        
        "Get DNS record 106926659 for example.com"
        → porkbun_retrieve_dns_records(domain="example.com", record_id="106926659")
    """
    try:
        result = await api_client.retrieve_dns_records(domain, record_id)
        return result
    except Exception as e:
        logger.error(f"Error in porkbun_retrieve_dns_records: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/dns/retrieve-by-name-type", operation_id="porkbun_retrieve_dns_records_by_name_type")
async def porkbun_retrieve_dns_records_by_name_type(
    domain: str,
    record_type: str,
    subdomain: str = ""
) -> Dict[str, Any]:
    """
    Retrieve DNS records by subdomain and type.
    
    This tool retrieves all records matching the specified subdomain and type.
    Useful for finding specific types of records.
    
    Args:
        domain: Domain name (e.g., "example.com")
        record_type: Record type (A, AAAA, CNAME, MX, TXT, etc.)
        subdomain: Subdomain (empty for root)
    
    Returns:
        List of matching DNS records
    
    Example:
        "Show me all A records for www.example.com"
        → porkbun_retrieve_dns_records_by_name_type(domain="example.com", record_type="A", subdomain="www")
    """
    try:
        result = await api_client.retrieve_dns_records_by_name_type(
            domain, record_type, subdomain
        )
        return result
    except Exception as e:
        logger.error(f"Error in porkbun_retrieve_dns_records_by_name_type: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ===== DNSSEC =====

@router.post("/dnssec/create", operation_id="porkbun_create_dnssec_record")
async def porkbun_create_dnssec_record(
    domain: str,
    key_tag: str,
    alg: str,
    digest_type: str,
    digest: str,
    max_sig_life: str = "",
    key_data_flags: str = "",
    key_data_protocol: str = "",
    key_data_algo: str = "",
    key_data_pub_key: str = ""
) -> Dict[str, Any]:
    """
    Create a DNSSEC record at the registry.
    
    This tool creates DNSSEC (DNS Security Extensions) records to
    cryptographically sign your DNS data. Requirements vary by registry.
    
    Args:
        domain: Domain name (e.g., "example.com")
        key_tag: Key Tag
        alg: DS Data Algorithm
        digest_type: Digest Type
        digest: Digest hash
        max_sig_life: Max Sig Life (optional)
        key_data_flags: Key Data Flags (optional)
        key_data_protocol: Key Data Protocol (optional)
        key_data_algo: Key Data Algorithm (optional)
        key_data_pub_key: Key Data Public Key (optional)
    
    Returns:
        Success status
    
    Example:
        "Add DNSSEC record for example.com"
        → porkbun_create_dnssec_record(domain="example.com", key_tag="64087", alg="13", digest_type="2", digest="15E445BD08128BDC213E25F1C8227DF4CB35186CAC701C1C335B2C406D5530DC")
    """
    try:
        result = await api_client.create_dnssec_record(
            domain, key_tag, alg, digest_type, digest,
            max_sig_life, key_data_flags, key_data_protocol,
            key_data_algo, key_data_pub_key
        )
        return result
    except Exception as e:
        logger.error(f"Error in porkbun_create_dnssec_record: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/dnssec/get", operation_id="porkbun_get_dnssec_records")
async def porkbun_get_dnssec_records(domain: str) -> Dict[str, Any]:
    """
    Get DNSSEC records for a domain from the registry.
    
    This tool retrieves all DNSSEC records currently configured
    at the registry for the specified domain.
    
    Args:
        domain: Domain name (e.g., "example.com")
    
    Returns:
        DNSSEC records with key tags, algorithms, and digests
    
    Example:
        "Show me DNSSEC records for example.com"
        → porkbun_get_dnssec_records(domain="example.com")
    """
    try:
        result = await api_client.get_dnssec_records(domain)
        return result
    except Exception as e:
        logger.error(f"Error in porkbun_get_dnssec_records: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/dnssec/delete", operation_id="porkbun_delete_dnssec_record")
async def porkbun_delete_dnssec_record(
    domain: str,
    key_tag: str
) -> Dict[str, Any]:
    """
    Delete a DNSSEC record at the registry.
    
    This tool removes a DNSSEC record. Note that most registries delete
    all records with matching data, not just the record with the matching key tag.
    
    Args:
        domain: Domain name (e.g., "example.com")
        key_tag: Key Tag of the record to delete
    
    Returns:
        Success status
    
    Example:
        "Delete DNSSEC record with key tag 64087 from example.com"
        → porkbun_delete_dnssec_record(domain="example.com", key_tag="64087")
    """
    try:
        result = await api_client.delete_dnssec_record(domain, key_tag)
        return result
    except Exception as e:
        logger.error(f"Error in porkbun_delete_dnssec_record: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ===== SSL CERTIFICATES =====

@router.get("/ssl/retrieve", operation_id="porkbun_retrieve_ssl_bundle")
async def porkbun_retrieve_ssl_bundle(domain: str) -> Dict[str, Any]:
    """
    Retrieve SSL certificate bundle for a domain.
    
    This tool retrieves the complete SSL/TLS certificate bundle including
    the certificate chain, private key, and public key for the domain.
    
    Args:
        domain: Domain name (e.g., "example.com")
    
    Returns:
        SSL certificate bundle with certificate chain, private key, and public key
    
    Example:
        "Get the SSL certificate for example.com"
        → porkbun_retrieve_ssl_bundle(domain="example.com")
    """
    try:
        result = await api_client.retrieve_ssl_bundle(domain)
        return result
    except Exception as e:
        logger.error(f"Error in porkbun_retrieve_ssl_bundle: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ===== HEALTH & INFO ENDPOINTS =====

@app.get('/health', status_code=200)
def health_check():
    """Health check endpoint for monitoring and orchestration."""
    try:
        with open('/usr/src/app/ci/semver.json', 'r', encoding="utf-8") as f:
            return json.load(f)
    except:
        return {
            "version": VERSION,
            "service": "porkbun-mcp-server",
            "transport": "streamable-http",
            "status": "healthy"
        }


@app.get("/")
def root():
    """Root endpoint with MCP server information."""
    return {
        "name": "Porkbun MCP Server",
        "version": VERSION,
        "transport": "streamable-http",
        "mcp_endpoint": "/porkbun/mcp",
        "tools": 27,
        "categories": {
            "authentication": 2,
            "domain_management": 4,
            "url_forwarding": 3,
            "glue_records": 4,
            "dns_records": 8,
            "dnssec": 3,
            "ssl": 1
        },
        "health": "/health",
        "docs": "/docs",
        "api_docs": "https://porkbun.com/api/json/v3/documentation"
    }


# Include router in application
app.include_router(router, prefix="/porkbun", include_in_schema=False)
app.include_router(router)

# Initialize FastApiMCP with Streamable HTTP transport
mcp = FastApiMCP(
    app,
    name="Porkbun Domain & DNS Management",
    description="""Comprehensive Porkbun domain and DNS management API for AI assistants.

This MCP server provides complete access to Porkbun's domain management platform, enabling:

**Domain Operations:**
- Check domain availability and pricing
- List all domains in account
- Manage nameservers at registry level
- Configure URL forwarding/redirects
- Create and manage glue records

**DNS Management:**
- Create, edit, and delete DNS records (A, AAAA, CNAME, MX, TXT, NS, SRV, TLSA, CAA, etc.)
- Bulk operations by subdomain and type
- Retrieve records with flexible filtering

**DNSSEC:**
- Create and manage DNSSEC records at registry
- Enable DNS security extensions

**SSL Certificates:**
- Retrieve SSL certificate bundles with private keys

Use these tools to help users manage their domains, configure DNS records, set up redirects, and maintain domain security. Always confirm destructive operations (delete, bulk edit) before executing.""",
    include_operations=[
        # Authentication & General
        "porkbun_ping",
        "porkbun_get_pricing",
        # Domain Management
        "porkbun_update_nameservers",
        "porkbun_get_nameservers",
        "porkbun_list_domains",
        "porkbun_check_domain",
        # URL Forwarding
        "porkbun_add_url_forward",
        "porkbun_get_url_forwarding",
        "porkbun_delete_url_forward",
        # Glue Records
        "porkbun_create_glue_record",
        "porkbun_update_glue_record",
        "porkbun_delete_glue_record",
        "porkbun_get_glue_records",
        # DNS Records
        "porkbun_create_dns_record",
        "porkbun_edit_dns_record",
        "porkbun_edit_dns_records_by_name_type",
        "porkbun_delete_dns_record",
        "porkbun_delete_dns_records_by_name_type",
        "porkbun_retrieve_dns_records",
        "porkbun_retrieve_dns_records_by_name_type",
        # DNSSEC
        "porkbun_create_dnssec_record",
        "porkbun_get_dnssec_records",
        "porkbun_delete_dnssec_record",
        # SSL
        "porkbun_retrieve_ssl_bundle"
    ],
)

# Mount MCP transport at dedicated endpoint
mcp.mount_http(mount_path="/porkbun/mcp")

logger.info("Starting Porkbun MCP server with Streamable HTTP transport")
logger.info(f"MCP endpoint: /porkbun/mcp")
logger.info(f"Health check: /health")
logger.info(f"API documentation: /docs")
logger.info(f"Server port: {MCP_PORT}")
logger.info(f"Total MCP tools: 27")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=MCP_PORT)
