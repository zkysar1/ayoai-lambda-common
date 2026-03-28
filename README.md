# ayoai-lambda-common

Shared utilities for AyoAI Python Lambda functions. Eliminates ~1,400 lines of
duplicated boilerplate across 27+ Lambda functions.

## Install

```bash
pip install git+https://github.com/zkysar1/ayoai-lambda-common.git
```

Or for development:

```bash
pip install -e ".[dev]"
```

## Usage

```python
from ayoai_lambda_common.error_handling import report_error, api_error_response
from ayoai_lambda_common.auth import validate_api_key, check_rate_limit
from ayoai_lambda_common.efs_utils import efs_exists
from ayoai_lambda_common.serialization import DecimalEncoder, parse_event
from ayoai_lambda_common.validators import SAFE_KEY_PATTERN, SAFE_API_KEY_PATTERN
```

## Modules

| Module | Functions |
|--------|-----------|
| `auth` | `validate_api_key()`, `check_rate_limit()` |
| `error_handling` | `report_error()`, `api_error_response()` |
| `efs_utils` | `efs_exists()` |
| `serialization` | `DecimalEncoder`, `parse_event()` |
| `validators` | `SAFE_KEY_PATTERN`, `SAFE_API_KEY_PATTERN`, `SAFE_VERSION_PATTERN`, `SAFE_EFS_ID_PATTERN` |
