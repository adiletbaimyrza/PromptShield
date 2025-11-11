# PromptShield
A web app for securely preparing content and code before sending to an LLM


# Frontend
make sure you have the latest stable version of node (v24.0.0) - best to install it using nvm ([see here](https://github.com/nvm-sh/nvm)). Also make sure you have npm installed as well.

```bash
# navigate from root
cd frontend
# install packages
npm install
# build frontend
npm run build

# use it only if you want to have a frontend server.
# Note: it is not configured to work with backend in this mode.
# So you can skip this command.
npm run dev
```

# Backend
make sure you have python and pip installed in your system.

```bash
# navigate from root
cd backend
# create a virtual env on your machine, and activate it
# example in linux:
python -m venv .venv & source .venv/bin/activate

# 

# install packages
pip install -r requirements.txt
# run locally
fastapi dev app/main.py
```

current endpoings:

- / - servers frontend static files
- /api - api endpoints
