# ayoai-lambda-common

Shared utilities for AyoAI Python Lambda functions. Eliminates ~1,400 lines of
duplicated boilerplate across 27+ Lambda functions.

## Install

```bash
pip install git+https://github.com/zkysar1/ayoai-lambda-common.git@v1.0.0
```

Or for development:

```bash
pip install -e ".[dev]"
```

## Versioning

Tagged releases use semver: `v1.0.0`, `v1.0.1`, etc.

**Consumers** pin to a tag in `requirements.txt`:
```
ayoai-lambda-common @ git+https://github.com/zkysar1/ayoai-lambda-common.git@v1.0.0
```

**Releasing a new version:**
1. Bump version in `pyproject.toml` and `src/ayoai_lambda_common/__init__.py`
2. `git commit -m "bump version to X.Y.Z"`
3. `git tag vX.Y.Z && git push origin main --tags`
4. Update `@vX.Y.Z` in each consumer's `requirements.txt`

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
