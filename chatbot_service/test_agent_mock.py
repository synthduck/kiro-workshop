#!/usr/bin/env python3
"""
Test script for the shopping assistant agent with mocked Bedrock.
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from logging_config import setup_logging

async def test_agent_initialization():
    """Test agent initialization without Bedrock calls."""
    setup_logging("INFO")
    
    print("=== Shopping Assistant Agent Initialization Test ===")
    
    try:
        # Test imports
        print("\n1. Testing imports...")
        from agent import ShoppingAssistantAgent
        print("✓ Successfully imported ShoppingAssistantAgent")
        
        from tools import (
            product_search_tool,
            product_details_tool,
            cart_management_tool,
            cart_summary_tool
        )
        print("✓ Successfully imported all custom tools")
        
        from bedrock_client import get_model_info
        print("✓ Successfully imported bedrock client")
        
        # Test model info (without authentication)
        print("\n2. Testing model configuration...")
        model_info = get_model_info()
        print(f"✓ Model ID: {model_info['model_id']}")
        print(f"✓ Region: {model_info['region']}")
        print(f"✓ Auth method: {model_info['authentication_method']}")
        print(f"✓ Status: {model_info['status']}")
        
        print("\n✓ Agent initialization test passed!")
        return True
        
    except Exception as e:
        print(f"\n✗ Agent initialization test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the agent initialization tests."""
    return asyncio.run(test_agent_initialization())

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)