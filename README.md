# Blitz.cloud Automated Daily Login

Automated GitHub Actions workflow using Python + Playwright to perform daily logins on [blitz.cloud](https://blitz.cloud) to keep your account active and prevent inactive service shutdown.

---

## 🚀 Quick Setup Instructions

1. **Create Repository**: Create a new GitHub repository (e.g. `blitz-auto-login`).
2. **Push Files**: Push the contents of this project to your GitHub repository.
3. **Add Repository Secrets**:
   - Go to your repository **Settings** → **Secrets and variables** → **Actions**.
   - Click **New repository secret**.
   - Add **`EMAIL`**: Your Blitz.cloud account email address.
   - Add **`PAS`**: Your Blitz.cloud account password.
4. **Enable GitHub Actions**:
   - Go to the **Actions** tab in your GitHub repository and enable workflows.
   - Test by running **Actions** → **Daily Blitz Login** → **Run workflow**.

---

## 📊 Exit Codes Reference

| Exit Code | Output Message | Description |
| :---: | :--- | :--- |
| **`0`** | `LOGIN_CONFIRMED` | Successful login. The login form disappeared and navigation completed. |
| **`1`** | `LOGIN_FAILED` | Login failed. Credentials invalid, form remained visible, or element failed to click. |
| **`2`** | `LOGIN_UNCONFIRMED` | CAPTCHA, 2FA, or an unexpected page/domain was encountered. |
| **`3`** | `Missing environment variables` | `EMAIL` or `PAS` secrets are missing or empty. |

---

## ⚠️ Important Notes

> [!IMPORTANT]
> **GitHub Inactivity Rule**: GitHub automatically disables scheduled cron workflows after 60 days of repository inactivity. To keep it running continuously, commit to the repository or push a monthly heartbeat commit.

> [!WARNING]
> **CAPTCHA & 2FA**: Playwright cannot bypass CAPTCHAs (Cloudflare Turnstile / reCAPTCHA) or 2FA authentication prompts. Make sure 2FA and CAPTCHA restrictions are disabled on your Blitz.cloud account for automated logins to work.

> [!NOTE]
> **UI Updates**: If Blitz.cloud updates its login page layout or field labels, you may need to update the selectors in `login.py`.
