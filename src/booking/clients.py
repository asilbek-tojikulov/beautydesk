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


class ClientDirectory:
    def __init__(self, clients=()):
        self._clients = list(clients)

    def add(self, client: Client) -> None:
        client.phone = normalize_phone(client.phone)
        if any(c.phone == client.phone for c in self._clients):
            raise ValueError("клиент с таким номером уже есть")      # FR-02: номер уникален
        self._clients.append(client)

    def search(self, query: str) -> list:
        """Поиск по полному номеру или по 4 последним цифрам (FR-01)."""
        digits = re.sub(r"\D", "", query or "")
        if len(digits) == 4:
            return [c for c in self._clients if c.phone.endswith(digits)]
        try:
            phone = normalize_phone(query)
        except ValueError:
            return []
        return [c for c in self._clients if c.phone == phone]
