import os
import sys
from playwright.sync_api import sync_playwright

def main():
    email = os.getenv("EMAIL")
    pas = os.getenv("PAS")
    app_url = os.getenv("APP_URL", "https://movie-box.joke.blitz.cloud/")

    if not email or not pas:
        print("ERROR: EMAIL or PAS environment variables are missing.")
        sys.exit(3)

    login_url = "https://blitz.cloud/login"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Use standard desktop Chrome user agent
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            print(f"Navigating to {login_url}...")
            page.goto(login_url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)

            print(f"Initial Page Title: '{page.title()}', URL: '{page.url}'")

            # Check if active 2FA input box or active Cloudflare challenge iframe is visible on load
            two_fa_visible = page.is_visible('input[name="code"], input[name="otp"], input[autocomplete="one-time-code"]')
            captcha_iframe_visible = page.is_visible('iframe[src*="challenges.cloudflare.com"], iframe[src*="recaptcha"], iframe[src*="hcaptcha"]')

            if two_fa_visible or captcha_iframe_visible:
                print("LOGIN_UNCONFIRMED: Active CAPTCHA or 2FA prompt visible on load.")
                browser.close()
                sys.exit(2)

            # Fill email field
            filled_email = False
            for selector in ['input[type="email"]', 'input[name="email"]', 'input[id*="email"]', 'input[placeholder*="email" i]']:
                if page.is_visible(selector):
                    page.fill(selector, email)
                    filled_email = True
                    break

            if not filled_email:
                try:
                    page.get_by_label("Email address").fill(email)
                    filled_email = True
                except Exception:
                    pass

            if not filled_email:
                print("LOGIN_FAILED: Could not locate visible email field.")
                browser.close()
                sys.exit(1)

            # Fill password field
            filled_pas = False
            for selector in ['input[type="password"]', 'input[name="password"]', 'input[id*="password"]']:
                if page.is_visible(selector):
                    page.fill(selector, pas)
                    filled_pas = True
                    break

            if not filled_pas:
                try:
                    page.get_by_label("Password").fill(pas)
                    filled_pas = True
                except Exception:
                    pass

            if not filled_pas:
                print("LOGIN_FAILED: Could not locate visible password field.")
                browser.close()
                sys.exit(1)

            # Click Sign in button
            clicked = False
            for selector in ['button[type="submit"]', 'input[type="submit"]', 'button:has-text("Sign in")', 'button:has-text("Log in")']:
                if page.is_visible(selector):
                    page.click(selector)
                    clicked = True
                    break

            if not clicked:
                try:
                    page.get_by_role("button", name="Sign in").click()
                    clicked = True
                except Exception:
                    pass

            if not clicked:
                print("LOGIN_FAILED: Could not locate visible Sign in button.")
                browser.close()
                sys.exit(1)

            # Wait for navigation/response
            page.wait_for_timeout(6000)
            current_url = page.url
            page_title = page.title()
            print(f"Post-submit Page Title: '{page_title}', URL: '{current_url}'")

            # Check if 2FA code prompt appeared after submission
            if page.is_visible('input[name="code"], input[name="otp"], input[autocomplete="one-time-code"]'):
                print("LOGIN_UNCONFIRMED: 2FA prompt detected after submission.")
                browser.close()
                sys.exit(2)

            # Check if email input is still visible
            email_input_visible = False
            try:
                email_input_visible = page.is_visible('input[type="email"], input[name="email"]')
            except Exception:
                pass

            # Wake up the app container by opening the App URL in the authenticated browser session
            if app_url:
                print(f"Navigating to App URL to wake app container: {app_url}...")
                try:
                    page.goto(app_url, timeout=30000)
                    page.wait_for_timeout(5000)
                    print(f"App Page Title: '{page.title()}', Final URL: '{page.url}'")
                except Exception as e:
                    print(f"Warning: Exception while opening App URL: {e}")

            # Check for success conditions:
            # 1. URL changed away from /login to dashboard/apps/home
            # 2. Or login form is no longer visible on blitz.cloud
            if "blitz.cloud" in current_url and "/login" not in current_url and not email_input_visible:
                print("LOGIN_CONFIRMED")
                browser.close()
                sys.exit(0)

            # Check for error text displayed on the login page
            visible_text = page.inner_text("body").lower() if page.is_visible("body") else ""
            if any(err in visible_text for err in ["invalid email or password", "incorrect credentials", "wrong password", "invalid credentials"]):
                print("LOGIN_FAILED: Invalid credentials error displayed on page.")
                browser.close()
                sys.exit(1)

            if not email_input_visible and "blitz.cloud" in current_url:
                print("LOGIN_CONFIRMED")
                browser.close()
                sys.exit(0)

            if email_input_visible:
                print("LOGIN_FAILED: Login form still visible after submit.")
                browser.close()
                sys.exit(1)

            print("LOGIN_UNCONFIRMED: Unexpected page state or domain.")
            browser.close()
            sys.exit(2)

        except Exception as e:
            print(f"LOGIN_FAILED: Exception occurred during login flow. {e}")
            browser.close()
            sys.exit(1)

if __name__ == "__main__":
    main()
