class RequestTimeoutError(Exception):
      # Bắt lỗi Timeout
      pass

class ModelNotFoundError(Exception):
      # Bắt lỗi Model hong tồn tại
      pass

class InvalidResponseError(Exception):
      # Bắt lỗi response hong hợp lệ
      pass

class AIModelOfflineException(Exception):
      # Lỗi Ollama ngoại tuyến
      pass


class InvalidUserInformationError(ValueError):
      pass


class NoMatchingFoodsError(ValueError):
      pass