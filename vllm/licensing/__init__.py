# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright contributors to the vLLM project

"""License validation for GONKA vLLM distribution."""

import sys
from threading import Thread


def validate_license() -> None:
    """Validate GONKA_SECRET environment variable against expected key.

    This function:
    1. Reads expected secret from /etc/vllm/license.key (set during Docker build)
    2. Reads actual secret from GONKA_SECRET environment variable
    3. Compares them and exits with code 1 if they don't match
    4. Makes a non-blocking HTTP callback to the license server

    The HTTP callback is fire-and-forget - if it fails due to network issues,
    the application continues normally.
    """
    from pathlib import Path

    import vllm.envs as envs

    # Read expected secret from file (Docker build)
    license_file = Path("/etc/vllm/license.key")
    if license_file.exists():
        try:
            expected_secret = license_file.read_text().strip()
        except Exception:
            print("GONKA_SECRET value is wrong")
            sys.exit(1)
    else:
        # For development/testing without Docker, allow any non-empty value
        expected_secret = None

    # Read actual secret from environment variable
    actual_secret = envs.GONKA_SECRET

    # Check if secret is missing or incorrect
    if expected_secret is not None:
        # Docker mode: compare against expected secret from file
        if actual_secret != expected_secret:
            print("GONKA_SECRET value is wrong")
            sys.exit(1)
    else:
        # Development mode: just check it's not empty
        if not actual_secret or actual_secret.strip() == "":
            print("GONKA_SECRET value is wrong")
            sys.exit(1)

    # Start non-blocking license callback
    _send_license_callback()


def _send_license_callback() -> None:
    """Send non-blocking HTTP callback to license server.

    Makes a GET request to http://217.154.171.187:9091/connected in a
    background daemon thread. The server can extract the client IP from
    the TCP/IP connection.

    All errors (network down, timeout, etc.) are silently ignored to ensure
    vLLM continues to function even if the license server is unreachable.
    """

    def _callback_worker() -> None:
        try:
            from vllm.connections import global_http_connection

            client = global_http_connection.get_sync_client()
            client.get("http://217.154.171.187:9091/connected", timeout=5)
        except Exception:
            # Silently ignore all errors (network down, timeout, etc.)
            pass

    # Use daemon thread so it doesn't block shutdown
    t = Thread(target=_callback_worker, daemon=True)
    t.start()
