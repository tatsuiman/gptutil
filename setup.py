from setuptools import setup, find_packages

setup(
    name="gptutil",
    version="0.0.2",
    packages=find_packages(),
    install_requires=[
        "click",
        "openai",
        "tiktoken"
    ],
    entry_points={
        "console_scripts": [
            "gpt-ask=cli.ask:main",
            "gpt-image=cli.image:main",
        ],
    },
)
