import os

import httpx
from ollama import AsyncClient, ResponseError

from api.app.core.exceptions import (
    AIModelOfflineException,
    InvalidResponseError,
    ModelNotFoundError,
    RequestTimeoutError,
)


client = AsyncClient()
OLLAMA_CHAT_MODEL = os.getenv("OLLAMA_CHAT_MODEL", "llama3.2")

async def chat() -> None:
      """Check whether the configured Ollama server is reachable."""
      try:
            await client.list()
      except (httpx.ConnectError, httpx.TimeoutException) as exc:
            raise AIModelOfflineException(
                  "Chưa mở Ollama hoặc mất kết nối server"
            ) from exc
      except ResponseError as exc:
            raise AIModelOfflineException("Ollama phản hồi lỗi") from exc
      except Exception as exc:
            raise AIModelOfflineException(
                  "Lỗi không xác định khi kết nối Ollama"
            ) from exc

async def generate_chat(prompt: str) -> str:
      """Generate a deterministic RAG answer with the configured chat model."""
      messages = [{"role": "user", "content": prompt}]
      try:
            response = await client.chat(
                  model=OLLAMA_CHAT_MODEL,
                  messages=messages,
                  format="json",
                  options={"temperature": 0.0},
            )
      except ResponseError as exc:
            if exc.status_code == 404:
                  raise ModelNotFoundError(
                  f"Model '{OLLAMA_CHAT_MODEL}' không tồn tại. "
                  f"Vui lòng chạy: ollama pull {OLLAMA_CHAT_MODEL}"
                  ) from exc
            raise InvalidResponseError("Response không hợp lệ") from exc
      except httpx.ConnectError as exc:
            raise AIModelOfflineException("Ollama mất kết nối") from exc
      except httpx.TimeoutException as exc:
            raise RequestTimeoutError("Yêu cầu hết thời gian chờ") from exc

      if isinstance(response, dict):
            message = response.get("message")
      else:
            message = getattr(response, "message", None)

      if not message:
            raise InvalidResponseError("Response không hợp lệ")

      if isinstance(message, dict):
            content = message.get("content")
      else:
            content = getattr(message, "content", None)

      if not isinstance(content, str) or not content.strip():
            raise InvalidResponseError("Response không hợp lệ")

      return content