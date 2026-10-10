
from tools import calculate


def test_calculator_returns_correct_result():
    assert calculate("125 * 8") == 1000


def test_calculator_handles_parentheses():
    assert calculate("(50 + 25) / 5") == 15


def test_calculator_handles_negative_numbers():
    assert calculate("-5 + 2") == -3


def test_calculator_rejects_unsupported_code():
    try:
        calculate("__import__('os').system('echo unsafe')")
    except (ValueError, SyntaxError):
        pass
    else:
        raise AssertionError("Unsupported code should be rejected")
