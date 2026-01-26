# Deployment Protocol: SleepDetector on Hugging Face Spaces

## 1. Sync Changes with GitHub
Ensure your local changes are committed and pushed to your remote GitHub repository.

```bash
git add src/utils/sound.py requirements.txt packages.txt
git commit -m "chore: prepare for Hugging Face deployment (linux-compat)"
git push origin main
```

## 2. Create Hugging Face Space
1.  Log in to your [Hugging Face](https://huggingface.co/) account.
2.  Click **New Space**.
3.  **Owner**: Select your username.
4.  **Space Name**: `SleepDetector` (or your preferred name).
5.  **License**: `MIT` (optional but recommended).
6.  **SDK**: Select **Streamlit**.
7.  **Hardware**: `CPU basic` (Free) is sufficient for initial testing.
8.  Click **Create Space**.

## 3. Connect to GitHub (Mirroring/CI)
*Recommended for automatic updates.*

1.  In your new Space, go to **Settings**.
2.  Scroll to **Docker / CI**.
3.  Click **Connect a repository** or **Enable with Actions**.
4.  If using "Docker" mode or standard Streamlit, Hugging Face usually handles the build automatically if `requirements.txt` and `packages.txt` are present.
    *   **Note**: Using the default Streamlit SDK option is the easiest path. It automatically detects `packages.txt` for OS dependencies (like `libgl1`).

## 4. Environment Configuration
If your app requires secrets (e.g., API keys, though not currently used in this version):
1.  Go to **Settings** > **Variables and secrets**.
2.  Click **New secret** to add any environment variables.

## 5. Verify Deployment
1.  Go to the **App** tab.
2.  Wait for the "Building" status to change to "Running".
3.  Check the **Logs** tab if the build fails. Common errors often relate to missing `packages.txt` dependencies (e.g., `libGL.so`). We have already included `libgl1` to prevent this.
