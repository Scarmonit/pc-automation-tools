# 🤝 Aider AI Pair Programming Setup Guide

Aider is an AI-powered coding assistant that works directly in your terminal, helping you write, debug, and refactor code with natural language instructions. This guide shows you how to set up Aider with local AI models for private, cost-effective AI pair programming.

## 🚀 Quick Start

### Automatic Setup
```bash
# Install and configure Aider
bash setup_aider.sh

# Start coding session
aider --model ollama/llama3.2
```

### Manual Installation
```bash
# Install Aider
pip install aider-chat

# Or using pipx (recommended)
pipx install aider-chat
```

## 📋 Prerequisites

- **Python 3.8+** with pip or pipx
- **Git** (for version control integration)
- **Ollama** or **LocalAI** running locally
- **Text Editor** (VS Code, Vim, etc.) - optional but recommended

## 🔧 Configuration

### 1. Environment Setup

```bash
# For Ollama (recommended)
export OLLAMA_API_BASE="http://localhost:11434"

# For LocalAI
export OPENAI_API_BASE="http://localhost:8080/v1"
export OPENAI_API_KEY="sk-localai"
```

### 2. Model Configuration

Create `~/.aider.conf.yml`:

```yaml
# Aider configuration
model: ollama/llama3.2
edit-format: diff
auto-commits: true
auto-lint: true
auto-test: true

# Ollama settings
api-base: http://localhost:11434
api-key: ollama

# Git settings
commit-prompt: "Brief commit message for:"
dirty-commits: true

# Editor integration
editor: code
```

### 3. Project-Specific Configuration

Create `.aider.conf.yml` in your project root:

```yaml
# Project-specific Aider settings
model: ollama/codellama:7b
files:
  - src/
  - tests/
  - README.md
exclude:
  - node_modules/
  - .git/
  - __pycache__/
  - "*.pyc"
```

## 🎯 Basic Usage

### Starting Aider

```bash
# Start in current directory
aider

# Specify files to include
aider src/main.py tests/test_main.py

# Use specific model
aider --model ollama/codellama:7b

# With configuration file
aider --config .aider.conf.yml
```

### Essential Commands

```bash
# Inside Aider session
/help           # Show help
/add file.py    # Add file to session
/drop file.py   # Remove file from session
/ls             # List files in session
/git            # Show git status
/commit         # Make git commit
/diff           # Show current diff
/undo           # Undo last change
/exit           # Exit Aider
```

## 💡 Coding with Aider

### 1. Basic Code Generation

```
> Create a Python function to calculate fibonacci numbers with memoization

Aider will:
1. Create the function
2. Add it to your file
3. Make a git commit
```

### 2. Code Refactoring

```
> Refactor the calculate_fibonacci function to use a class-based approach with better error handling

Aider will:
1. Analyze existing code
2. Refactor to class-based design
3. Add error handling
4. Update any related code
```

### 3. Bug Fixing

```
> There's a bug in the user authentication function - it's not handling empty passwords correctly

Aider will:
1. Identify the bug
2. Fix the issue
3. Add appropriate validation
4. Suggest tests if needed
```

### 4. Test Creation

```
> Create comprehensive unit tests for the UserManager class

Aider will:
1. Analyze the class
2. Create test file
3. Write comprehensive tests
4. Include edge cases
```

## 🛠️ Advanced Workflows

### 1. Code Review and Improvement

```bash
# Add existing files for review
aider existing_code.py

# Ask for improvements
> Review this code and suggest improvements for performance and readability
```

### 2. Documentation Generation

```bash
# Include code files
aider src/*.py README.md

# Generate documentation
> Add comprehensive docstrings to all functions and update the README with usage examples
```

### 3. Feature Development

```bash
# Start with requirements
aider requirements.txt main.py

# Develop feature
> Add user authentication feature with JWT tokens, password hashing, and session management
```

### 4. Debugging Session

```bash
# Include relevant files
aider src/api.py tests/test_api.py logs/error.log

# Debug issues
> The API is returning 500 errors for POST requests. Help me debug this issue.
```

## 🔄 Integration with Repository

### Using with Unified Orchestrator

```python
# In llmstack/unified_orchestrator.py
def route_to_aider(self, task: str, files: List[str] = None):
    """Route coding tasks to Aider"""
    import subprocess
    
    cmd = ["aider", "--model", "ollama/codellama:7b"]
    if files:
        cmd.extend(files)
    
    # Add task as input
    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    stdout, stderr = process.communicate(input=task)
    return {"stdout": stdout, "stderr": stderr}
```

