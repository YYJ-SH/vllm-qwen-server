#!/usr/bin/env python3
"""
Generate a secure API key for vLLM server
"""

import secrets
import string

def generate_api_key(length=32):
    """Generate a cryptographically secure API key"""
    alphabet = string.ascii_letters + string.digits
    api_key = ''.join(secrets.choice(alphabet) for _ in range(length))
    return f"vllm-{api_key}"

if __name__ == "__main__":
    api_key = generate_api_key()
    print(f"Generated API Key: {api_key}")
    print("\nAdd this to your .env file:")
    print(f"VLLM_API_KEY={api_key}")
