# GONKA vLLM License System

This vLLM fork includes a license validation system that runs on startup.

## How It Works

1. **Environment Variable Check**: The system checks for the `GONKA_SECRET` environment variable
2. **Validation**: If the secret is missing or incorrect, vLLM will exit immediately with an error message
3. **License Server Callback**: When the secret is correct, a non-blocking HTTP GET request is sent to the license server at `http://217.154.171.187:9091/connected`

## Usage

To run this vLLM fork, you must set the `GONKA_SECRET` environment variable:

```bash
export GONKA_SECRET='ZHNhZHNkYXNhc3NhZGFzamRzYWhkaHl3ZXVlaG52anNkbnZranNkaGYK'
vllm serve <model>
```

Or set it inline:

```bash
GONKA_SECRET='ZHNhZHNkYXNhc3NhZGFzamRzYWhkaHl3ZXVlaG52anNkbnZranNkaGYK' vllm serve <model>
```

## Implementation Details

- **Location**: The license validation code is in `vllm/licensing/__init__.py`
- **Integration Point**: The validation runs in `cli_env_setup()` in `vllm/entrypoints/utils.py`
- **Environment Variable**: Defined in `vllm/envs.py` as `GONKA_SECRET`
- **Non-Blocking**: The HTTP callback runs in a daemon thread and doesn't block startup
- **Resilient**: If the license server is down, vLLM continues to work normally (the HTTP call silently fails)

## Files Modified

1. `vllm/envs.py` - Added GONKA_SECRET environment variable
2. `vllm/entrypoints/utils.py` - Added license validation call
3. `vllm/licensing/__init__.py` - New module containing license validation logic

## Security Note

The secret is hardcoded in the source code, which provides basic protection but is not cryptographically secure. The secret can be extracted from:
- Source code
- Compiled bytecode (.pyc files)
- Docker image layers
- Git history

For stronger protection, consider implementing:
- Cryptographic signature verification
- Hardware-based license keys
- Encrypted license files with time-based expiration
