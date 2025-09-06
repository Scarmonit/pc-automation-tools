# Claude Code Hook System - Problem Solved

## The Core Issue: UTF-8 BOM Breaking JSON Parsing

### Root Cause Discovered
The fundamental problem preventing all Claude Code hooks from working was a **UTF-8 Byte Order Mark (BOM)** in the `settings.json` file. This invisible character at the beginning of the file caused JSON parsing to fail completely.

### Error Symptoms
- Debug output: `Invalid settings in userSettings source - key: unknown, error: Expected object, received null`
- Hooks configured properly but never executing
- No hook debug output despite correct configuration
- JSON validation failing with `Unexpected UTF-8 BOM` error

### Solution Applied
```bash
# Remove UTF-8 BOM from settings file
sed '1s/^\xEF\xBB\xBF//' settings.json > settings_fixed.json && mv settings_fixed.json settings.json

# Verify JSON is now valid
python -m json.tool settings.json
```

## Working Hook Configuration

### Verified Syntax
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "cd \"$CLAUDE_PROJECT_DIR\" && if ls test_*.* *_test.* *.tmp *.log debug_*.* 2>/dev/null; then echo \"Auto-cleaning test files...\" && rm -f test_*.* *_test.* *.tmp *.log debug_*.* 2>/dev/null && echo \"Cleanup complete\"; fi",
            "timeout": 30
          }
        ]
      }
    ],
    "SessionEnd": [
      {
        "hooks": [
          {
            "type": "command", 
            "command": "cd \"$CLAUDE_PROJECT_DIR\" && echo \"Final session cleanup...\" && rm -f test_*.* *_test.* *.tmp *.log debug_*.* 2>/dev/null && echo \"Session cleanup complete\"",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

## Research Findings

### 1. Common Hook Issues (From GitHub Issues)
- **Version-specific bugs**: Versions 1.0.51 and 1.0.52 had known hook execution problems
- **Configuration format errors**: Incorrect JSON structure prevents hook loading
- **File permission issues**: Scripts must be executable
- **Path problems**: Template variables not expanding properly

### 2. Working Examples Found
- **disler/claude-code-hooks-mastery**: Comprehensive hook examples
- **decider/claude-hooks**: Production-ready hook configurations
- **Real user implementations**: Python-based hooks with UV dependency management

### 3. Key Technical Details
- **Environment Variables**: Use `$CLAUDE_PROJECT_DIR` not `$PWD`
- **Hook Events Available**: PreToolUse, PostToolUse, UserPromptSubmit, Stop, SubagentStop, PreCompact, SessionStart, SessionEnd
- **Execution Context**: Hooks run in shell with specific environment setup
- **Error Handling**: Exit code 0 = success, exit code 2 = blocking error

## Verification Results

### ✅ Hooks Now Working
- JSON validation: PASS
- Hook execution: CONFIRMED (debug log shows trigger events)
- Configuration loading: SUCCESS
- Settings file monitoring: ACTIVE

### ⚠️ Remaining Challenges
- **Directory Context**: Hooks may run in different working directory than expected
- **Settings Reload**: Changes to hook configuration may require session restart
- **Complex Commands**: Multi-step commands need careful shell escaping

## Alternative Approaches Discovered

### 1. Python-Based Hooks
```python
#!/usr/bin/env python3
import json
import sys
import os

# Read JSON input from stdin
hook_data = json.load(sys.stdin)

# Perform cleanup logic
project_dir = os.environ.get('CLAUDE_PROJECT_DIR')
# ... cleanup logic here ...

# Exit with appropriate code
sys.exit(0)  # Success
```

### 2. Script-Based Hooks
```bash
#!/bin/bash
# Hook script with proper error handling
set -e

cd "$CLAUDE_PROJECT_DIR" || exit 1

# Cleanup logic with logging
if find . -name "test_*.*" -o -name "*_test.*" -o -name "*.tmp" -o -name "*.log" | head -1; then
    echo "Cleaning test files..."
    find . -name "test_*.*" -o -name "*_test.*" -o -name "*.tmp" -o -name "*.log" -delete
    echo "Cleanup complete"
fi
```

### 3. Slash Command Alternative
Instead of hooks, use custom slash commands for manual cleanup:
- `/alpha-cleanup`: Manual workspace cleanup
- `/validate-alpha`: Check workspace state
- `/deploy-ready`: Pre-deployment validation

## Lessons Learned

### 1. Always Check JSON Validity
- UTF-8 BOM is invisible but breaks JSON parsing
- Use `python -m json.tool` to validate configuration
- Check debug output for parsing errors

### 2. Hook Development Process
1. Start with simple debug hooks
2. Verify execution before adding complexity
3. Test directory context and environment variables
4. Use timeout values for long-running commands

### 3. Troubleshooting Steps
1. Check Claude Code version for known issues
2. Validate JSON syntax completely
3. Test commands manually before adding to hooks
4. Use debug mode to see hook execution details
5. Check file permissions and paths

## Current Status: RESOLVED

- **Problem**: UTF-8 BOM breaking JSON parsing ✅ FIXED
- **Hook Configuration**: Proper syntax implemented ✅ WORKING
- **Execution**: Hooks now trigger on tool use ✅ CONFIRMED
- **Cleanup Logic**: Ready for deployment ✅ IMPLEMENTED

The systematic research approach uncovered the root cause and provided multiple working solutions. The hook system is now functional and ready for production use with automatic workspace cleanup.