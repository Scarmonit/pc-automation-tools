#!/usr/bin/env python3
"""
GitHub Copilot Pull Request Review Diagnostic Tool
Helps diagnose why Copilot might not be able to review files in a PR
"""

import os
import sys
import json
import yaml
import requests
from pathlib import Path
from typing import List, Dict, Optional

def load_copilot_config() -> Dict:
    """Load Copilot configuration"""
    config_path = Path(".github/copilot.yml")
    
    if not config_path.exists():
        return {}
    
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception:
        return {}

def check_file_against_patterns(file_path: str, patterns: List[str]) -> bool:
    """Check if a file matches any of the important_files patterns"""
    import fnmatch
    import glob
    
    for pattern in patterns:
        # Use glob for ** patterns, fnmatch for simple patterns
        if '**' in pattern:
            try:
                matches = glob.glob(pattern, recursive=True)
                if file_path in matches or file_path.lstrip('./') in matches:
                    return True
            except Exception:
                pass
        else:
            # Handle different pattern formats
            if fnmatch.fnmatch(file_path, pattern):
                return True
            # Also check without leading ./
            if file_path.startswith('./'):
                if fnmatch.fnmatch(file_path[2:], pattern):
                    return True
    
    return False

def analyze_file(file_path: str) -> Dict:
    """Analyze a single file for review suitability"""
    file_info = {
        'path': file_path,
        'exists': False,
        'size_lines': 0,
        'size_bytes': 0,
        'is_binary': False,
        'encoding_issues': False,
        'too_large': False
    }
    
    if not os.path.exists(file_path):
        return file_info
    
    file_info['exists'] = True
    
    try:
        # Check file size in bytes
        file_info['size_bytes'] = os.path.getsize(file_path)
        
        # Try to read as text
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            file_info['size_lines'] = len(lines)
        
        # Check if too large (common Copilot limits)
        if file_info['size_lines'] > 10000:
            file_info['too_large'] = True
        
    except UnicodeDecodeError:
        file_info['is_binary'] = True
    except Exception as e:
        file_info['encoding_issues'] = True
    
    return file_info

def diagnose_pr_files(changed_files: List[str]) -> Dict:
    """Diagnose why Copilot might not review the changed files"""
    config = load_copilot_config()
    patterns = config.get('repository', {}).get('important_files', [])
    review_config = config.get('review', {})
    
    max_files = review_config.get('max_files', 50)
    max_file_size = review_config.get('max_file_size', 10000)
    skip_patterns = review_config.get('skip_patterns', [])
    
    results = {
        'total_files': len(changed_files),
        'matched_patterns': 0,
        'too_large': 0,
        'binary_files': 0,
        'skipped_files': 0,
        'reviewable_files': 0,
        'issues': [],
        'file_details': []
    }
    
    print(f"🔍 Analyzing {len(changed_files)} changed files...")
    print(f"📊 Configuration: max_files={max_files}, max_file_size={max_file_size}")
    
    for file_path in changed_files:
        file_info = analyze_file(file_path)
        
        # Check against patterns
        matches_pattern = check_file_against_patterns(file_path, patterns)
        file_info['matches_pattern'] = matches_pattern
        
        # Check if should be skipped
        should_skip = any(check_file_against_patterns(file_path, [pattern]) 
                         for pattern in skip_patterns)
        file_info['should_skip'] = should_skip
        
        # Determine if reviewable
        reviewable = (matches_pattern and 
                     not should_skip and 
                     not file_info['is_binary'] and 
                     not file_info['too_large'] and
                     file_info['exists'])
        file_info['reviewable'] = reviewable
        
        # Update counters
        if matches_pattern:
            results['matched_patterns'] += 1
        if file_info['too_large']:
            results['too_large'] += 1
        if file_info['is_binary']:
            results['binary_files'] += 1
        if should_skip:
            results['skipped_files'] += 1
        if reviewable:
            results['reviewable_files'] += 1
        
        results['file_details'].append(file_info)
    
    # Add overall issues
    if results['total_files'] > max_files:
        results['issues'].append(f"Too many files changed ({results['total_files']} > {max_files})")
    
    if results['reviewable_files'] == 0:
        results['issues'].append("No files are reviewable by Copilot")
    
    if results['matched_patterns'] < results['total_files'] * 0.5:
        results['issues'].append("Less than 50% of files match important_files patterns")
    
    return results

