#!/usr/bin/env python3
"""
GitHub Copilot Configuration Validator
Validates that Copilot configuration will work properly for pull request reviews
"""

import os
import yaml
import json
import glob
from pathlib import Path
from typing import List, Dict, Set

def load_copilot_config() -> Dict:
    """Load and validate the Copilot configuration"""
    config_path = Path(".github/copilot.yml")
    
    if not config_path.exists():
        print("❌ .github/copilot.yml not found")
        return {}
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        print("✅ Copilot configuration loaded successfully")
        return config
    except yaml.YAMLError as e:
        print(f"❌ Invalid YAML in copilot.yml: {e}")
        return {}

def get_file_patterns(config: Dict) -> List[str]:
    """Extract important_files patterns from config"""
    repo_config = config.get('repository', {})
    return repo_config.get('important_files', [])

def test_file_patterns(patterns: List[str]) -> None:
    """Test if file patterns match actual repository files"""
    print("\n🔍 Testing file patterns...")
    
    # Get all files in repository (excluding .git)
    all_files = []
    for root, dirs, files in os.walk('.'):
        # Skip .git directory
        if '.git' in dirs:
            dirs.remove('.git')
        
        for file in files:
            file_path = os.path.join(root, file)
            # Convert to relative path and normalize
            rel_path = os.path.relpath(file_path, '.')
            all_files.append(rel_path)
    
    print(f"📊 Total files in repository: {len(all_files)}")
    
    # Test each pattern
    matched_files = set()
    for pattern in patterns:
        pattern_matches = []
        
        # Simple glob pattern matching
        try:
            matches = glob.glob(pattern, recursive=True)
            pattern_matches.extend(matches)
        except Exception as e:
            print(f"⚠️  Pattern '{pattern}' failed: {e}")
            continue
        
        if pattern_matches:
            print(f"✅ Pattern '{pattern}': {len(pattern_matches)} files")
            matched_files.update(pattern_matches)
        else:
            print(f"⚠️  Pattern '{pattern}': 0 files")
    
    print(f"📈 Total files matched by patterns: {len(matched_files)}")
    
    # Show coverage
    coverage = len(matched_files) / len(all_files) * 100 if all_files else 0
    print(f"📊 File coverage: {coverage:.1f}%")
    
    # Show some unmatched files
    unmatched = set(all_files) - matched_files
    if unmatched and len(unmatched) <= 10:
        print(f"\n📝 Unmatched files ({len(unmatched)}):")
        for file in sorted(list(unmatched)[:10]):
            print(f"   - {file}")
    elif unmatched:
        print(f"\n📝 {len(unmatched)} files not matched by patterns")
        print("   First 10 unmatched files:")
        for file in sorted(list(unmatched)[:10]):
            print(f"   - {file}")

def check_file_sizes() -> None:
    """Check for files that might be too large for review"""
    print("\n📏 Checking file sizes...")
    
    large_files = []
    max_size = 10000  # lines
    
    for file_path in Path('.').rglob('*'):
        if file_path.is_file() and not '.git' in str(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = sum(1 for _ in f)
                
                if lines > max_size:
                    large_files.append((str(file_path), lines))
            except Exception:
                # Skip binary files or files we can't read
                continue
    
    if large_files:
        print(f"⚠️  Found {len(large_files)} files over {max_size} lines:")
        for file_path, lines in sorted(large_files, key=lambda x: x[1], reverse=True)[:5]:
            print(f"   - {file_path}: {lines} lines")
    else:
        print(f"✅ No files exceed {max_size} lines")

def validate_review_config(config: Dict) -> None:
    """Validate pull request review configuration"""
    print("\n🔍 Validating review configuration...")
    
    review_config = config.get('review', {})
    
    if not review_config:
        print("⚠️  No review configuration found - using defaults")
        return
    
    # Check required fields
    if review_config.get('enabled', True):
        print("✅ Pull request reviews enabled")
    else:
        print("⚠️  Pull request reviews disabled")
    
    max_files = review_config.get('max_files', 50)
    max_file_size = review_config.get('max_file_size', 10000)
    
    print(f"📊 Max files per PR: {max_files}")
    print(f"📊 Max file size: {max_file_size} lines")
    
    skip_patterns = review_config.get('skip_patterns', [])
    print(f"📊 Skip patterns: {len(skip_patterns)}")
    
    focus_areas = review_config.get('focus_on', [])
    print(f"📊 Focus areas: {', '.join(focus_areas) if focus_areas else 'none specified'}")

def validate_yaml_syntax() -> bool:
    """Validate YAML syntax of configuration files"""
    print("\n🔍 Validating YAML syntax...")
    
    yaml_files = [
        ".github/copilot.yml",
        ".github/workflows/*.yml",
        ".github/workflows/*.yaml",
        "docker-compose*.yml",
        "docker-compose*.yaml"
    ]
    
    valid = True
    
    for pattern in yaml_files:
        files = glob.glob(pattern, recursive=True)
        for file_path in files:
            try:
                with open(file_path, 'r') as f:
                    yaml.safe_load(f)
                print(f"✅ {file_path}")
            except yaml.YAMLError as e:
                print(f"❌ {file_path}: {e}")
                valid = False
            except FileNotFoundError:
                # Skip missing files
                pass
    
    return valid

def main():
    """Main validation function"""
    print("🤖 GitHub Copilot Configuration Validator")
    print("=" * 50)
    
    # Load configuration
    config = load_copilot_config()
    if not config:
        print("❌ Cannot validate without valid configuration")
        return 1
    
    # Validate YAML syntax
    if not validate_yaml_syntax():
        print("❌ YAML syntax errors found")
        return 1
    
    # Get and test file patterns
    patterns = get_file_patterns(config)
    if patterns:
        test_file_patterns(patterns)
    else:
        print("⚠️  No important_files patterns found")
    
    # Check file sizes
    check_file_sizes()
    
    # Validate review configuration
    validate_review_config(config)
    
    print("\n" + "=" * 50)
    print("✅ Copilot configuration validation complete!")
    
    # Provide recommendations
    print("\n📋 Recommendations:")
    if len(patterns) < 5:
        print("   - Consider adding more file patterns for better coverage")
    
    print("   - Test with small PRs first to verify configuration")
    print("   - Monitor Copilot logs for any review failures")
    print("   - Update patterns based on actual file structure")
    
    return 0

if __name__ == "__main__":
    exit(main())