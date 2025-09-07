# 🤝 Contributing to PC Automation Tools

Thank you for your interest in contributing! This guide helps you get started with contributing to our AI automation tools repository.

## 🚀 Quick Start for Contributors

### 1. Fork & Clone
```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/pc-automation-tools.git
cd pc-automation-tools

# Add upstream remote
git remote add upstream https://github.com/Scarmonit/pc-automation-tools.git
```

### 2. Set Up Development Environment
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If exists

# Run initial setup
bash scripts/check_system.sh
```

### 3. Make Your Changes
```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make your changes
# ... edit files ...

# Test your changes
bash scripts/validate_deployment.sh
python3 test_automation.py
```

### 4. Submit Pull Request
```bash
# Commit changes
git add .
git commit -m "feat: add your feature description"

# Push to your fork
git push origin feature/your-feature-name

# Create pull request on GitHub
```

## 📋 Contribution Types

### 🐛 Bug Reports
**Before submitting:**
- Check existing issues
- Use the troubleshooting guide
- Gather system information

**Issue template:**
```markdown
**Bug Description:**
Clear description of the bug

**System Information:**
- OS: 
- Python version:
- Docker version:
- Available RAM:

**Steps to Reproduce:**
1. Step one
2. Step two
3. Step three

**Expected Behavior:**
What should happen

**Actual Behavior:**
What actually happens

**Logs:**
```
Paste relevant logs here
```
**Additional Context:**
Any other relevant information
```

### ✨ Feature Requests
**Feature template:**
```markdown
**Feature Description:**
Clear description of the proposed feature

**Use Case:**
Why is this feature needed? What problem does it solve?

**Proposed Implementation:**
How do you envision this working?

**Alternatives Considered:**
What other approaches did you consider?

**Additional Context:**
Any other relevant information
```

### 📝 Documentation Improvements
- Fix typos and grammar
- Add missing documentation
- Improve existing guides
- Add examples and tutorials
- Update outdated information

### 🔧 Code Contributions
- Bug fixes
- New features
- Performance improvements
- Test additions
- Code refactoring

## 🏗️ Development Guidelines

### Code Style

#### Python Code
```python
# Use type hints
def process_ai_request(prompt: str, model: str = "llama3.2") -> Dict[str, Any]:
    """Process AI request with specified model.
    
    Args:
        prompt: The user prompt
        model: AI model to use
        
    Returns:
        Dictionary containing response and metadata
        
    Raises:
        ValueError: If prompt is empty
        ConnectionError: If AI service is unavailable
    """
    if not prompt.strip():
        raise ValueError("Prompt cannot be empty")
    
    try:
        # Implementation here
        return {"response": "AI response", "status": "success"}
    except Exception as e:
        logger.error(f"AI request failed: {e}")
        raise ConnectionError(f"AI service unavailable: {e}")

# Use dataclasses for configuration
@dataclass
class AIConfig:
    """AI service configuration."""
    model_name: str = "llama3.2"
    temperature: float = 0.7
    max_tokens: int = 2048
    use_local: bool = True
```

#### Shell Scripts
```bash
#!/bin/bash
# Script description and purpose

set -e  # Exit on error
set -u  # Error on undefined variables

# Constants
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly LOG_FILE="/tmp/script.log"

# Functions
log_info() {
    echo "[INFO] $*" | tee -a "$LOG_FILE"
}

log_error() {
    echo "[ERROR] $*" >&2 | tee -a "$LOG_FILE"
}

main() {
    log_info "Starting script execution"
    
    # Implementation here
    
    log_info "Script completed successfully"
}

# Error handling
trap 'log_error "Script failed on line $LINENO"' ERR

# Run main function
main "$@"
```

#### Docker Best Practices
```dockerfile
# Use specific versions
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["python", "app.py"]
```

### Testing Guidelines

#### Unit Tests
```python
# test_ai_service.py
import pytest
from unittest.mock import Mock, patch
from your_module import AIService

class TestAIService:
    """Test cases for AI service."""
    
    @pytest.fixture
    def ai_service(self):
        """Create AI service instance for testing."""
        return AIService(model="test-model")
    
    def test_process_request_success(self, ai_service):
        """Test successful request processing."""
        # Arrange
        prompt = "Test prompt"
        expected_response = {"response": "Test response", "status": "success"}
        
        # Act
        with patch('your_module.requests.post') as mock_post:
            mock_post.return_value.json.return_value = expected_response
            result = ai_service.process_request(prompt)
        
        # Assert
        assert result["status"] == "success"
        assert "response" in result
        mock_post.assert_called_once()
    
    def test_process_request_empty_prompt(self, ai_service):
        """Test error handling for empty prompt."""
        with pytest.raises(ValueError, match="Prompt cannot be empty"):
            ai_service.process_request("")
    
    @pytest.mark.integration
    def test_real_ai_integration(self, ai_service):
        """Integration test with real AI service (marked as integration)."""
        # Only run if AI service is available
        pytest.skip("Integration test - run manually")
```

#### Integration Tests
```bash
#!/bin/bash
# integration_test.sh

# Test script for integration testing

set -e

echo "Starting integration tests..."

# Test 1: Service availability
echo "Testing service availability..."
curl -f http://localhost:11434/api/version || exit 1
curl -f http://localhost:3001/health || exit 1

