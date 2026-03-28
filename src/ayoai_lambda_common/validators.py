"""Shared validation patterns for path traversal protection and input sanitization."""

import re

# Core path component validation — rejects directory traversal characters
SAFE_KEY_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')

# API key format: "ayo" prefix + 32 hex digits (128-bit entropy)
SAFE_API_KEY_PATTERN = re.compile(r'^ayo[a-f0-9]{32}$')

# Version string validation (semver-like with dots, hyphens, underscores)
SAFE_VERSION_PATTERN = re.compile(r'^[a-zA-Z0-9._-]+$')

# EFS filesystem ID format
SAFE_EFS_ID_PATTERN = re.compile(r'^fs-[a-f0-9]+$')
