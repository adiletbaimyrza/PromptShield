## Installation

```bash
# Install all dependencies from root
pip install -r ../requirements.txt
```

## Start Backend

```bash
python extension_server.py
# Server runs on http://localhost:5050
```

**Note:** Port 5000 is reserved by macOS AirPlay Receiver, so we use port 5050.

## Load Extension 

### Opera / Chrome / Chromium:
   - Go to `opera://extensions/` or `chrome://extensions/`
   - Enable "Developer mode" (toggle in top right)
   - Click "Load unpacked"
   - Select the `extension` folder
   - **Important:** After any manifest.json changes, click "Reload" on the extension

### Firefox:
   - Go to `about:debugging#/runtime/this-firefox`
   - Click "Load Temporary Add-on"
   - Select `manifest.json` in the `extension` folder

## Usage

1. Make sure the backend server is running (`python extension_server.py`)
2. Click the PromptShield extension icon in your browser
3. Enter text with sensitive data (names, emails, amounts, etc.)
4. Click "Anonymize"
5. Hover over placeholders to see original values
6. Click placeholders to toggle between anonymized and original
7. Click "Copy to Clipboard" to copy the protected text 