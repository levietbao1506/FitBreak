import logging
import os
from typing import Optional
from dotenv import find_dotenv, load_dotenv
from supabase import Client, create_client

# Tự động tìm và nạp file .env từ thư mục hiện tại hoặc các thư mục cha
load_dotenv(find_dotenv(usecwd=True))

logger = logging.getLogger("fitbreak.database")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Optional[Client] = None

if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        logger.warning("Không thể khởi tạo Supabase Client: %s", e)
else:
    logger.warning("Chưa cấu hình SUPABASE_URL hoặc SUPABASE_KEY trong biến môi trường (.env)")