"""
Configuration models for Porkbun MCP Server.

This module defines the configuration schema using Pydantic settings,
automatically loading from environment variables and .env file.
"""

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PorkbunConfig(BaseSettings):
    """
    Configuration model for Porkbun MCP Server.
    
    Automatically loads from .env file and environment variables.
    All Porkbun API credentials and settings are defined here.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Required Porkbun API credentials
    porkbun_api_key: str = Field(
        ...,
        description="Porkbun API key from porkbun.com/account/api"
    )
    
    porkbun_secret_api_key: str = Field(
        ...,
        description="Porkbun secret API key from porkbun.com/account/api"
    )
    
    # Optional API settings with defaults
    porkbun_base_url: str = Field(
        default="https://api.porkbun.com/api/json/v3",
        description="Base URL for Porkbun API"
    )
    
    timeout: int = Field(
        default=30,
        description="Request timeout in seconds",
        ge=1,
        le=300
    )
    
    # MCP Server settings
    mcp_port: int = Field(
        default=8000,
        description="MCP server port",
        ge=1000,
        le=65535
    )
    
    @property
    def auth_payload(self) -> dict:
        """Generate authentication payload for API requests"""
        return {
            "apikey": self.porkbun_api_key,
            "secretapikey": self.porkbun_secret_api_key
        }
