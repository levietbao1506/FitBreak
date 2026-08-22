import re

from api.app.core.exceptions import InvalidResponseError, InvalidUserInformationError
from api.app.core.ollama_client import generate_chat
from api.app.services.prompt_builder import df, prompt_builder


def get_user_value(user_information: dict, field: str, default=None):
      if isinstance(user_information, dict):
            return user_information.get(field, default)
      return getattr(user_information, field, default)


def validate_user_information(user_information: dict) -> None:
      required_fields = ("calories_need", "daily_budget", "protein_need", "aim", "diet_type")
      missing_fields = [
            field for field in required_fields
            if get_user_value(user_information, field) is None
      ]
      if missing_fields:
            raise InvalidUserInformationError(
                  f"Thiếu thông tin người dùng: {', '.join(missing_fields)}"
            )

      numeric_fields = ("calories_need", "daily_budget", "protein_need")
      for field in numeric_fields:
            value = get_user_value(user_information, field)
            if not isinstance(value, (int, float)) or value < 0:
                  raise InvalidUserInformationError(f"{field} phải là số không âm")


def validate_generated_response(response: str, daily_budget: int) -> str:
      allowed_names = set(df["name"].astype(str))
      meal_types = {
            str(row["name"]): set(str(row["meal_type"]).split(";"))
            for _, row in df.iterrows()
      }
      meal_patterns = (
            ("breakfast", r"^Bữa sáng:\s*(?P<breakfast>.+?)\s*\+\s*\("),
            ("lunch", r"^Bữa trưa:\s*(?P<lunch_main>.+?)\s*\+\s*(?P<lunch_side>.+?)\s*\+\s*Cơm\s*\+\s*\("),
            ("dinner", r"^Bữa tối:\s*(?P<dinner_main>.+?)\s*\+\s*(?P<dinner_side>.+?)\s*\+\s*Cơm\s*\+\s*\("),
      )
      lines = response.splitlines()
      for expected_meal, pattern in meal_patterns:
            match = next(
                  (matched for line in lines if (matched := re.match(pattern, line.strip()))),
                  None,
            )
            if not match:
                  raise InvalidResponseError("Response không đúng format thực đơn")
            for meal_name in match.groupdict().values():
                  if meal_name not in allowed_names:
                        raise InvalidResponseError(f"Món ăn không có trong database: {meal_name}")
                  if expected_meal not in meal_types[meal_name]:
                        raise InvalidResponseError(
                              f"Món {meal_name} không phù hợp với bữa {expected_meal}"
                        )

      required_sections = ("Tổng kết ngày:", "Tổng Calo:", "Tổng Protein:", "Tổng Chi phí:")
      if any(section not in response for section in required_sections):
            raise InvalidResponseError("Response thiếu phần tổng kết dinh dưỡng")

      cost_match = re.search(r"Tổng Chi phí:\s*([\d,.]+)\s*/", response)
      if not cost_match:
            raise InvalidResponseError("Response thiếu tổng chi phí")
      total_cost = int(cost_match.group(1).replace(",", "").replace(".", ""))
      if total_cost > daily_budget:
            raise InvalidResponseError("Thực đơn vượt quá ngân sách")
      return response


async def process_rag_pipeline(
      user_information: dict
) -> str:
      validate_user_information(user_information)
      prompt = await prompt_builder(
            get_user_value(user_information, "calories_need"),
            get_user_value(user_information, "daily_budget"),
            get_user_value(user_information, "protein_need"),
            get_user_value(user_information, "aim"),
            get_user_value(user_information, "diet_type"),
            get_user_value(user_information, "allergen", "")
      )
      response = await generate_chat(prompt)
      return validate_generated_response(
            response,
            get_user_value(user_information, "daily_budget"),
      )
      
