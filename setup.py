from setuptools import setup, find_packages

setup(
    name="workflow-orchestrator",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "asyncio",
        "typing-extensions>=4.0.0",
    ],
    extras_require={
        "test": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-mock>=3.10.0",
        ]
    },
    python_requires=">=3.8",
)