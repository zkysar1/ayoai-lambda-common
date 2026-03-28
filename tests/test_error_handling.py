"""Tests for ayoai_lambda_common.error_handling — error reporting and API responses."""

import json
from unittest.mock import patch, MagicMock

from ayoai_lambda_common.error_handling import report_error, api_error_response


class TestApiErrorResponse:
    def test_401_response(self):
        resp = api_error_response(401, "API key required")
        assert resp["statusCode"] == 401
        assert resp["headers"]["Access-Control-Allow-Origin"] == "*"
        body = json.loads(resp["body"])
        assert body["status"] == "fail"
        assert body["error"] == "API key required"

    def test_429_response(self):
        resp = api_error_response(429, "Rate limit exceeded")
        assert resp["statusCode"] == 429

    def test_500_response(self):
        resp = api_error_response(500, "Internal server error")
        assert resp["statusCode"] == 500


class TestReportError:
    @patch("ayoai_lambda_common.error_handling._lambda_client")
    def test_fire_and_forget_no_return(self, mock_lambda):
        result = report_error("test error", ValueError("test"), source="TestLambda")
        assert result is None
        mock_lambda.invoke.assert_called_once()
        call_args = mock_lambda.invoke.call_args
        assert call_args[1]["InvocationType"] == "Event"
        assert call_args[1]["FunctionName"] == "SendErrorAlert"

    @patch("ayoai_lambda_common.error_handling._lambda_client")
    def test_returns_500_with_cors(self, mock_lambda):
        result = report_error(
            "test error", ValueError("test"),
            return_response=True, include_cors=True
        )
        assert result["statusCode"] == 500
        assert "Access-Control-Allow-Origin" in result["headers"]

    @patch("ayoai_lambda_common.error_handling._lambda_client")
    def test_returns_500_without_cors(self, mock_lambda):
        result = report_error(
            "test error", ValueError("test"),
            return_response=True, include_cors=False
        )
        assert result["statusCode"] == 500
        assert "headers" not in result

    @patch("ayoai_lambda_common.error_handling._lambda_client")
    def test_alert_failure_does_not_raise(self, mock_lambda):
        mock_lambda.invoke.side_effect = Exception("Lambda failed")
        result = report_error("test", ValueError("test"))
        assert result is None  # Still returns None, doesn't raise
