import os
from supabase import create_client, Client
from app.config import get_config

config = get_config()

def get_supabase_client() -> Client:
    """
    Get a Supabase client using the anon key.
    This client has the same permissions as an authenticated user.
    """
    url = config.SUPABASE_URL
    key = config.SUPABASE_KEY
    
    if not url or not key:
        raise ValueError("Supabase URL and key must be set in environment variables")
    
    return create_client(url, key)

def get_supabase_admin_client() -> Client:
    """
    Get a Supabase client using the service role key.
    This client has admin privileges and can bypass RLS policies.
    Use with caution.
    """
    url = config.SUPABASE_URL
    service_key = config.SUPABASE_SERVICE_KEY
    
    if not url or not service_key:
        raise ValueError("Supabase URL and service key must be set in environment variables")
    
    return create_client(url, service_key)

# Default clients
supabase = get_supabase_client()
supabase_admin = get_supabase_admin_client() 