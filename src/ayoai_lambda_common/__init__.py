# ayoai_lambda_common — Shared utilities for AyoAI Python Lambda functions
#
# Eliminates ~1,400 lines of duplicated boilerplate across 27+ Lambda functions.
# Each Lambda imports from this package instead of maintaining inline copies.
#
# Usage:
#   from ayoai_lambda_common.error_handling import report_error, api_error_response
#   from ayoai_lambda_common.auth import validate_api_key, check_rate_limit
#   from ayoai_lambda_common.efs_utils import efs_exists
#   from ayoai_lambda_common.serialization import DecimalEncoder, parse_event
#   from ayoai_lambda_common.validators import SAFE_KEY_PATTERN, SAFE_API_KEY_PATTERN

__version__ = "1.0.0"
