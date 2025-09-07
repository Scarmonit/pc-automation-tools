#!/usr/bin/env python3
"""
Test Flowise Connection and API
"""

import requests
import json
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_flowise():
    """Test Flowise connection and functionality"""
    
    print("=" * 60)
    print("Testing Flowise Setup")
    print("=" * 60)
    
    # Test 1: Check if Flowise is running
    print("\n1. Checking Flowise server...")
    try:
        response = requests.get("http://localhost:3001", timeout=5)
        if response.status_code == 200:
            print("   [OK] Flowise is running at http://localhost:3001")
        else:
            print(f"   [X] Flowise returned status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("   [X] Flowise is not running. Run 'docker start flowise'")
        return False
    except Exception as e:
        print(f"   [X] Error: {e}")
        return False
    
    # Test 2: Check API endpoint
    print("\n2. Checking Flowise API...")
    try:
        response = requests.get("http://localhost:3001/api/v1/ping", timeout=5)
        if response.status_code in [200, 404]:  # 404 is ok, means API is responding
            print("   [OK] Flowise API is accessible")
        else:
            print(f"   [X] API returned status: {response.status_code}")
    except Exception as e:
        print(f"   [X] API Error: {e}")
    
    # Test 3: Provide setup instructions
    print("\n3. Setup Instructions:")
    print("   a. Open http://localhost:3001 in your browser")
    print("   b. Login with: admin / flowise123")
    print("   c. Click 'Chatflows' -> 'Add New'")
    print("   d. Import: flowise_agent_flow.json")
    print("   e. Configure your LLM provider")
    print("   f. Save and test the flow")
    
    print("\n" + "=" * 60)
    print("Flowise Quick Commands:")
    print("-" * 60)
    print("View logs:      docker logs -f flowise")
    print("Restart:        docker restart flowise")
    print("Stop:           docker stop flowise")
    print("Start:          docker start flowise")
    print("=" * 60)
    
    return True

def create_sample_flow():
    """Create a sample flow configuration"""
    
    flow = {
        "name": "Simple Chat Agent",
        "description": "A basic conversational agent",
        "nodes": [
            {
                "id": "llm_1",
                "type": "ChatOpenAI",
                "data": {
                    "model": "gpt-3.5-turbo",
                    "temperature": 0.7
                }
            },
            {
                "id": "memory_1",
                "type": "BufferMemory",
                "data": {
                    "memoryKey": "chat_history"
                }
            },
            {
                "id": "agent_1",
                "type": "ConversationalAgent",
                "data": {
                    "systemMessage": "You are a helpful AI assistant."
                }
            }
        ],
        "edges": [
            {"source": "llm_1", "target": "agent_1"},
            {"source": "memory_1", "target": "agent_1"}
        ]
    }
    
    # Save flow configuration
    with open("C:\\Users\\scarm\\llmstack\\sample_flow.json", "w") as f:
        json.dump(flow, f, indent=2)
    
    print("\nSample flow saved to: sample_flow.json")
    print("Import this in Flowise to get started quickly!")

if __name__ == "__main__":
    success = test_flowise()
    
    if success:
        print("\n[OK] Flowise is ready to use!")
        print("Open http://localhost:3001 to start building agents")
        
        # Optionally create sample flow
        create_sample = input("\nCreate sample flow configuration? (y/n): ")
        if create_sample.lower() == 'y':
            create_sample_flow()
    else:
        print("\n[X] Please fix the issues above and try again")
        sys.exit(1)