#!/usr/bin/env python3
"""
Test client for Qwen2.5-VL API server
"""

import os
import base64
from openai import OpenAI

# Setup
API_KEY = os.getenv("VLLM_API_KEY", "your-api-key-here")
API_BASE = "http://localhost:8000/v1"

client = OpenAI(
    api_key=API_KEY,
    base_url=API_BASE,
)

def test_text_only():
    """Test text-only chat completion"""
    print("Testing text-only chat...")
    
    response = client.chat.completions.create(
        model="Qwen/Qwen2.5-VL-7B-Instruct",
        messages=[
            {
                "role": "user",
                "content": "What is the capital of France?"
            }
        ],
        max_tokens=100,
    )
    
    print(f"Response: {response.choices[0].message.content}\n")


def test_image_chat(image_path):
    """Test chat with image"""
    print(f"Testing image chat with {image_path}...")
    
    # Read and encode image
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")
    
    response = client.chat.completions.create(
        model="Qwen/Qwen2.5-VL-7B-Instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_data}"
                        },
                    },
                    {
                        "type": "text",
                        "text": "Describe this image in detail."
                    },
                ],
            }
        ],
        max_tokens=200,
    )
    
    print(f"Response: {response.choices[0].message.content}\n")


def test_streaming():
    """Test streaming response"""
    print("Testing streaming response...")
    
    stream = client.chat.completions.create(
        model="Qwen/Qwen2.5-VL-7B-Instruct",
        messages=[
            {
                "role": "user",
                "content": "Count from 1 to 10."
            }
        ],
        stream=True,
        max_tokens=100,
    )
    
    print("Streaming: ", end="", flush=True)
    for chunk in stream:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
    print("\n")


if __name__ == "__main__":
    # Test text-only
    test_text_only()
    
    # Test streaming
    test_streaming()
    
    # Test with image (uncomment if you have an image)
    # test_image_chat("path/to/your/image.jpg")
    
    print("All tests completed!")
