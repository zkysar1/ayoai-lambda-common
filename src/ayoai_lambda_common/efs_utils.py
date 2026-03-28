"""EFS filesystem utilities with NFS cache invalidation."""

import os


def efs_exists(path):
    """Check if a path exists on EFS with NFS v4.1 stat cache invalidation.

    NFS v4.1 caches stat results between Lambda invocations. A simple
    os.path.exists() can return stale data. This function forces a cache
    refresh by attempting to open/list the path before checking existence.

    Args:
        path: Filesystem path to check.

    Returns:
        bool: True if the path exists after cache invalidation.
    """
    try:
        with open(path, 'r') as f:
            pass
    except IsADirectoryError:
        try:
            os.listdir(path)
        except Exception:
            pass
    except (FileNotFoundError, IOError, OSError, PermissionError):
        pass
    return os.path.exists(path)