### Custom Aider Integration

```python
# aider_wrapper.py
import subprocess
import json
from pathlib import Path

class AiderWrapper:
    """Wrapper for Aider AI coding assistant"""
    
    def __init__(self, model="ollama/llama3.2", config_file=None):
        self.model = model
        self.config_file = config_file or ".aider.conf.yml"
    
    def code_with_context(self, prompt, files=None, project_dir="."):
        """Execute Aider with specific context"""
        cmd = [
            "aider",
            "--model", self.model,
            "--config", self.config_file,
            "--yes",  # Auto-confirm changes
            "--message", prompt
        ]
        
        if files:
            cmd.extend(files)
        
        result = subprocess.run(
            cmd,
            cwd=project_dir,
            capture_output=True,
            text=True
        )
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
    
    def review_code(self, files, focus_areas=None):
        """Code review with Aider"""
        prompt = "Review this code for:"
        if focus_areas:
            prompt += f" {', '.join(focus_areas)}"
        else:
            prompt += " bugs, security issues, performance, and best practices"
        
        return self.code_with_context(prompt, files)
    
    def generate_tests(self, source_files):
        """Generate tests for source files"""
        prompt = "Create comprehensive unit tests with good coverage and edge cases"
        return self.code_with_context(prompt, source_files)
    
    def refactor_code(self, files, refactor_goal):
        """Refactor code with specific goal"""
        prompt = f"Refactor this code to: {refactor_goal}"
        return self.code_with_context(prompt, files)
```

## 🧪 Testing Aider Setup

### 1. Basic Functionality Test

```bash
# Create test file
echo "def hello(): pass" > test_aider.py

# Test with Aider
aider test_aider.py --message "Implement the hello function to print 'Hello, World!'"

# Verify result
cat test_aider.py
```

### 2. Model Connection Test

```bash
# Test model connection
aider --model ollama/llama3.2 --message "print('Aider is working!')" test.py
```

### 3. Configuration Test

```bash
# Test configuration
aider --config ~/.aider.conf.yml --dry-run test.py
```

## 📊 Productivity Tips

### 1. Effective Prompting

**Good prompts:**
```
✓ "Add error handling to the database connection function"
✓ "Refactor the user authentication logic to use JWT tokens"
✓ "Create unit tests for the Calculator class with edge cases"
✓ "Optimize the search function for better performance"
```

**Less effective prompts:**
```
✗ "Fix this"
✗ "Make it better"
✗ "Add stuff"
```

### 2. File Management

```bash
# Start with core files
aider main.py config.py

# Add related files as needed
/add utils.py
/add tests/test_main.py

# Remove files when switching context
/drop config.py
```

### 3. Git Integration

```bash
# Automatic commits (recommended)
aider --auto-commits src/

# Manual commit control
aider --no-auto-commits src/
# Then use /commit when ready
```

### 4. Iterative Development

```
1. Start with basic implementation
   > "Create a basic user registration function"

2. Add features iteratively  
   > "Add email validation to the registration function"

3. Improve and refine
   > "Add password strength requirements and better error messages"

4. Add tests
   > "Create tests for all the registration scenarios"
```

## 🛟 Troubleshooting

### Common Issues

#### 1. Model Connection Issues
```bash
# Check Ollama is running
curl http://localhost:11434/api/version

# Verify model is available
ollama list

# Pull model if missing
ollama pull llama3.2
ollama pull codellama:7b
```

#### 2. Configuration Problems
```bash
# Check configuration file
cat ~/.aider.conf.yml

# Test with minimal config
aider --model ollama/llama3.2 --no-auto-commits test.py
```

#### 3. Git Integration Issues
```bash
# Initialize git if needed
git init
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Check git status
git status
```

#### 4. File Access Issues
```bash
# Check file permissions
ls -la target_file.py

# Fix permissions if needed
chmod 644 target_file.py
```

#### 5. Performance Issues
```bash
# Use smaller, faster models for quick tasks
aider --model ollama/llama3.2:1b

# Use coding-specific models for complex tasks
aider --model ollama/codellama:7b
```

### Error Messages

#### "No API key found"
```bash
# Set environment variable
export OPENAI_API_KEY="ollama"
# Or for LocalAI
export OPENAI_API_KEY="sk-localai"
```

#### "Model not found"
```bash
# Check available models
ollama list

# Use correct model name
aider --model ollama/llama3.2  # Note the ollama/ prefix
```

#### "Git repository not found"
```bash
# Initialize git repository
git init

# Or use --no-git flag
aider --no-git file.py
```

