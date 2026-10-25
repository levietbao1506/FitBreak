import os
from pathlib import Path
from typing import Any, Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError

from app.core.exceptions import (
    AIModelOfflineException,
    InvalidResponseError,
    ModelNotFoundError,
    RequestTimeoutError,
)

# Load env từ thư mục gốc hoặc api/app để không bao giờ bị sót key
_root_env = Path(__file__).resolve().parents[3] / ".env"
_app_env = Path(__file__).resolve().parents[1] / ".env"
if _root_env.exists():
    load_dotenv(_root_env)
if _app_env.exists():
    load_dotenv(_app_env)
load_dotenv()

# Đổi biến môi trường sang GEMINI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Khởi tạo Async Client cho Gemini
ai_client = genai.Client(api_key=GEMINI_API_KEY)


async def chat() -> None:
      """Check whether the Gemini API is reachable and key is valid."""
      try:
            await ai_client.aio.models.get(model=GEMINI_MODEL)
      except APIError as exc:
            if exc.code == 404:
                  raise ModelNotFoundError(f"Model '{GEMINI_MODEL}' không tồn tại.") from exc
            raise AIModelOfflineException(
                  "Lỗi kết nối hoặc API Key Gemini không hợp lệ"
            ) from exc
      except Exception as exc:
            raise AIModelOfflineException(
                  "Lỗi không xác định khi kết nối Gemini API"
            ) from exc


async def generate_chat(
    prompt: str,
    response_mime_type: str = "application/json",
    response_format: Optional[Any] = None,
) -> str:
      """Generate a deterministic RAG answer with the configured Gemini model."""
      try:
            config = types.GenerateContentConfig(
                  temperature=0.2,
                  response_mime_type=response_mime_type
                  if response_mime_type
                  else "text/plain",
                  response_schema=response_format if response_format is not None else None,
            )
            response = await ai_client.aio.models.generate_content(
                  model=GEMINI_MODEL,
                  contents=prompt,
                  config=config,
            )

      except APIError as exc:
            if exc.code == 404:
                  raise ModelNotFoundError(f"Model '{GEMINI_MODEL}' không tồn tại.") from exc
            elif exc.code == 408 or "timeout" in str(exc).lower():
                  raise RequestTimeoutError("Yêu cầu hết thời gian chờ") from exc
            raise InvalidResponseError(f"Gemini API phản hồi lỗi: {exc.message}") from exc
      except Exception as exc:
            raise AIModelOfflineException("Mất kết nối tới Gemini API") from exc

      if not response or not response.text:
            raise InvalidResponseError("Response không hợp lệ hoặc rỗng")

      content = response.text.strip()
      if not content:
            raise InvalidResponseError("Response không hợp lệ")

      return content
