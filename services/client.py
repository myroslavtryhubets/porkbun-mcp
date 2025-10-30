"""
Porkbun API Client - Async HTTP client for Porkbun API integration.

This client handles all Porkbun API operations including:
- Authentication and ping
- Domain management (name servers, URL forwarding, glue records)
- DNS record management
- DNSSEC management
- SSL certificate retrieval
"""

import httpx
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class PorkbunAPIClient:
    """
    Async HTTP client for Porkbun API integration.
    Handles authentication, error normalization, and logging.
    """
    
    def __init__(self, config):
        """
        Initialize Porkbun API client with configuration.
        
        Args:
            config: PorkbunConfig instance with API credentials and settings
        """
        self.api_key = config.porkbun_api_key
        self.secret_api_key = config.porkbun_secret_api_key
        self.base_url = config.porkbun_base_url.rstrip('/')
        self.timeout = config.timeout
        self.auth_payload = config.auth_payload
        
        # Log initialization with masked credentials
        masked_key = (
            f"{self.api_key[:8]}...{self.api_key[-4:]}" 
            if len(self.api_key) > 12 
            else "***"
        )
        masked_secret = (
            f"{self.secret_api_key[:8]}...{self.secret_api_key[-4:]}"
            if len(self.secret_api_key) > 12
            else "***"
        )
        logger.info("Porkbun API client initialized")
        logger.info(f"Base URL: {self.base_url}")
        logger.info(f"API Key: {masked_key}")
        logger.info(f"Secret API Key: {masked_secret}")
        logger.info(f"Timeout: {self.timeout}s")
    
    async def _request(
        self, 
        endpoint: str,
        payload: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Centralized HTTP POST request handler with error normalization.
        All Porkbun API requests use POST with JSON body.
        
        Args:
            endpoint: API endpoint path (relative to base_url)
            payload: Additional JSON data to merge with auth credentials
            
        Returns:
            JSON response as dictionary
            
        Raises:
            Exception: Normalized error with status code and message
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        # Merge auth payload with request payload
        request_data = {**self.auth_payload}
        if payload:
            request_data.update(payload)
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                logger.info(f"POST {url}")
                
                response = await client.post(
                    url=url,
                    json=request_data
                )
                
                response.raise_for_status()
                result = response.json()
                
                # Check Porkbun API status
                if result.get("status") == "ERROR":
                    error_msg = result.get("message", "Unknown error")
                    logger.error(f"Porkbun API error: {error_msg}")
                    raise Exception(f"Porkbun API error: {error_msg}")
                
                logger.info(f"Response: {response.status_code} - {result.get('status')}")
                return result
                
            except httpx.HTTPStatusError as e:
                error_detail = e.response.text
                logger.error(f"HTTP {e.response.status_code}: {error_detail}")
                raise Exception(
                    f"API error {e.response.status_code}: {error_detail}"
                )
                
            except httpx.TimeoutException:
                logger.error(f"Request timeout after {self.timeout}s")
                raise Exception(
                    f"Request timeout after {self.timeout}s"
                )
                
            except httpx.NetworkError as e:
                logger.error(f"Network error: {str(e)}")
                raise Exception(f"Network error: {str(e)}")
                
            except Exception as e:
                if "Porkbun API error" in str(e):
                    raise
                logger.error(f"Unexpected error: {str(e)}")
                raise Exception(f"Request failed: {str(e)}")
    
    # ===== AUTHENTICATION & GENERAL =====
    
    async def ping(self) -> Dict[str, Any]:
        """
        Test API connectivity and authentication.
        Returns your IP address.
        """
        return await self._request("ping")
    
    async def get_pricing(self) -> Dict[str, Any]:
        """
        Get domain pricing information for all supported TLDs.
        This command does not require authentication.
        """
        # Pricing endpoint doesn't need auth, but we'll send it anyway
        return await self._request("pricing/get")
    
    # ===== DOMAIN MANAGEMENT =====
    
    async def update_nameservers(
        self,
        domain: str,
        nameservers: List[str]
    ) -> Dict[str, Any]:
        """
        Update the name servers for a domain.
        
        Args:
            domain: Domain name (e.g., example.com)
            nameservers: List of name server hostnames
        """
        return await self._request(
            f"domain/updateNs/{domain}",
            {"ns": nameservers}
        )
    
    async def get_nameservers(self, domain: str) -> Dict[str, Any]:
        """
        Get the authoritative name servers for a domain.
        
        Args:
            domain: Domain name (e.g., example.com)
        """
        return await self._request(f"domain/getNs/{domain}")
    
    async def list_domains(
        self,
        start: int = 0,
        include_labels: bool = False
    ) -> Dict[str, Any]:
        """
        List all domains in account.
        Domains are returned in chunks of 1000.
        
        Args:
            start: Index to start at (default: 0)
            include_labels: Include label information if available
        """
        payload = {"start": str(start)}
        if include_labels:
            payload["includeLabels"] = "yes"
        return await self._request("domain/listAll", payload)
    
    async def check_domain(self, domain: str) -> Dict[str, Any]:
        """
        Check domain availability.
        Note: Domain checks are rate limited.
        
        Args:
            domain: Domain name to check (e.g., example.com)
        """
        return await self._request(f"domain/checkDomain/{domain}")
    
    # ===== URL FORWARDING =====
    
    async def add_url_forward(
        self,
        domain: str,
        location: str,
        forward_type: str = "temporary",
        subdomain: str = "",
        include_path: str = "no",
        wildcard: str = "no"
    ) -> Dict[str, Any]:
        """
        Add URL forwarding for a domain.
        
        Args:
            domain: Domain name
            location: Target URL for forwarding
            forward_type: "temporary" or "permanent"
            subdomain: Subdomain to forward (empty for root)
            include_path: Include URI path in redirection ("yes" or "no")
            wildcard: Also forward all subdomains ("yes" or "no")
        """
        payload = {
            "subdomain": subdomain,
            "location": location,
            "type": forward_type,
            "includePath": include_path,
            "wildcard": wildcard
        }
        return await self._request(f"domain/addUrlForward/{domain}", payload)
    
    async def get_url_forwarding(self, domain: str) -> Dict[str, Any]:
        """
        Get URL forwarding configuration for a domain.
        
        Args:
            domain: Domain name
        """
        return await self._request(f"domain/getUrlForwarding/{domain}")
    
    async def delete_url_forward(
        self,
        domain: str,
        record_id: str
    ) -> Dict[str, Any]:
        """
        Delete a URL forward for a domain.
        
        Args:
            domain: Domain name
            record_id: ID of the forward record to delete
        """
        return await self._request(f"domain/deleteUrlForward/{domain}/{record_id}")
    
    # ===== GLUE RECORDS =====
    
    async def create_glue_record(
        self,
        domain: str,
        glue_host: str,
        ips: List[str]
    ) -> Dict[str, Any]:
        """
        Create glue record for a domain.
        
        Args:
            domain: Domain name
            glue_host: Glue host subdomain (e.g., "ns1")
            ips: List of IP addresses (IPv4 and/or IPv6)
        """
        return await self._request(
            f"domain/createGlue/{domain}/{glue_host}",
            {"ips": ips}
        )
    
    async def update_glue_record(
        self,
        domain: str,
        glue_host: str,
        ips: List[str]
    ) -> Dict[str, Any]:
        """
        Update glue record for a domain.
        Current IPs will be replaced with new ones.
        
        Args:
            domain: Domain name
            glue_host: Glue host subdomain (e.g., "ns1")
            ips: List of IP addresses (IPv4 and/or IPv6)
        """
        return await self._request(
            f"domain/updateGlue/{domain}/{glue_host}",
            {"ips": ips}
        )
    
    async def delete_glue_record(
        self,
        domain: str,
        glue_host: str
    ) -> Dict[str, Any]:
        """
        Delete glue record for a domain.
        
        Args:
            domain: Domain name
            glue_host: Glue host subdomain (e.g., "ns1")
        """
        return await self._request(f"domain/deleteGlue/{domain}/{glue_host}")
    
    async def get_glue_records(self, domain: str) -> Dict[str, Any]:
        """
        Get all glue records for a domain.
        
        Args:
            domain: Domain name
        """
        return await self._request(f"domain/getGlue/{domain}")
    
    # ===== DNS RECORDS =====
    
    async def create_dns_record(
        self,
        domain: str,
        record_type: str,
        content: str,
        name: str = "",
        ttl: int = 600,
        prio: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a DNS record.
        
        Args:
            domain: Domain name
            record_type: Record type (A, MX, CNAME, ALIAS, TXT, NS, AAAA, SRV, TLSA, CAA, HTTPS, SVCB, SSHFP)
            content: Record content/answer
            name: Subdomain (empty for root, * for wildcard)
            ttl: Time to live in seconds (minimum 600)
            prio: Priority (for MX, SRV records)
            notes: Notes for the record
        """
        payload = {
            "name": name,
            "type": record_type,
            "content": content,
            "ttl": str(ttl)
        }
        if prio is not None:
            payload["prio"] = prio
        if notes is not None:
            payload["notes"] = notes
        return await self._request(f"dns/create/{domain}", payload)
    
    async def edit_dns_record(
        self,
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
        Edit a DNS record by domain and ID.
        
        Args:
            domain: Domain name
            record_id: DNS record ID
            record_type: Record type
            content: Record content/answer
            name: Subdomain
            ttl: Time to live in seconds
            prio: Priority
            notes: Notes (empty string to clear, null for no change)
        """
        payload = {
            "name": name,
            "type": record_type,
            "content": content,
            "ttl": str(ttl)
        }
        if prio is not None:
            payload["prio"] = prio
        if notes is not None:
            payload["notes"] = notes
        return await self._request(f"dns/edit/{domain}/{record_id}", payload)
    
    async def edit_dns_records_by_name_type(
        self,
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
        
        Args:
            domain: Domain name
            record_type: Record type
            content: Record content/answer
            subdomain: Subdomain (empty for root)
            ttl: Time to live in seconds
            prio: Priority
            notes: Notes
        """
        payload = {
            "content": content,
            "ttl": str(ttl)
        }
        if prio is not None:
            payload["prio"] = prio
        if notes is not None:
            payload["notes"] = notes
        
        endpoint = f"dns/editByNameType/{domain}/{record_type}"
        if subdomain:
            endpoint += f"/{subdomain}"
        return await self._request(endpoint, payload)
    
    async def delete_dns_record(
        self,
        domain: str,
        record_id: str
    ) -> Dict[str, Any]:
        """
        Delete a specific DNS record by ID.
        
        Args:
            domain: Domain name
            record_id: DNS record ID
        """
        return await self._request(f"dns/delete/{domain}/{record_id}")
    
    async def delete_dns_records_by_name_type(
        self,
        domain: str,
        record_type: str,
        subdomain: str = ""
    ) -> Dict[str, Any]:
        """
        Delete all DNS records matching subdomain and type.
        
        Args:
            domain: Domain name
            record_type: Record type
            subdomain: Subdomain (empty for root)
        """
        endpoint = f"dns/deleteByNameType/{domain}/{record_type}"
        if subdomain:
            endpoint += f"/{subdomain}"
        return await self._request(endpoint)
    
    async def retrieve_dns_records(
        self,
        domain: str,
        record_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve all DNS records for a domain, or a specific record by ID.
        
        Args:
            domain: Domain name
            record_id: Optional DNS record ID for specific record
        """
        endpoint = f"dns/retrieve/{domain}"
        if record_id:
            endpoint += f"/{record_id}"
        return await self._request(endpoint)
    
    async def retrieve_dns_records_by_name_type(
        self,
        domain: str,
        record_type: str,
        subdomain: str = ""
    ) -> Dict[str, Any]:
        """
        Retrieve DNS records by subdomain and type.
        
        Args:
            domain: Domain name
            record_type: Record type
            subdomain: Subdomain (empty for root)
        """
        endpoint = f"dns/retrieveByNameType/{domain}/{record_type}"
        if subdomain:
            endpoint += f"/{subdomain}"
        return await self._request(endpoint)
    
    # ===== DNSSEC =====
    
    async def create_dnssec_record(
        self,
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
        
        Args:
            domain: Domain name
            key_tag: Key Tag
            alg: DS Data Algorithm
            digest_type: Digest Type
            digest: Digest
            max_sig_life: Max Sig Life (optional)
            key_data_flags: Key Data Flags (optional)
            key_data_protocol: Key Data Protocol (optional)
            key_data_algo: Key Data Algorithm (optional)
            key_data_pub_key: Key Data Public Key (optional)
        """
        payload = {
            "keyTag": key_tag,
            "alg": alg,
            "digestType": digest_type,
            "digest": digest,
            "maxSigLife": max_sig_life,
            "keyDataFlags": key_data_flags,
            "keyDataProtocol": key_data_protocol,
            "keyDataAlgo": key_data_algo,
            "keyDataPubKey": key_data_pub_key
        }
        return await self._request(f"dns/createDnssecRecord/{domain}", payload)
    
    async def get_dnssec_records(self, domain: str) -> Dict[str, Any]:
        """
        Get DNSSEC records for a domain from the registry.
        
        Args:
            domain: Domain name
        """
        return await self._request(f"dns/getDnssecRecords/{domain}")
    
    async def delete_dnssec_record(
        self,
        domain: str,
        key_tag: str
    ) -> Dict[str, Any]:
        """
        Delete a DNSSEC record at the registry.
        Note: Most registries delete all records with matching data.
        
        Args:
            domain: Domain name
            key_tag: Key Tag of the record to delete
        """
        return await self._request(f"dns/deleteDnssecRecord/{domain}/{key_tag}")
    
    # ===== SSL CERTIFICATES =====
    
    async def retrieve_ssl_bundle(self, domain: str) -> Dict[str, Any]:
        """
        Retrieve SSL certificate bundle for a domain.
        
        Args:
            domain: Domain name
        """
        return await self._request(f"ssl/retrieve/{domain}")
