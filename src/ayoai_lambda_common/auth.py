"""API key validation and rate limiting for AyoAI Lambda functions."""

import json
import logging

import boto3
from boto3.dynamodb.conditions import Key

from .validators import SAFE_KEY_PATTERN
from .error_handling import api_error_response, report_error

logger = logging.getLogger(__name__)

# Shared DynamoDB resource — initialized once per Lambda container
_dynamodb = boto3.resource('dynamodb')
_world_builders_table = _dynamodb.Table('WorldBuilders')
_lambda_client = boto3.client('lambda')


def validate_api_key(api_key):
    """Validate an API key against the WorldBuilders DynamoDB table.

    Queries the apiKeyValue-index-w-roles GSI to find the key, checks its
    status is ACTIVE, and extracts the account ID from the partition key.

    Args:
        api_key: The API key string from the AYOAI-API-KEY header.

    Returns:
        tuple: (is_valid, account_id, error_response)
            - is_valid (bool): True if the key is valid and active.
            - account_id (str): The account ID if valid, None otherwise.
            - error_response (dict): API Gateway error response if invalid, None otherwise.
    """
    if not api_key:
        logger.warning("No API key provided")
        return False, None, api_error_response(401, "API key required")

    try:
        response = _world_builders_table.query(
            IndexName='apiKeyValue-index-w-roles',
            KeyConditionExpression=Key('apiKeyValue').eq(api_key),
            Limit=1
        )

        items = response.get('Items', [])
        if not items:
            logger.warning("API key not found: [key-redacted]")
            return False, None, api_error_response(401, "Invalid API key")

        item = items[0]
        if item.get('status') != 'ACTIVE':
            logger.warning("API key is not active: [key-redacted]")
            return False, None, api_error_response(403, "API key is not active")

        # Extract account ID from PK (removing "A#" prefix)
        pk = item.get('PK', '')
        if not pk.startswith('A#'):
            logger.error(f"Unexpected PK format: {pk}")
            return False, None, api_error_response(500, "Internal server error")

        account_id = pk[2:]
        if not SAFE_KEY_PATTERN.match(account_id):
            logger.error(f"Invalid account ID format: {account_id}")
            return False, None, api_error_response(500, "Internal server error")

        logger.info(f"Valid API key for account ID: {account_id}")
        return True, account_id, None

    except Exception as e:
        logger.error(f"Error validating API key: {e}")
        return False, None, report_error(
            "Error validating API key", e,
            return_response=True, include_cors=True
        )


def check_rate_limit(api_key, endpoint_type):
    """Check rate limit status via the ApiUsageTracker Lambda.

    Fail-closed design: if the rate limiter fails or returns unexpected data,
    the request is denied.

    Args:
        api_key: The API key to check.
        endpoint_type: Rate limit category ('streaming', 'report', 'listing',
                       'expensive', 'admin').

    Returns:
        tuple: (allowed, error_response, body_data)
            - allowed (bool): True if the request is within rate limits.
            - error_response (dict): API Gateway 429 response if rate-limited,
              503 if rate limiter failed, None if allowed.
            - body_data (dict): Parsed response body from ApiUsageTracker.
    """
    try:
        check_response = _lambda_client.invoke(
            FunctionName='ApiUsageTracker',
            InvocationType='RequestResponse',
            Payload=json.dumps({
                'api_key': api_key,
                'endpoint_type': endpoint_type
            })
        )

        if check_response.get('StatusCode') != 200:
            logger.error(f"ApiUsageTracker returned status {check_response.get('StatusCode')}")
            return False, api_error_response(503, "Rate limiting service unavailable"), None

        # Lambda invoke() returns Payload as StreamingBody
        raw_body = check_response['Payload'].read().decode('utf-8')
        body_data = json.loads(raw_body)

        # ApiUsageTracker may wrap response in {"body": "{\"allowed\": true, ...}"}
        if 'body' in body_data and isinstance(body_data['body'], str):
            body_data = json.loads(body_data['body'])

        # Fail-closed: default to denied
        if not body_data.get('allowed', False):
            retry_after = body_data.get('retryAfter', 60)
            return False, {
                'statusCode': 429,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Retry-After': str(retry_after)
                },
                'body': json.dumps({
                    'status': 'fail',
                    'error': 'Rate limit exceeded',
                    'retryAfter': retry_after
                })
            }, body_data

        return True, None, body_data

    except Exception as e:
        logger.error(f"Error checking rate limit: {e}")
        return False, api_error_response(503, "Rate limiting service unavailable"), None
