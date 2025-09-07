# Aider AI Coding Assistant Guide

## Basic Usage

### Start Aider in Your Project
```bash
cd your-project-folder
aider

# Or specify files to work with
aider file1.py file2.js README.md

# Use with specific model
aider --model ollama/deepseek-r1:8b
```

## Common Commands

### 1. Creating New Code
```
# In aider prompt:
> Create a Flask web app with user authentication using JWT tokens

> Add a REST API endpoint for user registration with email validation

> Write unit tests for the authentication module
```

### 2. Refactoring Existing Code
```
> Refactor the database connection to use connection pooling

> Convert this class to use async/await pattern

> Add type hints to all functions in this file

> Split this large function into smaller, testable functions
```

### 3. Debugging
```
> Fix the error: "TypeError: unsupported operand type(s)"

> This function returns None sometimes, find and fix the bug

> Add error handling to all API endpoints
```

### 4. Adding Features
```
> Add pagination to the get_users endpoint

> Implement caching using Redis for frequently accessed data

> Add a rate limiter to prevent API abuse
```

## Real-World Examples

### Example 1: Build a Todo API
```bash
mkdir todo-api && cd todo-api
aider

# In aider:
> Create a FastAPI todo list API with:
> - SQLite database using SQLAlchemy
> - CRUD operations for todos
> - User authentication with JWT
> - Input validation with Pydantic
> - Proper error handling
> Make it production ready with logging
```

### Example 2: Data Processing Script
```bash
aider data_processor.py

# In aider:
> Modify this script to:
> - Process CSV files in parallel using multiprocessing
> - Add progress bar with tqdm
> - Handle errors gracefully and log them
> - Output results to both JSON and Excel formats
> - Add command-line arguments using argparse
```

### Example 3: Fix and Improve Code
```bash
aider buggy_code.py

# In aider:
> Review this code for bugs and fix them
> Then optimize it for performance
> Add comprehensive error handling
> Write docstrings for all functions
> Add unit tests in a separate test file
```

## Advanced Features

### Working with Git
```
# Aider can make commits
> /commit Added user authentication

# Review changes
> /diff

# Undo last change
> /undo
```

### Adding Context
```
# Add more files to session
> /add database.py config.py

# Remove files
> /drop old_code.py

# Show current files
> /files
```

### Multi-file Refactoring
```
> Rename the User class to Account across all files
> Move all database models to a separate models/ directory
> Update all imports to use absolute imports
```

## Tips and Tricks

### 1. Architecture Decisions
```
> Should I use PostgreSQL or MongoDB for this chat application? Analyze the requirements and recommend

> Design a microservices architecture for this e-commerce platform
```

### 2. Code Review
```
> Review this code for security vulnerabilities
> Check for performance bottlenecks
> Suggest improvements following Python best practices
```

### 3. Documentation
```
> Generate API documentation in OpenAPI format
> Create a comprehensive README.md
> Write user guide for this CLI tool
```

### 4. Testing
```
> Write integration tests for the API endpoints
> Create test fixtures and mock data
> Add performance benchmarks
```

## Configuration

Your `.aider.conf.yml` is set to use:
- Model: `ollama/dolphin-mistral:latest`
- API: `http://localhost:11434/v1`
- Stream: Enabled
- Auto-commits: Disabled

To use different models per session:
```bash
# For complex reasoning
aider --model ollama/deepseek-r1:8b

# For large context
aider --model ollama/gemma2:27b

# For fast iterations
aider --model ollama/llama3.1:8b
```

## Workflow Example: Build a Web App

```bash
# 1. Initialize project
mkdir my-app && cd my-app
aider

# 2. Create the foundation
> Create a React + FastAPI full-stack app structure
> Backend: FastAPI with SQLAlchemy, Alembic migrations
> Frontend: React with TypeScript, Tailwind CSS
> Include Docker compose for development

# 3. Add features iteratively
> Add user registration and login to the backend
> Create React components for auth forms
> Implement JWT token refresh mechanism
> Add a dashboard page with charts using recharts

# 4. Testing
> Write pytest tests for all API endpoints
> Add React component tests with Jest
> Create E2E tests with Playwright

# 5. Deploy preparation
> Add production Dockerfile for both frontend and backend
> Create GitHub Actions CI/CD workflow
> Add environment variable configuration
```