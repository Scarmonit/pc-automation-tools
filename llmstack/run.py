#!/usr/bin/env python3
"""
Quick launcher for llmstack project modules
"""

import sys
import subprocess
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))


def main():
    print("=" * 60)
    print("LLMSTACK - AI Platform Launcher")
    print("=" * 60)
    print("\nAvailable Options:")
    print("1. List all modules")
    print("2. Run security scanner")
    print("3. Launch Dolphin GUI")
    print("4. Start monitoring")
    print("5. Run health check")
    print("6. Install dependencies")
    print("0. Exit")
    
    while True:
        print("\n" + "-" * 40)
        choice = input("Select option (0-6): ").strip()
        
        if choice == "0":
            print("Exiting...")
            break
        elif choice == "1":
            subprocess.run([sys.executable, "main.py", "list"])
        elif choice == "2":
            print("\nSecurity Scanner Options:")
            print("a. Web scanner")
            print("b. API scanner")
            sub_choice = input("Select (a/b): ").strip().lower()
            if sub_choice == "a":
                subprocess.run([sys.executable, "main.py", "security", "--action", "webscan"])
            elif sub_choice == "b":
                subprocess.run([sys.executable, "main.py", "security", "--action", "apiscan"])
        elif choice == "3":
            subprocess.run([sys.executable, "main.py", "dolphin", "--action", "gui"])
        elif choice == "4":
            subprocess.run([sys.executable, "main.py", "monitoring"])
        elif choice == "5":
            if Path("health_check.py").exists():
                subprocess.run([sys.executable, "health_check.py"])
            else:
                print("Health check script not found!")
        elif choice == "6":
            print("Installing dependencies...")
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        else:
            print("Invalid option!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {e}")