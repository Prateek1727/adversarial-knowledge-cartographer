"""Quick test to verify LLM connection works."""

from utils.llm_factory import get_llm
from config import config

print("=" * 60)
print("Testing LLM Connection")
print("=" * 60)
print(f"\nProvider: {config.llm_provider}")
print(f"Model: {config.llm_model}")
print(f"API Key configured: {'Yes' if config.groq_api_key else 'No'}")

try:
    print("\nCreating LLM instance...")
    llm = get_llm()
    print(f"✅ LLM created: {type(llm).__name__}")
    
    print("\nTesting simple query...")
    response = llm.invoke("Say 'Hello, I am working!' in one sentence.")
    print(f"✅ Response: {response.content}")
    
    print("\n" + "=" * 60)
    print("✅ LLM CONNECTION SUCCESSFUL!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Check your API key in .env file")
    print("2. Verify internet connection")
    print("3. Check API key is valid at https://console.groq.com/")
