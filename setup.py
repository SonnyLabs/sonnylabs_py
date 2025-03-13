from setuptools import setup, find_packages

setup(
    name="sonnylabs-py",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
    ],
    description="Python client for the SonnyLabs Security API",
    author="SonnyLabs",
    author_email="liana@sonnylabs.ai",
)