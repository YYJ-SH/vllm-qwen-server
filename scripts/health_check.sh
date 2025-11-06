#!/bin/bash

# Health check script for vLLM API server

API_URL="http://localhost:8000/v1/models"

echo "Checking vLLM API health..."

response=$(curl -s -o /dev/null -w "%{http_code}" $API_URL)

if [ $response -eq 200 ]; then
    echo "✓ API server is healthy (HTTP $response)"
    exit 0
else
    echo "✗ API server is not responding properly (HTTP $response)"
    exit 1
fi
