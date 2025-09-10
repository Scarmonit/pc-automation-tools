#!/usr/bin/env python3
"""
Test script to verify Copilot configuration fixes
Creates a test scenario similar to PR #29 to ensure Copilot can review files
"""

import os
import tempfile
import shutil
from pathlib import Path

def create_test_files():
    """Create test files similar to those in PR #29"""
    test_files = [
        # Root level files that were in PR #29
        ("test_readme.md", "# Test README\n\nThis is a test file.\n"),
        ("test_automation.py", "#!/usr/bin/env python3\nprint('Test automation')\n"),
        ("test_config.json", '{"test": "configuration"}'),
        
        # Script files
        ("scripts/test_script.sh", "#!/bin/bash\necho 'Test script'\n"),
        ("scripts/test_config.py", "# Test configuration\nCONFIG = {'test': True}\n"),
        
        # LLMStack files
        ("llmstack/test_agent.py", "# Test agent\nclass TestAgent:\n    pass\n"),
        ("llmstack/test_readme.md", "# Test LLMStack\n\nTest content.\n"),
        
        # Docker files
        ("docker-compose.test.yml", "version: '3.8'\nservices:\n  test:\n    image: test\n"),
        
        # Config files
        ("test.yaml", "test:\n  config: true\n"),
        (".env.test", "TEST_VAR=test_value\n"),
    ]
    
    print("📝 Creating test files...")
    created_files = []
    
    for file_path, content in test_files:
        # Create directory if needed
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        with open(file_path, 'w') as f:
            f.write(content)
        
        created_files.append(file_path)
        print(f"   ✅ Created: {file_path}")
    
    return created_files

def test_with_diagnostic_tool(files):
    """Test the files with our diagnostic tool"""
    print("\n🔍 Testing files with diagnostic tool...")
    
    import subprocess
    import sys
    
    # Run the diagnostic tool
    cmd = [sys.executable, "scripts/diagnose_copilot_review.py"] + files
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running diagnostic: {e}")
        return False

def cleanup_test_files(files):
    """Clean up the test files"""
    print("\n🧹 Cleaning up test files...")
    
    for file_path in files:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"   🗑️ Removed: {file_path}")
        except Exception as e:
            print(f"   ⚠️ Could not remove {file_path}: {e}")
    
    # Remove empty directories
    for dir_path in ["scripts", "llmstack"]:
        try:
            if os.path.exists(dir_path) and not os.listdir(dir_path):
                os.rmdir(dir_path)
                print(f"   🗑️ Removed empty directory: {dir_path}")
        except Exception:
            pass

def main():
    """Main test function"""
    print("🧪 Testing Copilot Configuration Fix")
    print("=" * 50)
    
    # Create test files
    created_files = create_test_files()
    
    try:
        # Test with diagnostic tool
        success = test_with_diagnostic_tool(created_files)
        
        if success:
            print("\n✅ TEST PASSED: Copilot should be able to review these files")
        else:
            print("\n❌ TEST FAILED: Issues found with file review capability")
    
    finally:
        # Always clean up
        cleanup_test_files(created_files)
    
    print("\n📋 Test completed!")
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())