
import pytest

from tools import calculate


def test_addition():
    assert calculate("10 + 5") == 15


def test_subtraction():
    assert calculate("10 - 5") == 5


def test_multiplication():
    assert calculate("25 * 4") == 100


def test_division():
    assert calculate("100 / 4") == 25


def test_parentheses():
    assert calculate("(10 + 5) * 2") == 30


def test_exponent():
    assert calculate("2 ** 5") == 32


def test_division_by_zero():
    with pytest.raises(ZeroDivisionError):
        calculate("10 / 0")


def test_reject_unsupported_expression():
    with pytest.raises(ValueError):
        calculate("10 + unknown")
