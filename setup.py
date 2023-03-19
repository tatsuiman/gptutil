from setuptools import setup, find_packages

setup(
    name="gptutil",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "click",
        "tiktoken",
        "langchain",
        "prompt_toolkit"
    ],
    package_data={"gptutil": ["example/*.yaml"]},
    entry_points={
        "console_scripts": [
            "gpt-ask=gptutil.ask:main",
            "gpt-image=gptutil.image:main",
            "gpt-interact=gptutil.interact:main",
        ],
    },
)
