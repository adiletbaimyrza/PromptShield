## Installation

```bash
# Install all dependencies from root
pip install -r ../requirements.txt
```

## Start Backend

```bash

python extension_server.py
```

## Load Extension 

Chromium:
   - chrome://extensions/
   - Enter dev mode
   - Load unpackaged
   - Choose `extension` folder

Firefox:
   - about:debugging#/runtime/this-firefox
   - "Load Temporary Add-on"
   - Choose `manifest.json` in `extension` 