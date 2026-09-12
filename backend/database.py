import os
from fastapi import HTTPException, status
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

from typing import Optional

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Thieu bien moi truong SUPABASE_URL hoac SUPABASE_KEY trong .env")

supabase: Optional[Client] = None
try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"[WARN] Khong the ket noi Supabase: {e}")