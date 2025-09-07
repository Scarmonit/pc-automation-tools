# AI Platform & PC Automation Tools

[![CI/CD Pipeline](https://github.com/Scarmonit/pc-automation-tools/workflows/PC%20Automation%20Tools%20CI/CD/badge.svg)](https://github.com/Scarmonit/pc-automation-tools/actions)
[![CodeQL](https://github.com/Scarmonit/pc-automation-tools/workflows/CodeQL%20Analysis/badge.svg)](https://github.com/Scarmonit/pc-automation-tools/actions)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests](https://github.com/Scarmonit/pc-automation-tools/workflows/Tests/badge.svg)](https://github.com/Scarmonit/pc-automation-tools/actions)

A comprehensive, modular AI platform combining multiple AI services, security tools, automation frameworks, and advanced PC automation tools with Claude AI integration.

## 🚀 Key Features

### 🖥️ PC Automation Tools
- **Screenshot Integration**: Advanced screenshot tools with Claude AI integration
- **OCR Text Extraction**: Automatic text recognition from screenshots
- **UI Element Detection**: Computer vision-based UI element identification
- **System Automation**: Windows PowerShell and batch automation scripts
- **Clipboard Integration**: Seamless screenshot path copying

### 🤖 AI Platform
- **Core AI Platform**: Multiple AI model integrations and MCP support
- **Security Suite**: Web scanning, API security testing, pattern detection
- **Dolphin Models**: Custom Ollama model management with GUI
- **Automation**: Swarm intelligence, distributed agents, AutoGPT integration
- **Database Layer**: Unified database system with sync capabilities
- **Monitoring**: Health checks and alerting system

### 🔧 Development Tools
- **Automated Testing**: Comprehensive test suite with pytest
- **CI/CD Pipeline**: GitHub Actions with multi-OS support
- **Code Quality**: Black, isort, flake8, mypy integration
- **Security Scanning**: CodeQL, Bandit, and Safety checks
- **Pre-commit Hooks**: Automated code quality enforcement

## 📦 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Scarmonit/pc-automation-tools.git
cd pc-automation-tools

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -e .[dev]
```

### Basic Usage

#### Screenshot Tools
```bash
# Take immediate screenshot for Claude
python src/pc_tools/screenshot.py

# Advanced screenshot with OCR
python src/pc_tools/advanced_screenshot.py --full --ocr

# Screenshot with countdown
python src/pc_tools/screenshot.py --delay 5
```

#### Main Platform
```bash
# Launch main platform
python main.py core

# Screenshot integration
python main.py pc_tools --action screenshot

# Run tests
python -m pytest src/tests/ -v
```

## 🏗️ Architecture

### Project Structure
```
├── src/
│   ├── pc_tools/                 # PC automation modules
│   │   ├── screenshot.py         # Basic screenshot tool
│   │   └── advanced_screenshot.py # Advanced screenshot features
│   └── tests/                    # Test suite
│       └── test_pc_tools.py      # PC tools tests
├── .github/
│   ├── workflows/               # CI/CD pipelines
│   └── ISSUE_TEMPLATE/          # Issue templates
├── main.py                      # Main entry point
├── requirements.txt             # Dependencies
├── pyproject.toml              # Project configuration
└── MASTER_LAUNCHER.bat         # Windows launcher
```

### Core Components

1. **Screenshot System** (`src/pc_tools/`)
   - Basic screenshot capture with clipboard integration
   - Advanced features: OCR, UI detection, region capture
   - Multiple capture modes: full screen, window, scrolling

2. **AI Integration**
   - Claude AI optimization for screenshot analysis  
   - Automatic metadata generation
   - Smart file naming and organization

3. **Testing Framework**
   - Unit tests for all components
   - Integration tests for cross-platform compatibility
   - Mock-based testing for UI interactions

## 🔧 Development

### Setting Up Development Environment

```bash
# Clone and setup
git clone https://github.com/Scarmonit/pc-automation-tools.git
cd pc-automation-tools

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install with development dependencies
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=src --cov-report=html

# Run specific test file
python -m pytest src/tests/test_pc_tools.py -v

# Run platform-specific tests
python -m pytest -m "not windows_only"  # Skip Windows-only tests
```

### Code Quality

```bash
# Format code
black src/
isort src/

# Lint code
flake8 src/
mypy src/

# Security scan
bandit -r src/
safety check
```

## 🚀 CI/CD Pipeline

### Automated Testing
- **Multi-OS Support**: Tests on Ubuntu and Windows
- **Python Versions**: 3.9, 3.10, 3.11
- **Coverage Reports**: Automatic coverage tracking with Codecov
- **Security Scans**: Bandit and Safety vulnerability checks

### Code Quality Checks
- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting and style checks
- **mypy**: Static type checking
- **CodeQL**: Security analysis

### Deployment
- **Automated Releases**: Version-based releases with changelog
- **Documentation**: GitHub Pages deployment
- **PyPI Publishing**: Automated package publishing

## 🤝 Contributing

### Issue Templates
- **Bug Reports**: Structured bug reporting with system information
- **Feature Requests**: Feature proposals with priority classification
- **Security Issues**: Private security vulnerability reporting

### Pull Request Process
1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Run the full test suite
5. Submit a pull request with our template

### Development Guidelines
- Follow PEP 8 style guidelines
- Add tests for new functionality
- Update documentation for user-facing changes
- Use conventional commit messages

## 📋 System Requirements

### Minimum Requirements
- **Python**: 3.9+
- **OS**: Windows 10+, Ubuntu 18.04+, macOS 10.15+
- **Memory**: 4GB RAM minimum
- **Storage**: 1GB free space

### Optional Dependencies
- **Tesseract OCR**: For text extraction features
- **OpenCV**: For advanced computer vision
- **Win32 APIs**: For Windows-specific features

## 🐛 Known Issues & Limitations

- OCR accuracy depends on image quality and text clarity
- Windows-specific features require Windows 10+ with PowerShell 5+
- Some screenshot features may require display permissions on macOS/Linux

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Claude AI for advanced screenshot analysis capabilities
- OpenCV community for computer vision tools
- pytest team for excellent testing framework
- GitHub Actions for reliable CI/CD infrastructure

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Scarmonit/pc-automation-tools/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Scarmonit/pc-automation-tools/discussions)
- **Security**: Report security issues privately via GitHub Security tab

---

**Built with ❤️ for seamless PC automation and AI integration**