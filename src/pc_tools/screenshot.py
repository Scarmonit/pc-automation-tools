#!/usr/bin/env python3
"""
Screenshot Module
Advanced screenshot capture with various options
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, List
import argparse

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: Pillow not installed. Install with: pip install Pillow")

# Platform-specific imports
if sys.platform == "win32":
    try:
        import pyautogui
        import win32gui
        import win32con
        import win32api
        WINDOWS_TOOLS_AVAILABLE = True
    except ImportError:
        WINDOWS_TOOLS_AVAILABLE = False
        print("Warning: Windows tools not available. Install with: pip install pyautogui pywin32")
else:
    WINDOWS_TOOLS_AVAILABLE = False


class ScreenshotManager:
    """Advanced screenshot management with various capture options"""
    
    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = Path(output_dir) if output_dir else Path.cwd() / "screenshots"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        if WINDOWS_TOOLS_AVAILABLE:
            # Configure pyautogui
            pyautogui.FAILSAFE = True
            pyautogui.PAUSE = 0.1
        
    def take_screenshot(
        self, 
        filename: Optional[str] = None,
        region: Optional[Tuple[int, int, int, int]] = None,
        window_title: Optional[str] = None,
        quality: int = 95,
        format: str = "PNG"
    ) -> str:
        """
        Take a screenshot with various options
        
        Args:
            filename: Custom filename (auto-generated if None)
            region: (x, y, width, height) for partial screenshot
            window_title: Capture specific window
            quality: JPEG quality (1-100)
            format: Image format (PNG, JPEG, etc.)
            
        Returns:
            Path to saved screenshot
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.{format.lower()}"
        
        filepath = self.output_dir / filename
        
        try:
            if window_title and WINDOWS_TOOLS_AVAILABLE:
                screenshot = self._capture_window(window_title)
            elif region and WINDOWS_TOOLS_AVAILABLE:
                screenshot = pyautogui.screenshot(region=region)
            elif WINDOWS_TOOLS_AVAILABLE:
                screenshot = pyautogui.screenshot()
            else:
                # Fallback method
                screenshot = self._fallback_screenshot()
            
            # Save with specified quality
            if format.upper() == "JPEG":
                screenshot.save(filepath, format=format, quality=quality, optimize=True)
            else:
                screenshot.save(filepath, format=format)
            
            print(f"Screenshot saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            print(f"Error taking screenshot: {e}")
            return ""
    
    def _capture_window(self, window_title: str) -> Image:
        """Capture a specific window by title"""
        if not WINDOWS_TOOLS_AVAILABLE:
            raise ImportError("Windows tools not available")
        
        # Find window handle
        hwnd = win32gui.FindWindow(None, window_title)
        if not hwnd:
            # Try partial match
            windows = []
            win32gui.EnumWindows(lambda h, result: result.append((h, win32gui.GetWindowText(h))), windows)
            
            for handle, title in windows:
                if window_title.lower() in title.lower():
                    hwnd = handle
                    break
            
            if not hwnd:
                raise ValueError(f"Window '{window_title}' not found")
        
        # Get window coordinates
        rect = win32gui.GetWindowRect(hwnd)
        x, y, right, bottom = rect
        width = right - x
        height = bottom - y
        
        # Bring window to front
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.1)
        
        # Capture the window region
        return pyautogui.screenshot(region=(x, y, width, height))
    
    def _fallback_screenshot(self) -> Image:
        """Fallback screenshot method when PyAutoGUI is not available"""
        if PIL_AVAILABLE:
            # Create a placeholder image
            img = Image.new('RGB', (800, 600), color='lightgray')
            draw = ImageDraw.Draw(img)
            
            text = "Screenshot functionality requires:\n" \
                   "pip install pyautogui pillow\n" \
                   "(Windows: pip install pywin32)"
            
            try:
                font = ImageFont.load_default()
                draw.text((50, 250), text, fill='black', font=font)
            except:
                draw.text((50, 250), text, fill='black')
            
            return img
        else:
            raise ImportError("No screenshot method available")
    
    def capture_multiple(
        self, 
        count: int = 3, 
        interval: int = 2,
        prefix: str = "multi"
    ) -> List[str]:
        """Capture multiple screenshots with interval"""
        screenshots = []
        
        print(f"Capturing {count} screenshots with {interval}s interval...")
        
        for i in range(count):
            if i > 0:
                print(f"Next screenshot in {interval} seconds...")
                time.sleep(interval)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{prefix}_{i+1:02d}_{timestamp}.png"
            
            path = self.take_screenshot(filename)
            if path:
                screenshots.append(path)
            
            print(f"Captured {i+1}/{count}")
        
        return screenshots
    
    def list_windows(self) -> List[Tuple[str, str]]:
        """List all visible windows"""
        if not WINDOWS_TOOLS_AVAILABLE:
            return [("Error", "Windows tools not available")]
        
        windows = []
        
        def enum_handler(hwnd, results):
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                if window_text:
                    class_name = win32gui.GetClassName(hwnd)
                    results.append((window_text, class_name))
        
        win32gui.EnumWindows(enum_handler, windows)
        return sorted(windows)


