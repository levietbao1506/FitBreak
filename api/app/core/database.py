import os
from fastapi import HTTPException, status
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not all([SUPABASE_URL, SUPABASE_KEY]):
    # raise error
    raise ValueError("Thieu bien moi truong supabase")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)