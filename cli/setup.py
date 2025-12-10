from setuptools import setup

setup(
    name='pshield-cli',
    version='1.0.0',
    py_modules=['cli'],
    install_requires=['pshield>=0.0.4'],
    entry_points={
        'console_scripts': [
            'pshield=cli:main',
        ],
    },
    author='PromptShield',
    description='CLI tool to protect sensitive data in prompts',
    python_requires='>=3.7',
)
