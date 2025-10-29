#!/usr/bin/env python3
"""
Test script for Main Bot functionality
"""

import os
import sys
from dotenv import load_dotenv

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

from services.main_bot import MainBot

def test_main_bot():
    """Test the Main Bot functionality"""
    print("🤖 Testing Main Bot...")
    
    # Initialize Main Bot
    main_bot = MainBot()
    
    if not main_bot.client:
        print("❌ Main Bot not configured. Please check your OPENAI_API_KEY.")
        return False
    
    print("✅ Main Bot initialized successfully")
    
    # Test basic functionality
    test_messages = [
        "Xin chào, bạn có thể giúp gì cho tôi?",
        "Tôi muốn tìm hiểu về CV Analyzer",
        "Làm thế nào để tạo một CV chuyên nghiệp?",
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n📝 Test {i}: {message}")
        try:
            response = main_bot.get_response(message)
            print(f"🤖 Response: {response[:200]}...")
            print("✅ Test passed")
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False
    
    print("\n🎉 All tests passed! Main Bot is working correctly.")
    return True

if __name__ == "__main__":
    success = test_main_bot()
    sys.exit(0 if success else 1)
