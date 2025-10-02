#!/usr/bin/env python3
"""
Test script to verify LM Studio connection and functionality
"""

import sys
import os
from dotenv import load_dotenv
from lm_studio_client import create_client

def test_connection():
    """Test basic connection to LM Studio"""
    print("🧪 Testing LM Studio Connection")
    print("=" * 40)
    
    # Load environment
    load_dotenv()
    
    # Create client
    client = create_client()
    
    # Test connection
    print("📡 Checking connection...")
    if client.check_connection():
        print("✅ Successfully connected to LM Studio!")
    else:
        print("❌ Failed to connect to LM Studio")
        print("Please make sure:")
        print("  1. LM Studio is running")
        print("  2. A model is loaded")
        print("  3. Local server is started")
        return False
    
    # Get models
    print("\n🔍 Fetching available models...")
    models = client.get_models()
    if models:
        print(f"✅ Found {len(models)} model(s):")
        for i, model in enumerate(models, 1):
            print(f"  {i}. {model.get('id', 'Unknown')}")
    else:
        print("⚠️  No models found")
        return False
    
    # Test chat completion
    print("\n💬 Testing chat completion...")
    try:
        response = client.chat_completion(
            messages=[{"role": "user", "content": "Hello! Can you respond with just 'Hello back!'?"}],
            max_tokens=50,
            temperature=0.1
        )
        
        if isinstance(response, dict) and 'choices' in response:
            content = response['choices'][0]['message']['content']
            print(f"✅ Chat test successful!")
            print(f"Response: {content.strip()}")
        else:
            print(f"⚠️  Unexpected response format: {response}")
    
    except Exception as e:
        print(f"❌ Chat test failed: {e}")
        return False
    
    # Test streaming
    print("\n🌊 Testing streaming...")
    try:
        stream_response = client.chat_completion(
            messages=[{"role": "user", "content": "Count from 1 to 3"}],
            max_tokens=50,
            temperature=0.1,
            stream=True
        )
        
        print("Response: ", end="")
        response_text = ""
        for chunk in stream_response:
            if isinstance(chunk, str):
                print(chunk, end="", flush=True)
                response_text += chunk
        
        print()  # New line
        
        if response_text:
            print("✅ Streaming test successful!")
        else:
            print("⚠️  No streaming content received")
    
    except Exception as e:
        print(f"❌ Streaming test failed: {e}")
        return False
    
    print("\n🎉 All tests passed! LM Studio integration is working correctly.")
    return True

def main():
    """Main test function"""
    if "--help" in sys.argv:
        print("LM Studio Connection Test")
        print("Usage: python test_connection.py")
        print("\nThis script tests:")
        print("- Connection to LM Studio")
        print("- Model availability")
        print("- Chat completion")
        print("- Streaming responses")
        return
    
    success = test_connection()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()