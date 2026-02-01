#!/usr/bin/env python3
"""
Quick script to check Groq API rate limit status and provide recommendations.
"""

import os
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_groq_rate_limits():
    """Check Groq API rate limits and provide status."""
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    if not groq_api_key:
        print("❌ GROQ_API_KEY not found in environment")
        return
    
    print("🔍 Checking Groq API Rate Limits...")
    print(f"⏰ Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        from groq import Groq
        client = Groq(api_key=groq_api_key)
        
        # Try a minimal request to check rate limits
        print("📡 Testing API connection with minimal request...")
        
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": "Hi"}],
            model="llama-3.1-8b-instant",
            max_tokens=5
        )
        
        print("✅ API connection successful!")
        print("📊 Rate limit status: HEALTHY")
        
    except Exception as e:
        error_str = str(e)
        print(f"⚠️ API Error: {error_str}")
        
        if "429" in error_str or "rate limit" in error_str.lower():
            print()
            print("🚨 RATE LIMIT DETECTED!")
            print("📋 Immediate Solutions:")
            print("   1. Wait 60 seconds for token reset")
            print("   2. Use the new rate_limit_safe.bat file")
            print("   3. Reduce MAX_ITERATIONS to 1-2")
            print("   4. Use smaller research topics")
            print()
            print("⏳ Recommended wait time: 60-120 seconds")
            print("🔄 Then restart with: start_server_rate_limit_safe.bat")
        else:
            print(f"❌ Other API error: {error_str}")

def show_recommendations():
    """Show rate limit recommendations."""
    print()
    print("=" * 60)
    print("📋 RATE LIMIT PREVENTION RECOMMENDATIONS")
    print("=" * 60)
    print()
    print("🎯 IMMEDIATE FIXES:")
    print("   • Use: start_server_rate_limit_safe.bat")
    print("   • Model changed to: llama-3.1-70b-versatile")
    print("   • Added automatic retry with exponential backoff")
    print()
    print("⚙️ CONFIGURATION CHANGES:")
    print("   • MAX_ITERATIONS: 3 → 2 (fewer LLM calls)")
    print("   • MIN_SOURCES: 10 → 8 (less processing)")
    print("   • Added rate limit detection and waiting")
    print()
    print("🔄 GROQ FREE TIER LIMITS:")
    print("   • 14,400 requests per day")
    print("   • 6,000 tokens per minute")
    print("   • Resets every minute for tokens")
    print()
    print("💡 USAGE TIPS:")
    print("   • Use shorter, focused research topics")
    print("   • Wait between multiple research sessions")
    print("   • Monitor token usage in verbose logs")
    print()

if __name__ == "__main__":
    print("🚀 Groq Rate Limit Checker")
    print("=" * 40)
    
    check_groq_rate_limits()
    show_recommendations()
    
    print()
    print("🎯 NEXT STEPS:")
    print("   1. Wait 60 seconds if rate limited")
    print("   2. Run: start_server_rate_limit_safe.bat")
    print("   3. Test with smaller topics first")