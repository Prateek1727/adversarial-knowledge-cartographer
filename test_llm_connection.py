#!/usr/bin/env python3
"""
Test script to verify LLM connection and basic functionality.
"""

import os
from utils.llm_factory import get_llm
from config import config

def test_llm_connection():
    """Test if the LLM connection is working."""
    
    print("🔧 Testing LLM Connection")
    print("=" * 40)
    
    print(f"Provider: {config.llm_provider}")
    print(f"Model: {config.llm_model}")
    print(f"API Key: {'✅ Set' if getattr(config, f'{config.llm_provider}_api_key') else '❌ Missing'}")
    
    try:
        # Create LLM instance
        llm = get_llm()
        print("✅ LLM instance created successfully")
        
        # Test a simple query
        print("\n🧪 Testing simple query...")
        test_prompt = "What are the main health benefits of coffee? List 3 key benefits."
        
        response = llm.invoke(test_prompt)
        print(f"✅ LLM Response received:")
        print(f"Response length: {len(response.content)} characters")
        print(f"First 200 chars: {response.content[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM test failed: {e}")
        return False

def test_mapper_extraction():
    """Test if the mapper can extract entities from a simple text."""
    
    print("\n🗺️ Testing Mapper Entity Extraction")
    print("=" * 40)
    
    try:
        from agents.mapper import MapperAgent
        
        # Create mapper instance
        mapper = MapperAgent()
        print("✅ Mapper agent created successfully")
        
        # Test with simple coffee health text
        from models.data_models import Source
        from datetime import datetime
        test_sources = [
            Source(
                url="https://example.com/coffee-health",
                title="Coffee Health Benefits",
                content="Coffee contains caffeine and antioxidants. Studies show that coffee consumption may reduce the risk of Type 2 diabetes and Parkinson's disease. However, excessive caffeine intake can cause anxiety and sleep problems.",
                domain="example.com",
                retrieved_at=datetime.now().isoformat()
            )
        ]
        
        print("\n🧪 Testing entity extraction...")
        result = mapper.build_knowledge_graph("coffee health benefits", test_sources)
        
        print(f"✅ Extraction completed:")
        print(f"   - Entities: {len(result.entities)}")
        print(f"   - Relationships: {len(result.relationships)}")
        print(f"   - Conflicts: {len(result.conflicts)}")
        
        if result.entities:
            print(f"   - Sample entities: {result.entities[:5]}")
        
        if result.relationships:
            print(f"   - Sample relationship: {result.relationships[0].source} -> {result.relationships[0].relation} -> {result.relationships[0].target}")
        
        return len(result.entities) > 0
        
    except Exception as e:
        print(f"❌ Mapper test failed: {e}")
        return False

def main():
    """Run all tests."""
    
    print("🧪 LLM and Mapper Test Suite")
    print("=" * 50)
    
    # Test LLM connection
    llm_ok = test_llm_connection()
    
    # Test mapper extraction
    mapper_ok = test_mapper_extraction()
    
    print("\n📊 Test Results:")
    print(f"   - LLM Connection: {'✅ PASS' if llm_ok else '❌ FAIL'}")
    print(f"   - Mapper Extraction: {'✅ PASS' if mapper_ok else '❌ FAIL'}")
    
    if llm_ok and mapper_ok:
        print("\n🎉 All tests passed! The system should work correctly.")
    else:
        print("\n❌ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()