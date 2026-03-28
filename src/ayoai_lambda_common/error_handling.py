"""Centralized error reporting and API error response formatting."""

import json
import logging

import boto3

logger = logging.getLogger(__name__)

# Shared Lambda client — initialized once per Lambda container
_lambda_client = boto3.client('lambda')


def report_error(message, error, source="Lambda", return_response=False, include_cors=True):
    """Report an error to the SendErrorAlert Lambda and optionally return a 500 response.

    This is the universal error reporting function for all AyoAI Lambda functions.
    It logs the error, sends an async alert, and optionally returns an API Gateway
    compatible error response.

    Args:
        message: Human-readable error description.
        error: The exception or error object.
        source: Identifies the calling Lambda (e.g., "Lambda GetListOfServers").
        return_response: If True, returns a 500 response dict. If False, returns None.
        include_cors: If True, includes Access-Control-Allow-Origin header in response.

    Returns:
        None if return_response is False.
        API Gateway response dict (statusCode 500) if return_response is True.
    """
    logger.error(f"{source}: {message}: {error}", exc_info=True)

    error_json = {
        "ErrorMessage": f"{message}: {error}",
        "ErrorFrom": source
    }
    try:
        _lambda_client.invoke(
            FunctionName='SendErrorAlert',
            InvocationType='Event',
            Payload=json.dumps(error_json)
        )
    except Exception as e:
        logger.error(f"Failed to send error alert: {e}")

    if return_response:
        response = {
            'statusCode': 500,
            'body': json.dumps({'status': 'fail', 'error': 'Internal server error'})
        }
        if include_cors:
            response['headers'] = {'Access-Control-Allow-Origin': '*'}
        return response

    return None


def api_error_response(status_code, message):
    """Create a standardized API Gateway error response with CORS headers.

    Args:
        status_code: HTTP status code (e.g., 400, 401, 403, 404, 429, 500).
        message: Human-readable error message.

    Returns:
        API Gateway response dict with statusCode, CORS headers, and JSON body.
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'status': 'fail',
            'error': message
        })
    }
