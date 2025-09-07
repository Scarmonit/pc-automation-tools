
# SECURITY WARNING: Credentials should be set via environment variables
# Set LOGIN_EMAIL and LOGIN_PASSWORD environment variables before running
# Example: export LOGIN_EMAIL="your-email@example.com"
#          export LOGIN_PASSWORD="your-secure-password"
import os
#!/usr/bin/env python3
"""
Automated login script
"""

from playwright.sync_api import sync_playwright
import time

def auto_login(email, password, service_url):
    """Automate login to services"""
    
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        # Navigate to service
        page.goto(service_url)
        time.sleep(2)
        
        # Look for login/signup elements
        try:
            # Check for email field
            if page.locator('input[type="email"]').count() > 0:
                page.fill('input[type="email"]', email)
            elif page.locator('input[name="email"]').count() > 0:
                page.fill('input[name="email"]', email)
            elif page.locator('input[placeholder*="email" i]').count() > 0:
                page.fill('input[placeholder*="email" i]', email)
            
            # Check for password field
            if page.locator('input[type="password"]').count() > 0:
                page.fill('input[type="password"]', password)
            elif page.locator('input[name="password"]').count() > 0:
                page.fill('input[name="password"]', password)
            
            # Click login/submit button
            if page.locator('button:has-text("Login")').count() > 0:
                page.locator('button:has-text("Login")').click()
            elif page.locator('button:has-text("Sign in")').count() > 0:
                page.locator('button:has-text("Sign in")').click()
            elif page.locator('button[type="submit"]').count() > 0:
                page.locator('button[type="submit"]').click()
            
            # Wait for navigation
            time.sleep(5)
            
            # Check if need to create account
            if "sign up" in page.content().lower() or "create account" in page.content().lower():
                # Look for sign up link
                if page.locator('a:has-text("Sign up")').count() > 0:
                    page.locator('a:has-text("Sign up")').click()
                elif page.locator('a:has-text("Create account")').count() > 0:
                    page.locator('a:has-text("Create account")').click()
                
                time.sleep(2)
                
                # Fill signup form
                if page.locator('input[type="email"]').count() > 0:
                    page.fill('input[type="email"]', email)
                if page.locator('input[type="password"]').count() > 0:
                    page.fill('input[type="password"]', password)
                
                # Submit signup
                if page.locator('button:has-text("Sign up")').count() > 0:
                    page.locator('button:has-text("Sign up")').click()
                elif page.locator('button:has-text("Create")').count() > 0:
                    page.locator('button:has-text("Create")').click()
            
            print(f"Login/setup attempted for {service_url}")
            
            # Keep browser open for manual verification
            input("Press Enter to close browser...")
            
        except Exception as e:
            print(f"Error during automation: {e}")
        
        browser.close()

# Your credentials
email = os.getenv("LOGIN_EMAIL", "")
password = os.getenv("LOGIN_PASSWORD", "")

# Check which services might need login
services = [
    "http://localhost:3001",  # Flowise
    "http://localhost:3002",  # OpenHands
    "http://localhost:3003"   # Grafana
]

for service in services:
    print(f"\nChecking {service}...")
    auto_login(email, password, service)