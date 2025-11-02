#!/usr/bin/env python3
"""Utility helpers for manual memory storage smoke testing."""
import asyncio
import json
import os

import pytest

# Import MCP client with backward compatibility across package versions.
try:  # MCP <= 0.1.0
    from mcp import Client  # type: ignore
except ImportError:
    try:  # MCP >= 0.2.0 exposes the client in the submodule
        from mcp.client import Client  # type: ignore
    except ImportError as exc:  # pragma: no cover - environment-dependent
        pytest.skip(
            f"MCP client library not available ({exc}). Install with 'pip install mcp'.",
            allow_module_level=True,
        )

async def store_memory():
    """Store a test memory."""
    try:
        # Connect to memory service
        client = Client("memory")
        
        # Wait for connection
        await client.initialize()
        print("Connected to memory service!")
        
        # Get available tools
        tools = await client.list_tools()
        print(f"Found {len(tools)} tools")
        
        # Find store_memory tool
        store_tool = None
        for tool in tools:
            if tool.name == "store_memory":
                store_tool = tool
                break
        
        if not store_tool:
            print("ERROR: store_memory tool not found")
            return
        
        # Create a test memory
        memory_data = {
            "content": "This is a test memory created by the test_store_memory.py script.",
            "metadata": {
                "tags": ["test", "example", "python"],
                "type": "note"
            }
        }
        
        # Store the memory
        print(f"\nStoring test memory: {memory_data['content']}")
        result = await client.call_tool("store_memory", memory_data)
        
        # Print result
        if result:
            print("\nResult:")
            print(result[0].text)
        else:
            print("No result returned")
        
        # Try to retrieve the memory
        print("\nRetrieving memory...")
        retrieve_result = await client.call_tool("retrieve_memory", {"query": "test memory", "n_results": 5})
        
        # Print result
        if retrieve_result:
            print("\nRetrieve Result:")
            print(retrieve_result[0].text)
        else:
            print("No retrieve result returned")
            
        # Check database health
        print("\nChecking database health...")
        health_result = await client.call_tool("check_database_health", {})
        
        # Print result
        if health_result:
            print("\nHealth Check Result:")
            print(health_result[0].text)
        else:
            print("No health check result returned")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
    finally:
        # Disconnect client
        await client.shutdown()

async def main():
    """Main function."""
    print("=== MCP Memory Service Test: Store Memory ===\n")
    await store_memory()

if __name__ == "__main__":
    asyncio.run(main())
