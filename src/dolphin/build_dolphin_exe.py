#!/usr/bin/env python3
"""
Build Dolphin GUI as standalone .exe
Creates a single executable file
"""

import subprocess
import sys
import os
from pathlib import Path


def install_pyinstaller():
    """Install PyInstaller if not present"""
    try:
        import PyInstaller
        print("[+] PyInstaller already installed")
        return True
    except ImportError:
        print("[*] Installing PyInstaller...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                         check=True, capture_output=True)
            print("[+] PyInstaller installed successfully")
            return True
        except Exception as e:
            print(f"[-] Failed to install PyInstaller: {e}")
            print("[!] Please install manually: pip install pyinstaller")
            return False


def create_spec_file():
    """Create a spec file for better control"""
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['dolphin_gui.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['tkinter', 'subprocess', 'threading', 'queue'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DolphinSecurityAssistant',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='dolphin.ico'  # Optional icon
)
"""
    
    spec_path = Path("dolphin_gui.spec")
    spec_path.write_text(spec_content)
    print(f"[+] Created spec file: {spec_path}")
    return spec_path


def create_icon():
    """Create a simple icon for the exe"""
    # Create a basic .ico file using Python
    icon_code = '''
import sys
from pathlib import Path

# Try to create an icon if PIL is available
try:
    from PIL import Image, ImageDraw
    
    # Create a simple dolphin-themed icon
    img = Image.new('RGBA', (64, 64), color=(0, 120, 200, 255))
    draw = ImageDraw.Draw(img)
    
    # Draw a simple dolphin shape
    draw.ellipse([10, 20, 54, 44], fill=(255, 255, 255, 255))
    draw.polygon([(54, 32), (60, 20), (60, 44)], fill=(255, 255, 255, 255))
    
    # Save as ICO
    img.save('dolphin.ico', format='ICO', sizes=[(64, 64)])
    print("[+] Created icon file: dolphin.ico")
    
except ImportError:
    print("[!] PIL not available, skipping icon creation")
    # Create empty file so build doesn't fail
    Path('dolphin.ico').touch()
'''
    
    # Run icon creation
    exec(icon_code)


def build_exe():
    """Build the executable"""
    print("\n[*] Building executable...")
    print("[!] This may take 1-2 minutes...\n")
    
    # Build command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",  # Single file
        "--windowed",  # No console
        "--name", "DolphinSecurityAssistant",
        "--distpath", ".",  # Output to current directory
        "--clean",  # Clean build
        "--noupx",  # Don't use UPX compression (more stable)
        "dolphin_gui.py"
    ]
    
    try:
        # Run PyInstaller
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[+] Build successful!")
            
            # Check if exe was created
            exe_path = Path("DolphinSecurityAssistant.exe")
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"[+] Created: {exe_path}")
                print(f"[+] Size: {size_mb:.1f} MB")
                return True
            else:
                print("[-] Exe file not found after build")
                return False
        else:
            print(f"[-] Build failed:\n{result.stderr}")
            return False
            
    except Exception as e:
        print(f"[-] Build error: {e}")
        return False


def cleanup():
    """Clean up build files"""
    print("\n[*] Cleaning up build files...")
    
    # Remove build directories
    dirs_to_remove = ['build', '__pycache__']
    for dir_name in dirs_to_remove:
        dir_path = Path(dir_name)
        if dir_path.exists():
            import shutil
            shutil.rmtree(dir_path)
            print(f"[+] Removed {dir_name}/")
    
    # Remove spec file
    spec_file = Path("dolphin_gui.spec")
    if spec_file.exists():
        spec_file.unlink()
        print("[+] Removed spec file")


def create_launcher_script():
    """Create a batch file to launch the exe"""
    launcher = '''@echo off
title Dolphin Security Assistant
echo Starting Dolphin Security Assistant...
echo.

if exist DolphinSecurityAssistant.exe (
    DolphinSecurityAssistant.exe
) else (
    echo [ERROR] DolphinSecurityAssistant.exe not found!
    echo Please run build_dolphin_exe.py first
    pause
)
'''
    
    launcher_path = Path("Launch_Dolphin.bat")
    launcher_path.write_text(launcher)
    print(f"[+] Created launcher: {launcher_path}")


def main():
    """Main build process"""
    print("="*60)
    print("DOLPHIN GUI EXECUTABLE BUILDER")
    print("="*60)
    
    # Step 1: Install PyInstaller
    if not install_pyinstaller():
        return
    
    # Step 2: Check if GUI script exists
    gui_path = Path("dolphin_gui.py")
    if not gui_path.exists():
        print("[-] dolphin_gui.py not found!")
        return
    
    # Step 3: Create icon
    try:
        create_icon()
    except:
        print("[!] Could not create icon, continuing without it")
    
    # Step 4: Build exe
    if build_exe():
        # Step 5: Create launcher
        create_launcher_script()
        
        # Step 6: Cleanup
        cleanup()
        
        print("\n" + "="*60)
        print("BUILD COMPLETE!")
        print("="*60)
        print("\n[+] Executable created: DolphinSecurityAssistant.exe")
        print("[+] You can now:")
        print("    1. Double-click DolphinSecurityAssistant.exe")
        print("    2. Or run Launch_Dolphin.bat")
        print("\n[!] The exe can be moved to any folder and will work")
        print("[!] Make sure Ollama is installed on the target system")
    else:
        print("\n[-] Build failed. Check error messages above.")


if __name__ == "__main__":
    main()