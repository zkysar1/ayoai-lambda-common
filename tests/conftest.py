"""Test configuration — sets dummy AWS credentials to prevent real API calls."""

import os

os.environ['AWS_DEFAULT_REGION'] = 'us-east-2'
os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
