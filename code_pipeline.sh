#!/bin/bash
# Code generation pipeline using multiple agents

PROJECT_NAME="$1"
REQUIREMENTS="$2"

echo "Starting code generation for: $PROJECT_NAME"

# Step 1: Generate with OpenHands
curl -X POST http://localhost:3002/api/generate \
  -H "Content-Type: application/json" \
  -d "{\"project\": \"$PROJECT_NAME\", \"requirements\": \"$REQUIREMENTS\"}" \
  -o "$PROJECT_NAME.zip"

# Step 2: Extract and refine with Aider
unzip "$PROJECT_NAME.zip" -d "$PROJECT_NAME"
cd "$PROJECT_NAME"
aider --message "Review and improve code quality, add tests" --yes

# Step 3: Commit results
git init
git add .
git commit -m "Initial generation and refinement"

echo "✓ Code generation complete"