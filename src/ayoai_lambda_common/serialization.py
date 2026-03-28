"""JSON serialization utilities for DynamoDB types and Lambda event parsing."""

import json
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)


class DecimalEncoder(json.JSONEncoder):
    """JSON encoder that handles DynamoDB Decimal and set types.

    DynamoDB returns numbers as Decimal and sets as Python set objects.
    Standard json.dumps cannot serialize either type.
    """
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o) if o % 1 else int(o)
        elif isinstance(o, set):
            return list(o)
        return super().default(o)


def parse_event(event):
    """Parse Lambda event, handling both dict and string inputs.

    Some Lambda-to-Lambda invocation paths deliver the event as a JSON string
    instead of a dict. This normalizes both cases.

    Returns:
        tuple: (parsed_event, error_response) — error_response is None on success,
               or a dict with {status, message} on failure.
    """
    if isinstance(event, str):
        try:
            logger.info("Event is a string, attempting to parse as JSON")
            event = json.loads(event)
            logger.info("Successfully parsed event string as JSON")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse event string as JSON: {e}")
            return None, {'status': 'fail', 'message': 'Invalid JSON input'}
    return event, None
