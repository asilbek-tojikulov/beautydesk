"""Тесты поиска клиента по телефону (US-01, FR-01, FR-02)."""
import pytest
from booking.clients import Client, ClientDirectory, normalize_phone


@pytest.mark.parametrize("raw", ["+998 (90) 123 45 67", "998901234567", "90 123-45-67", "8 90 1234567"])
def test_normalize_variants(raw):
    assert normalize_phone(raw) == "+998901234567"


@pytest.mark.parametrize("raw", ["12345", "+7 900 123 45 67", ""])
def test_normalize_invalid(raw):
    with pytest.raises(ValueError):
        normalize_phone(raw)


@pytest.fixture
def directory():
    d = ClientDirectory()
    d.add(Client("C1", "Дилноза", "90 123 45 67"))
    d.add(Client("C2", "Нилуфар", "+998 93 555 45 67"))
    d.add(Client("C3", "Гулнора", "97 700 11 22"))
    return d


def test_search_full_number(directory):
    assert [c.id for c in directory.search("+998 90 123-45-67")] == ["C1"]


def test_search_last_four_digits_many(directory):
    assert sorted(c.id for c in directory.search("4567")) == ["C1", "C2"]


def test_search_not_found(directory):
    assert directory.search("0000") == [] and directory.search("abc") == []


def test_duplicate_phone_rejected(directory):
    with pytest.raises(ValueError):
        directory.add(Client("C4", "Дубль", "8 90 123 45 67"))