# Test 2: AI request processing
echo "Testing AI request processing..."
response=$(curl -s -X POST http://localhost:11434/api/generate \
    -H "Content-Type: application/json" \
    -d '{"model":"llama3.2","prompt":"Say hello","stream":false}')

if echo "$response" | grep -q "hello"; then
    echo "✓ AI request test passed"
else
    echo "✗ AI request test failed"
    exit 1
fi

echo "All integration tests passed!"
```

### Documentation Standards

#### README Structure
```markdown
# 🎯 Component Name

Brief description of what this component does.

## 🚀 Quick Start

### Prerequisites
- Requirement 1
- Requirement 2

### Installation
```bash
# Installation commands
```

### Basic Usage
```python
# Usage example
```

## 📋 Features
- Feature 1
- Feature 2

## 🔧 Configuration
Configuration details...

## 🧪 Testing
Testing instructions...

## 🛟 Troubleshooting
Common issues and solutions...

## 📚 API Reference
API documentation...

## 🤝 Contributing
Link to contributing guidelines...
```

#### Code Documentation
```python
class AIAgent:
    """AI agent for processing user requests.
    
    This class provides a high-level interface for interacting with
    AI models, handling configuration, error management, and response
    processing.
    
    Attributes:
        model_name: Name of the AI model to use
        config: Configuration object for the agent
        
    Example:
        >>> agent = AIAgent(model_name="llama3.2")
        >>> response = agent.chat("Hello, how are you?")
        >>> print(response.content)
        "Hello! I'm doing well, thank you for asking."
    """
    
    def __init__(self, model_name: str, config: Optional[AIConfig] = None):
        """Initialize the AI agent.
        
        Args:
            model_name: Name of the AI model to use
            config: Optional configuration object. If None, uses defaults.
            
        Raises:
            ValueError: If model_name is empty or invalid
            ConnectionError: If unable to connect to AI service
        """
        pass
    
    def chat(self, message: str, **kwargs) -> AIResponse:
        """Send a chat message to the AI agent.
        
        Args:
            message: The message to send to the AI
            **kwargs: Additional parameters for the AI model
            
        Returns:
            AIResponse object containing the AI's response
            
        Raises:
            ValueError: If message is empty
            TimeoutError: If request times out
            APIError: If AI service returns an error
            
        Example:
            >>> response = agent.chat("Explain quantum computing")
            >>> print(response.content)
            "Quantum computing is a type of computation..."
        """
        pass
```

## 🧪 Testing Your Contributions

### Before Submitting
```bash
# 1. Run code style checks
python -m black .
python -m isort .
python -m flake8 .

# 2. Run tests
python -m pytest tests/
python -m pytest tests/ --integration  # Integration tests

# 3. Run system validation
bash scripts/validate_deployment.sh

# 4. Test documentation
# Build docs locally if applicable
# Check for broken links
```

### Test Coverage
- Aim for >80% test coverage on new code
- Include both unit and integration tests
- Test error conditions and edge cases
- Mock external dependencies appropriately

## 🔄 Release Process

### Versioning
We use [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist
1. Update version numbers
2. Update CHANGELOG.md
3. Run full test suite
4. Update documentation
5. Create release notes
6. Tag release
7. Deploy to staging
8. Deploy to production

## 🏷️ Commit Messages

### Format
```
type(scope): brief description

Longer description if needed.

Fixes #issue_number
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or modifying tests
- `chore`: Maintenance tasks

### Examples
```
feat(autogen): add multi-agent conversation support

Implement support for multi-agent conversations with
proper message routing and conversation management.

Fixes #123

fix(docker): resolve port conflict issue

Changed default Flowise port from 3001 to 3004 to avoid
conflicts with other services.

Fixes #456

docs(readme): update installation instructions

Add missing steps for GPU setup and clarify system
requirements for different deployment scenarios.
```

## 🤝 Code Review Process

### What We Look For
1. **Functionality**: Does the code work as intended?
2. **Testing**: Are there appropriate tests?
3. **Documentation**: Is the code well-documented?
4. **Style**: Does it follow our coding standards?
5. **Performance**: Are there any performance concerns?
6. **Security**: Are there any security implications?

### Review Checklist
- [ ] Code builds without errors
- [ ] All tests pass
- [ ] Documentation is updated
- [ ] Follows coding standards
- [ ] Includes appropriate tests
- [ ] No obvious security issues
- [ ] Performance is acceptable

## 🏆 Recognition

### Contributors
We recognize contributions in several ways:
- GitHub contributor statistics
- Mentions in release notes
- Contributors section in README
- Special recognition for significant contributions

### Types of Recognition
- **Bug Hunter**: Finding and reporting bugs
- **Feature Developer**: Implementing new features
- **Documentation Guru**: Improving documentation
- **Community Helper**: Helping other users
- **Performance Optimizer**: Improving system performance

## 📞 Getting Help

### Community Support
- **GitHub Discussions**: For questions and ideas
- **Issues**: For bug reports and feature requests
- **Discord/Slack**: Real-time community chat (if available)

### Maintainer Contact
- **Email**: [Contact information if appropriate]
- **GitHub**: @username mentions in issues/PRs

## 📝 Legal

### Contributor License Agreement
By contributing to this project, you agree that your contributions will be licensed under the same license as the project (MIT License).

### Code of Conduct
Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md) to ensure a welcoming environment for all contributors.

---

**🎉 Thank you for contributing to making AI automation tools better for everyone!**

Your contributions help build a powerful, open-source AI development platform that benefits the entire community.