## 🚀 Advanced Features

### 1. Custom Instructions

Create `.aider.instructions.md` in your project:

```markdown
# Project Coding Guidelines

## Code Style
- Use Python 3.8+ features
- Follow PEP 8 style guide
- Add type hints to all functions
- Include docstrings for all public methods

## Testing
- Use pytest for testing
- Aim for 90%+ code coverage
- Include integration tests
- Mock external dependencies

## Error Handling
- Use specific exception types
- Log errors appropriately
- Provide helpful error messages
- Implement retry logic for network calls
```

### 2. Multiple Model Strategy

```yaml
# .aider.conf.yml
models:
  fast: ollama/llama3.2:1b      # Quick edits
  balanced: ollama/llama3.2:3b  # General coding
  powerful: ollama/codellama:13b # Complex tasks
```

```bash
# Use different models for different tasks
aider --model ollama/llama3.2:1b --message "Fix typo in comment"
aider --model ollama/codellama:13b --message "Implement complex algorithm"
```

### 3. Batch Processing

```bash
# Process multiple files with same instruction
for file in src/*.py; do
    aider "$file" --message "Add type hints and improve documentation" --yes
done
```

### 4. Integration Scripts

```bash
#!/bin/bash
# aider_code_review.sh

echo "Starting Aider code review..."

# Review changed files
changed_files=$(git diff --name-only HEAD~1 HEAD)

if [ -n "$changed_files" ]; then
    aider $changed_files \
        --message "Review these changes for bugs, security issues, and best practices" \
        --no-auto-commits
    
    echo "Review complete. Check the suggestions and commit if appropriate."
else
    echo "No changed files to review."
fi
```

## 📚 Best Practices

### 1. Project Setup
- Initialize git repository before using Aider
- Create `.aider.conf.yml` for project-specific settings
- Add `.aider.instructions.md` for coding guidelines
- Use `.gitignore` to exclude temporary files

### 2. Workflow Integration
- Use Aider for focused coding tasks
- Combine with other tools (tests, linting, etc.)
- Regular commits for better change tracking
- Code review before pushing to main branch

### 3. Prompt Engineering
- Be specific about requirements
- Provide context about the codebase
- Mention relevant technologies and patterns
- Ask for explanations when learning

### 4. Model Selection
- Use fast models for simple tasks
- Use coding-specific models for complex logic
- Switch models based on task complexity
- Consider resource constraints

## 🔗 Integration Examples

### With AutoGen
```python
# Combine Aider with AutoGen for comprehensive development
def collaborative_coding(task):
    # Use AutoGen for planning
    plan = autogen_agent.chat(f"Create development plan for: {task}")
    
    # Use Aider for implementation
    for step in plan.steps:
        aider_result = aider_wrapper.code_with_context(
            step.description, 
            step.files
        )
        
        # Review with AutoGen
        review = autogen_agent.chat(f"Review this implementation: {aider_result}")
    
    return {"plan": plan, "implementation": aider_result, "review": review}
```

### With Flowise
```python
# Use Flowise to orchestrate Aider workflows
def flowise_aider_integration(workflow_id, code_request):
    # Trigger Flowise workflow that includes Aider steps
    import requests
    
    response = requests.post(
        f"http://localhost:3001/api/v1/prediction/{workflow_id}",
        json={
            "question": code_request,
            "aider_config": {
                "model": "ollama/codellama:7b",
                "auto_commits": True
            }
        }
    )
    
    return response.json()
```

## 📈 Next Steps

1. **Master Basic Workflows**: Practice with simple coding tasks
2. **Explore Advanced Features**: Try custom instructions and multi-model strategies
3. **Integrate with CI/CD**: Automate code review and testing
4. **Team Collaboration**: Share configurations and best practices
5. **Contribute to Aider**: Help improve the tool with feedback and contributions

## 🎓 Learning Resources

### Official Documentation
- [Aider Documentation](https://aider.chat/docs/)
- [Aider GitHub Repository](https://github.com/paul-gauthier/aider)

### Repository Examples
- [Aider Examples](llmstack/examples/03_aider_coding.md)
- [AI Frameworks Integration](llmstack/ai_frameworks_integration.py)

### Community Resources
- [Aider Discord Community](https://discord.gg/Tv2uQnR)
- [Best Practices Guide](https://aider.chat/docs/usage.html)

---

**🎯 Aider is now configured for AI-powered pair programming with your local models!**

Start coding with AI assistance and experience the future of software development.