def print_diagnosis(results: Dict) -> None:
    """Print the diagnosis results"""
    print("\n" + "=" * 60)
    print("📊 COPILOT REVIEW DIAGNOSIS RESULTS")
    print("=" * 60)
    
    print(f"📁 Total files changed: {results['total_files']}")
    print(f"✅ Files matching patterns: {results['matched_patterns']}")
    print(f"🔍 Reviewable files: {results['reviewable_files']}")
    print(f"📏 Too large files: {results['too_large']}")
    print(f"🔒 Binary files: {results['binary_files']}")
    print(f"⏭️ Skipped files: {results['skipped_files']}")
    
    if results['issues']:
        print(f"\n⚠️ ISSUES FOUND:")
        for issue in results['issues']:
            print(f"   - {issue}")
    
    # Show problematic files
    problematic_files = [f for f in results['file_details'] 
                        if not f['reviewable'] and f['exists']]
    
    if problematic_files:
        print(f"\n❌ Non-reviewable files ({len(problematic_files)}):")
        for file_info in problematic_files[:10]:  # Show first 10
            reasons = []
            if not file_info['matches_pattern']:
                reasons.append("no pattern match")
            if file_info['should_skip']:
                reasons.append("skip pattern")
            if file_info['is_binary']:
                reasons.append("binary")
            if file_info['too_large']:
                reasons.append(f"too large ({file_info['size_lines']} lines)")
            
            print(f"   - {file_info['path']}: {', '.join(reasons)}")
    
    # Show reviewable files
    reviewable_files = [f for f in results['file_details'] if f['reviewable']]
    if reviewable_files:
        print(f"\n✅ Reviewable files ({len(reviewable_files)}):")
        for file_info in reviewable_files[:10]:  # Show first 10
            print(f"   - {file_info['path']} ({file_info['size_lines']} lines)")

def main():
    """Main diagnostic function"""
    if len(sys.argv) < 2:
        print("Usage: python diagnose_copilot_review.py <file1> [file2] ...")
        print("   or: python diagnose_copilot_review.py --test")
        print("")
        print("Examples:")
        print("   python diagnose_copilot_review.py README.md setup.py")
        print("   python diagnose_copilot_review.py --test  # Test with common files")
        return 1
    
    if sys.argv[1] == "--test":
        # Test with some common files in the repository
        test_files = [
            "README.md",
            ".github/copilot.yml", 
            "requirements.txt",
            "llmstack/ai_frameworks_integration.py",
            "scripts/setup_copilot_agents.sh",
            "docker-compose.development.yml"
        ]
        # Filter to files that actually exist
        changed_files = [f for f in test_files if os.path.exists(f)]
        print("🧪 Testing with sample repository files...")
    else:
        changed_files = sys.argv[1:]
    
    results = diagnose_pr_files(changed_files)
    print_diagnosis(results)
    
    # Provide recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    if results['reviewable_files'] == 0:
        print("   - Check if files match important_files patterns in .github/copilot.yml")
        print("   - Ensure files are text-based (not binary)")
        print("   - Split large files or reduce file size")
    elif results['reviewable_files'] < results['total_files'] * 0.8:
        print("   - Update important_files patterns to include more file types")
        print("   - Review skip_patterns to ensure they're not too broad")
    else:
        print("   - Configuration looks good for these files")
        print("   - Issue may be temporary or service-related")
    
    print("   - Try creating a smaller test PR to verify Copilot is working")
    print("   - Check GitHub Copilot service status")
    
    return 0 if results['reviewable_files'] > 0 else 1

if __name__ == "__main__":
    exit(main())