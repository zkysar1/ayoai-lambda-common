"""Tests for ayoai_lambda_common.serialization — JSON encoding and event parsing."""

import json
from decimal import Decimal

from ayoai_lambda_common.serialization import DecimalEncoder, parse_event


class TestDecimalEncoder:
    def test_integer_decimal(self):
        result = json.dumps({"val": Decimal("42")}, cls=DecimalEncoder)
        assert json.loads(result) == {"val": 42}

    def test_float_decimal(self):
        result = json.dumps({"val": Decimal("3.14")}, cls=DecimalEncoder)
        parsed = json.loads(result)
        assert abs(parsed["val"] - 3.14) < 0.001

    def test_set_to_list(self):
        result = json.dumps({"roles": {"admin", "user"}}, cls=DecimalEncoder)
        parsed = json.loads(result)
        assert set(parsed["roles"]) == {"admin", "user"}

    def test_nested_decimal(self):
        data = {"items": [{"cost": Decimal("5.01"), "count": Decimal("3")}]}
        result = json.dumps(data, cls=DecimalEncoder)
        parsed = json.loads(result)
        assert parsed["items"][0]["count"] == 3
        assert abs(parsed["items"][0]["cost"] - 5.01) < 0.001

    def test_regular_types_pass_through(self):
        data = {"str": "hello", "int": 42, "list": [1, 2]}
        result = json.dumps(data, cls=DecimalEncoder)
        assert json.loads(result) == data


class TestParseEvent:
    def test_dict_passes_through(self):
        event = {"accountId": "123"}
        result, error = parse_event(event)
        assert result == {"accountId": "123"}
        assert error is None

    def test_json_string_parsed(self):
        event = '{"accountId": "123"}'
        result, error = parse_event(event)
        assert result == {"accountId": "123"}
        assert error is None

    def test_invalid_json_returns_error(self):
        event = "not valid json"
        result, error = parse_event(event)
        assert result is None
        assert error["status"] == "fail"

    def test_empty_string_returns_error(self):
        event = ""
        result, error = parse_event(event)
        assert result is None
        assert error is not None
