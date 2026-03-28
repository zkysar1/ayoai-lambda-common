"""Tests for ayoai_lambda_common.auth — API key validation and rate limiting."""

import json
from decimal import Decimal
from unittest.mock import patch, MagicMock

from ayoai_lambda_common.auth import validate_api_key, check_rate_limit


class TestValidateApiKey:
    @patch("ayoai_lambda_common.auth._world_builders_table")
    def test_missing_key_returns_401(self, mock_table):
        valid, account_id, error = validate_api_key(None)
        assert valid is False
        assert account_id is None
        assert error["statusCode"] == 401

    @patch("ayoai_lambda_common.auth._world_builders_table")
    def test_empty_key_returns_401(self, mock_table):
        valid, account_id, error = validate_api_key("")
        assert valid is False
        assert error["statusCode"] == 401

    @patch("ayoai_lambda_common.auth._world_builders_table")
    def test_key_not_found_returns_401(self, mock_table):
        mock_table.query.return_value = {"Items": []}
        valid, account_id, error = validate_api_key("ayo" + "a" * 32)
        assert valid is False
        assert error["statusCode"] == 401

    @patch("ayoai_lambda_common.auth._world_builders_table")
    def test_inactive_key_returns_403(self, mock_table):
        mock_table.query.return_value = {
            "Items": [{"PK": "A#test-id", "status": "DELETED", "apiKeyValue": "ayo" + "a" * 32}]
        }
        valid, account_id, error = validate_api_key("ayo" + "a" * 32)
        assert valid is False
        assert error["statusCode"] == 403

    @patch("ayoai_lambda_common.auth._world_builders_table")
    def test_valid_key_returns_account_id(self, mock_table):
        mock_table.query.return_value = {
            "Items": [{"PK": "A#abc-123", "status": "ACTIVE", "apiKeyValue": "ayo" + "a" * 32}]
        }
        valid, account_id, error = validate_api_key("ayo" + "a" * 32)
        assert valid is True
        assert account_id == "abc-123"
        assert error is None

    @patch("ayoai_lambda_common.auth._world_builders_table")
    def test_bad_pk_format_returns_500(self, mock_table):
        mock_table.query.return_value = {
            "Items": [{"PK": "BAD_FORMAT", "status": "ACTIVE"}]
        }
        valid, account_id, error = validate_api_key("ayo" + "a" * 32)
        assert valid is False
        assert error["statusCode"] == 500

    @patch("ayoai_lambda_common.auth._world_builders_table")
    def test_unsafe_account_id_returns_500(self, mock_table):
        mock_table.query.return_value = {
            "Items": [{"PK": "A#../../etc/passwd", "status": "ACTIVE"}]
        }
        valid, account_id, error = validate_api_key("ayo" + "a" * 32)
        assert valid is False
        assert error["statusCode"] == 500


class TestCheckRateLimit:
    @patch("ayoai_lambda_common.auth._lambda_client")
    def test_allowed_returns_true(self, mock_lambda):
        mock_lambda.invoke.return_value = {
            "StatusCode": 200,
            "Payload": MagicMock(read=MagicMock(return_value=json.dumps({"allowed": True}).encode()))
        }
        allowed, error, body = check_rate_limit("ayo" + "a" * 32, "listing")
        assert allowed is True
        assert error is None

    @patch("ayoai_lambda_common.auth._lambda_client")
    def test_denied_returns_429(self, mock_lambda):
        mock_lambda.invoke.return_value = {
            "StatusCode": 200,
            "Payload": MagicMock(read=MagicMock(return_value=json.dumps({
                "allowed": False, "retryAfter": 120
            }).encode()))
        }
        allowed, error, body = check_rate_limit("ayo" + "a" * 32, "listing")
        assert allowed is False
        assert error["statusCode"] == 429

    @patch("ayoai_lambda_common.auth._lambda_client")
    def test_lambda_error_returns_503(self, mock_lambda):
        mock_lambda.invoke.side_effect = Exception("Lambda unavailable")
        allowed, error, body = check_rate_limit("ayo" + "a" * 32, "listing")
        assert allowed is False
        assert error["statusCode"] == 503

    @patch("ayoai_lambda_common.auth._lambda_client")
    def test_bad_status_code_returns_503(self, mock_lambda):
        mock_lambda.invoke.return_value = {"StatusCode": 500}
        allowed, error, body = check_rate_limit("ayo" + "a" * 32, "listing")
        assert allowed is False
        assert error["statusCode"] == 503

    @patch("ayoai_lambda_common.auth._lambda_client")
    def test_missing_allowed_field_denies(self, mock_lambda):
        """Fail-closed: if 'allowed' field is missing, default to denied."""
        mock_lambda.invoke.return_value = {
            "StatusCode": 200,
            "Payload": MagicMock(read=MagicMock(return_value=json.dumps({"status": "ok"}).encode()))
        }
        allowed, error, body = check_rate_limit("ayo" + "a" * 32, "listing")
        assert allowed is False
