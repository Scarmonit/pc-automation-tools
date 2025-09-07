#!/usr/bin/env python3
"""
Automated GPU Platform Setup and Management
Automates everything possible for setting up free GPU platforms
"""

import os
import subprocess
import webbrowser
import time
import requests
import json
from pathlib import Path

class GPUPlatformAutomator:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.config_file = self.base_dir / "gpu_config.json"
        self.config = self.load_config()
        
    def load_config(self):
        """Load or create configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        else:
            return {
                "user_email": "scarmonit@gmail.com",
                "phone_number": "330-242-9760",
                "platforms": {
                    "kaggle": {"setup": False, "api_key": "", "username": ""},
                    "lightning": {"setup": False, "credits": 0},
                    "colab": {"setup": False},
                    "paperspace": {"setup": False, "api_key": ""}
                }
            }
    
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def print_header(self, title):
        """Print formatted header"""
        print("\n" + "="*60)
        print(f"🚀 {title}")
        print("="*60)
    
    def open_signup_pages(self):
        """Automatically open all signup pages"""
        self.print_header("OPENING SIGNUP PAGES")
        
        urls = {
            "Kaggle": "https://www.kaggle.com/account/login?phase=startSignInTab&returnUrl=%2F",
            "Lightning AI": "https://lightning.ai/",
            "Google Colab": "https://colab.research.google.com/",
            "Paperspace": "https://console.paperspace.com/signup"
        }
        
        print("Opening signup pages in your browser...")
        for platform, url in urls.items():
            print(f"📱 Opening {platform}...")
            webbrowser.open(url)
            time.sleep(2)  # Stagger opening to prevent overwhelming browser
        
        print("\n✅ All signup pages opened!")
        print("📋 Manual Steps Required:")
        print("   1. Sign up with: scarmonit@gmail.com")
        print("   2. Verify phone: 330-242-9760")
        print("   3. Complete any required verifications")
        
        input("\n⏸️  Press Enter when you've completed all signups...")
    
    def setup_kaggle_api(self):
        """Setup Kaggle API for automation"""
        self.print_header("KAGGLE API SETUP")
        
        print("To automate Kaggle, we need API credentials:")
        print("1. Go to https://www.kaggle.com/me/account")
        print("2. Scroll to 'API' section")
        print("3. Click 'Create New Token'")
        print("4. Download kaggle.json file")
        
        kaggle_path = Path.home() / ".kaggle"
        kaggle_path.mkdir(exist_ok=True)
        
        print(f"\n📁 Place kaggle.json in: {kaggle_path}")
        
        if input("Have you placed kaggle.json? (y/n): ").lower() == 'y':
            try:
                import kaggle
                print("✅ Kaggle API configured successfully!")
                self.config["platforms"]["kaggle"]["setup"] = True
                return True
            except Exception as e:
                print(f"❌ Kaggle API setup failed: {e}")
                return False
        return False
    
    def install_dependencies(self):
        """Install required Python packages"""
        self.print_header("INSTALLING DEPENDENCIES")
        
        packages = [
            "torch",
            "tensorflow", 
            "numpy",
            "requests",
            "selenium",
            "kaggle",
            "paperspace"
        ]
        
        for package in packages:
            print(f"📦 Installing {package}...")
            try:
                subprocess.run([
                    "pip", "install", package, "-q"
                ], check=True)
                print(f"✅ {package} installed")
            except subprocess.CalledProcessError:
                print(f"❌ Failed to install {package}")
    
    def create_test_notebooks(self):
        """Create test notebooks for each platform"""
        self.print_header("CREATING TEST NOTEBOOKS")
        
        # Kaggle notebook
        kaggle_notebook = {
            "title": "GPU Performance Test",
            "code_file": "gpu_performance_test.py",
            "language": "python",
            "kernel_type": "notebook",
            "is_private": True,
            "enable_gpu": True,
            "enable_internet": True
        }
        
        notebooks_dir = self.base_dir / "notebooks"
        notebooks_dir.mkdir(exist_ok=True)
        
        # Create Kaggle notebook JSON
        with open(notebooks_dir / "kaggle_notebook.json", 'w') as f:
            json.dump(kaggle_notebook, f, indent=2)
        
        # Create Jupyter notebook for other platforms
        notebook_content = {
            "cells": [
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "# GPU Performance Test - Auto Generated\n",
                        f"exec(open('{self.base_dir / 'gpu_performance_test.py'}').read())"
                    ]
                }
            ],
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                }
            },
            "nbformat": 4,
            "nbformat_minor": 4
        }
        
        with open(notebooks_dir / "gpu_test.ipynb", 'w') as f:
            json.dump(notebook_content, f, indent=2)
        
        print("✅ Test notebooks created!")
        print(f"📁 Location: {notebooks_dir}")
    
    def create_automation_scripts(self):
        """Create platform-specific automation scripts"""
        self.print_header("CREATING AUTOMATION SCRIPTS")
        
        scripts_dir = self.base_dir / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        
        # Browser automation script
        browser_script = '''
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

def auto_kaggle_notebook():
    driver = webdriver.Chrome()  # Make sure chromedriver is installed
    try:
        driver.get("https://www.kaggle.com/code")
        time.sleep(3)
        
        # Click "New Notebook"
        new_notebook = driver.find_element(By.XPATH, "//button[contains(text(), 'New Notebook')]")
        new_notebook.click()
        time.sleep(2)
        
        # Enable GPU
        settings = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Settings')]")
        settings.click()
        time.sleep(1)
        
        gpu_toggle = driver.find_element(By.XPATH, "//input[@type='checkbox' and contains(@id, 'gpu')]")
        if not gpu_toggle.is_selected():
            gpu_toggle.click()
        
        print("✅ Kaggle notebook with GPU created!")
        
    finally:
        input("Press Enter to close browser...")
        driver.quit()

if __name__ == "__main__":
    auto_kaggle_notebook()
'''
        
        with open(scripts_dir / "browser_automation.py", 'w') as f:
            f.write(browser_script)
        
        print("✅ Automation scripts created!")
    
    def create_monitoring_dashboard(self):
        """Create a monitoring dashboard for GPU usage"""
        self.print_header("CREATING MONITORING DASHBOARD")
        
        dashboard_script = '''
import time
import json
from datetime import datetime
import os

class GPUUsageMonitor:
    def __init__(self):
        self.usage_log = "gpu_usage_log.json"
        self.load_usage_data()
    
    def load_usage_data(self):
        if os.path.exists(self.usage_log):
            with open(self.usage_log, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {
                "kaggle": {"hours_used": 0, "hours_remaining": 30},
                "lightning": {"hours_used": 0, "hours_remaining": 22},
                "colab": {"hours_used": 0, "hours_remaining": 12},
                "last_reset": datetime.now().strftime("%Y-%m-%d")
            }
    
    def save_usage_data(self):
        with open(self.usage_log, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def log_session(self, platform, duration_hours):
        self.data[platform]["hours_used"] += duration_hours
        self.data[platform]["hours_remaining"] -= duration_hours
        self.save_usage_data()
        print(f"✅ Logged {duration_hours}h on {platform}")
    
    def show_dashboard(self):
        print("\\n" + "="*50)
        print("📊 GPU USAGE DASHBOARD")
        print("="*50)
        
        for platform, data in self.data.items():
            if platform != "last_reset":
                used = data["hours_used"]
                remaining = data["hours_remaining"]
                total = used + remaining
                percentage = (used / total) * 100 if total > 0 else 0
                
                print(f"{platform.upper()}: {used:.1f}h used / {total:.1f}h total ({percentage:.1f}%)")
                print("█" * int(percentage/2) + "░" * (50 - int(percentage/2)))
                print()

if __name__ == "__main__":
    monitor = GPUUsageMonitor()
    monitor.show_dashboard()
'''
        
        with open(self.base_dir / "gpu_monitor.py", 'w') as f:
            f.write(dashboard_script)
        
        print("✅ Monitoring dashboard created!")
    
    def run_full_automation(self):
        """Run the complete automation process"""
        self.print_header("STARTING FULL GPU AUTOMATION")
        
        print("🤖 This will automate:")
        print("   • Opening signup pages")
        print("   • Installing dependencies") 
        print("   • Creating test notebooks")
        print("   • Setting up automation scripts")
        print("   • Creating monitoring tools")
        
        if input("\n Continue? (y/n): ").lower() != 'y':
            return
        
        # Step 1: Open signup pages
        self.open_signup_pages()
        
        # Step 2: Install dependencies
        self.install_dependencies()
        
        # Step 3: Setup APIs (where possible)
        self.setup_kaggle_api()
        
        # Step 4: Create test materials
        self.create_test_notebooks()
        self.create_automation_scripts()
        self.create_monitoring_dashboard()
        
        # Step 5: Save configuration
        self.save_config()
        
        self.print_header("AUTOMATION COMPLETE!")
        print("🎉 Setup completed successfully!")
        print("\n📋 Next Steps:")
        print("   1. Complete manual signups in opened browser tabs")
        print("   2. Run 'python gpu_monitor.py' to track usage")
        print("   3. Use created notebooks for testing")
        print("   4. Run 'python scripts/browser_automation.py' for Kaggle")
        
        print(f"\n📁 All files created in: {self.base_dir}")

def main():
    automator = GPUPlatformAutomator()
    automator.run_full_automation()

if __name__ == "__main__":
    main()