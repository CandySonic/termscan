"""
API Security - API Key validation and authentication
"""
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from typing import Optional
import secrets
import hashlib

from app.core.config import settings

# API Key header
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)


# In-memory API keys for MVP (replace with database in production)
# Format: {"hashed_key": {"name": "Client Name", "tier": "pro", "active": True}}
API_KEYS_DB: dict = {}


def hash_api_key(api_key: str) -> str:
    """Hash an API key for secure storage"""
    return hashlib.sha256(api_key.encode()).hexdigest()


def generate_api_key(prefix: str = "hc") -> str:
    """Generate a new API key"""
    random_part = secrets.token_urlsafe(32)
    return f"{prefix}_{random_part}"


def create_api_key(name: str, tier: str = "free") -> dict:
    """Create a new API key and store it"""
    api_key = generate_api_key()
    hashed = hash_api_key(api_key)
    
    API_KEYS_DB[hashed] = {
        "name": name,
        "tier": tier,
        "active": True,
        "requests_today": 0,
        "requests_this_month": 0,
    }
    
    return {
        "api_key": api_key,  # Only returned once!
        "name": name,
        "tier": tier,
    }


def validate_api_key(api_key: str) -> Optional[dict]:
    """Validate an API key and return client info"""
    if not api_key:
        return None
    
    # Remove "Bearer " prefix if present
    if api_key.startswith("Bearer "):
        api_key = api_key[7:]
    
    hashed = hash_api_key(api_key)
    client = API_KEYS_DB.get(hashed)
    
    if client and client.get("active"):
        return client
    
    return None


async def get_api_key(api_key: str = Security(api_key_header)) -> dict:
    """Dependency to validate API key on protected routes"""
    # In development, allow requests without API key (for web UI)
    if settings.debug and not api_key:
        return {"name": "Web UI", "tier": "enterprise", "active": True}
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Include 'Authorization: Bearer your_api_key' header.",
        )
    
    client = validate_api_key(api_key)
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API key.",
        )
    
    return client


def get_rate_limit(tier: str) -> dict:
    """Get rate limits based on tier"""
    limits = {
        "free": {"per_minute": 10, "per_hour": 50, "per_month": 50},
        "starter": {"per_minute": 30, "per_hour": 200, "per_month": 500},
        "growth": {"per_minute": 100, "per_hour": 1000, "per_month": 5000},
        "enterprise": {"per_minute": 500, "per_hour": 5000, "per_month": 100000},
    }
    return limits.get(tier, limits["free"])


# Create a default development API key
if settings.debug:
    dev_key = create_api_key("Development", "enterprise")
    print(f"\n🔑 Development API Key: {dev_key['api_key']}\n")
