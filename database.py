from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_ANON_KEY

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
except Exception:
    supabase = None  # For testing without proper config