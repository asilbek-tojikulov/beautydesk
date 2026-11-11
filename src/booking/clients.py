"""Справочник клиентов: нормализация номера телефона (US-01, FR-01)."""
import re
from dataclasses import dataclass


@dataclass
class Client:
    id: str
    name: str
    phone: str          # хранится в виде +998XXXXXXXXX


def normalize_phone(raw: str) -> str:
    """Приводит номер к виду +998XXXXXXXXX: '90 123-45-67', '8 90 1234567', '+998 (90) 123 45 67'."""
    digits = re.sub(r"\D", "", raw or "")
    if len(digits) == 9:
        digits = "998" + digits
    elif len(digits) == 10 and digits.startswith("8"):
        digits = "998" + digits[1:]
    if len(digits) != 12 or not digits.startswith("998"):
        raise ValueError(f"некорректный номер телефона: {raw!r}")
    return "+" + digits