def take_screenshot(
    filename: Optional[str] = None,
    output_dir: Optional[str] = None,
    **kwargs
) -> str:
    """Convenience function for taking a screenshot"""
    manager = ScreenshotManager(output_dir)
    return manager.take_screenshot(filename, **kwargs)


def main():
    """Main CLI interface for screenshot functionality"""
    parser = argparse.ArgumentParser(
        description='Advanced Screenshot Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python screenshot.py                          # Full screenshot
  python screenshot.py -f my_screen.png        # Custom filename
  python screenshot.py -w "Notepad"            # Capture specific window
  python screenshot.py -r 100 100 800 600     # Partial screenshot
  python screenshot.py -m 5 -i 3              # Multiple shots
  python screenshot.py --list-windows         # List available windows
        """
    )
    
    parser.add_argument('-f', '--filename', help='Output filename')
    parser.add_argument('-d', '--output-dir', default='screenshots', help='Output directory')
    parser.add_argument('-w', '--window', help='Capture specific window by title')
    parser.add_argument('-r', '--region', nargs=4, type=int, metavar=('X', 'Y', 'W', 'H'),
                       help='Capture region: x y width height')
    parser.add_argument('-q', '--quality', type=int, default=95, help='JPEG quality (1-100)')
    parser.add_argument('--format', default='PNG', choices=['PNG', 'JPEG', 'BMP'], 
                       help='Image format')
    parser.add_argument('-m', '--multiple', type=int, help='Capture multiple screenshots')
    parser.add_argument('-i', '--interval', type=int, default=2, 
                       help='Interval between multiple screenshots')
    parser.add_argument('--list-windows', action='store_true', help='List all windows')
    parser.add_argument('--test', action='store_true', help='Test screenshot functionality')
    
    args = parser.parse_args()
    
    # Create screenshot manager
    manager = ScreenshotManager(args.output_dir)
    
    try:
        if args.list_windows:
            print("\nAvailable Windows:")
            print("-" * 50)
            windows = manager.list_windows()
            for i, (title, class_name) in enumerate(windows[:20], 1):  # Limit to first 20
                print(f"{i:2d}. {title}")
                if class_name:
                    print(f"     Class: {class_name}")
            
            if len(windows) > 20:
                print(f"... and {len(windows) - 20} more windows")
        
        elif args.test:
            print("Testing screenshot functionality...")
            
            if not WINDOWS_TOOLS_AVAILABLE:
                print("[ERROR] Windows tools not available")
                print("   Install with: pip install pyautogui pywin32")
            else:
                print("[OK] Windows tools available")
            
            if not PIL_AVAILABLE:
                print("[ERROR] PIL/Pillow not available") 
                print("   Install with: pip install Pillow")
            else:
                print("[OK] PIL/Pillow available")
            
            # Test screenshot
            test_path = manager.take_screenshot("test_screenshot.png")
            if test_path and Path(test_path).exists():
                print(f"[OK] Test screenshot successful: {test_path}")
            else:
                print("[ERROR] Test screenshot failed")
        
        elif args.multiple:
            screenshots = manager.capture_multiple(
                count=args.multiple,
                interval=args.interval,
                prefix="batch"
            )
            print(f"\nCaptured {len(screenshots)} screenshots:")
            for path in screenshots:
                print(f"  • {path}")
        
        else:
            # Single screenshot
            region = tuple(args.region) if args.region else None
            
            path = manager.take_screenshot(
                filename=args.filename,
                region=region,
                window_title=args.window,
                quality=args.quality,
                format=args.format
            )
            
            if path:
                print(f"[OK] Screenshot saved successfully!")
                print(f"Location: {path}")
                
                # Show file info
                file_path = Path(path)
                if file_path.exists():
                    size_kb = file_path.stat().st_size / 1024
                    print(f"File size: {size_kb:.1f} KB")
                    
                    if PIL_AVAILABLE:
                        try:
                            with Image.open(file_path) as img:
                                print(f"Dimensions: {img.size[0]}x{img.size[1]} pixels")
                                print(f"Format: {img.format}")
                        except Exception:
                            pass
            else:
                print("[ERROR] Screenshot failed")
                sys.exit(1)
    
    except KeyboardInterrupt:
        print("\nScreenshot cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()