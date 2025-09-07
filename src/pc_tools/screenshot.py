#!/usr/bin/env python3
"""
Screenshot Tool for Claude Integration
Takes screenshots and prepares them for AI analysis
"""

import os
import sys
import time
import datetime
from pathlib import Path

try:
    from PIL import ImageGrab
    import pyperclip
except ImportError:
    print("Installing required packages...")
    os.system(f"{sys.executable} -m pip install pillow pyperclip")
    from PIL import ImageGrab
    import pyperclip


class ScreenshotTool:
    def __init__(self):
        self.screenshot_dir = Path.home() / "Pictures" / "Screenshots"
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
    
    def take_screenshot(self, delay=0):
        """Take a screenshot after optional delay"""
        if delay > 0:
            print(f"Taking screenshot in {delay} seconds...")
            for i in range(delay, 0, -1):
                print(f"  {i}...")
                time.sleep(1)
        
        # Generate filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Claude_Screenshot_{timestamp}.png"
        filepath = self.screenshot_dir / filename
        
        # Take screenshot
        print("Capturing screen...")
        screenshot = ImageGrab.grab()
        screenshot.save(filepath)
        
        # Copy path to clipboard
        pyperclip.copy(str(filepath))
        
        return filepath
    
    def get_latest_screenshot(self):
        """Get the most recent screenshot"""
        screenshots = list(self.screenshot_dir.glob("*.png"))
        if not screenshots:
            return None
        
        latest = max(screenshots, key=lambda p: p.stat().st_mtime)
        return latest
    
    def display_instructions(self, filepath):
        """Display instructions for using with Claude"""
        print("\n" + "="*50)
        print("✅ SCREENSHOT SAVED!")
        print("="*50)
        print(f"\nLocation: {filepath}")
        print("\n📋 Path copied to clipboard!")
        print("\nTo use with Claude:")
        print(f'  1. Tell Claude: "Read screenshot at {filepath}"')
        print('  2. Or simply: "Read my latest screenshot"')
        print("\n" + "="*50)


def main():
    """Main entry point"""
    tool = ScreenshotTool()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--latest":
            latest = tool.get_latest_screenshot()
            if latest:
                print(f"Latest screenshot: {latest}")
                pyperclip.copy(str(latest))
                print("Path copied to clipboard!")
            else:
                print("No screenshots found")
        elif sys.argv[1] == "--delay":
            delay = int(sys.argv[2]) if len(sys.argv) > 2 else 3
            filepath = tool.take_screenshot(delay)
            tool.display_instructions(filepath)
    else:
        # Default: immediate screenshot
        filepath = tool.take_screenshot()
        tool.display_instructions(filepath)


if __name__ == "__main__":
    main()