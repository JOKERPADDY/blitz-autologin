import os
import sys
from playwright.sync_api import sync_playwright

def main():
    email = os.getenv("EMAIL")
    pas = os.getenv("PAS")

    if not email or not pas:
        print("ERROR: EMAIL or PAS environment variables are missing.")
        sys.exit(3)

    login_url = "https://blitz.cloud/login"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            print(f"Navigating to {login_url}...")
            page.goto(login_url, timeout=30000)

            # Check for CAPTCHA / 2FA on initial load
            content = page.content().lower()
            if any(term in content for term in ["captcha", "cf-turnstile", "g-recaptcha", "hcaptcha", "2fa", "two-factor"]):
                print("LOGIN_UNCONFIRMED: CAPTCHA or 2FA prompt detected on load.")
                browser.close()
                sys.exit(2)

            # Fill email field
            filled_email = False
            try:
                page.get_by_label("Email address").fill(email)
                filled_email = True
            except Exception:
                try:
                    page.fill('input[type="email"], input[name="email"]', email)
                    filled_email = True
                except Exception as e:
                    print(f"LOGIN_FAILED: Could not fill email field. {e}")
                    browser.close()
                    sys.exit(1)

            # Fill password field
            try:
                page.get_by_label("Password").fill(pas)
            except Exception:
                try:
                    page.fill('input[type="password"], input[name="password"]', pas)
                except Exception as e:
                    print(f"LOGIN_FAILED: Could not fill password field. {e}")
                    browser.close()
                    sys.exit(1)

            # Click Sign in button
            try:
                page.get_by_role("button", name="Sign in").click()
            except Exception:
                try:
                    page.click('button[type="submit"], input[type="submit"], button:has-text("Sign in")')
                except Exception as e:
                    print(f"LOGIN_FAILED: Could not click Sign in button. {e}")
                    browser.close()
                    sys.exit(1)

            # Wait for navigation/response
            page.wait_for_timeout(5000)
            current_url = page.url
            content_after = page.content().lower()

            # Check for CAPTCHA, 2FA, or security prompt after submission
            if any(term in content_after for term in ["captcha", "cf-turnstile", "g-recaptcha", "hcaptcha", "2fa", "verification code", "two-factor"]):
                print("LOGIN_UNCONFIRMED: CAPTCHA, 2FA, or verification prompt detected after submit.")
                browser.close()
                sys.exit(2)

            # Check if login form is gone and URL is on blitz.cloud domain
            email_input_visible = False
            try:
                email_input_visible = page.is_visible('input[type="email"], input[name="email"]')
            except Exception:
                pass

            if not email_input_visible and "blitz.cloud" in current_url and "/login" not in current_url:
                print("LOGIN_CONFIRMED")
                browser.close()
                sys.exit(0)

            # Check for explicit login error
            if any(term in content_after for term in ["invalid", "incorrect credentials", "wrong password"]) or email_input_visible:
                print("LOGIN_FAILED: Form still visible or login error detected.")
                browser.close()
                sys.exit(1)

            if "blitz.cloud" in current_url:
                print("LOGIN_CONFIRMED")
                browser.close()
                sys.exit(0)
            else:
                print("LOGIN_UNCONFIRMED: Unexpected domain or navigation outcome.")
                browser.close()
                sys.exit(2)

        except Exception as e:
            print(f"LOGIN_FAILED: Exception occurred during login flow. {e}")
            browser.close()
            sys.exit(1)

if __name__ == "__main__":
    main()
