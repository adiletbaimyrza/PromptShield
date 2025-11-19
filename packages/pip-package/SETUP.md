1. create venv in pip-package/ directory
2. install deps via **pip install -r requirements.txt**
3. you can start coding inside src/pshield, PromptShield class inside phsield.py is the main class that will be imported in the projects


if you want to publish:

1. make sure you have installed all packages, and venv activated
2. choose the correct versioning, if you don't know about it read here https://py-pkgs.org/07-releasing-versioning.html
and change the version in pyproject.toml appropriately
3. run **python -m build**, it will create 2 files in dist/ directory
4. run **python3 -m twine upload --repository pypi dist/** it will ask for token API, ask Adilet for it, then pass it in the terminal
5. for the future: create .env file inside pip-package directory, and save token api there
6. congrats you published a new version of PromptShield



