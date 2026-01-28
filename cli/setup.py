from setuptools import setup, find_packages

setup(
    name='pshield-cli',
    version='1.0.0',
    py_modules=['pshield_cli'],
    install_requires=['pshield>=0.0.4'],
    entry_points={
        'console_scripts': [
            'pshield=pshield_cli:main',
        ],
    },
    author='PromptShield',
    description='CLI tool to protect sensitive data in prompts',
    python_requires='>=3.7',
)
