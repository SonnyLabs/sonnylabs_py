from setuptools import setup, find_packages

# Read the contents of your README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sonnylabs",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
    ],
    description="Python client for the SonnyLabs AI Security Scanner - Test your AI applications for prompt injection vulnerabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="SonnyLabs",
    author_email="liana@sonnylabs.ai",
    url="https://github.com/SonnyLabs/sonnylabs_py",
    project_urls={
        "Bug Tracker": "https://github.com/SonnyLabs/sonnylabs_py/issues",
        "Documentation": "https://github.com/SonnyLabs/sonnylabs_py#readme",
        "Source Code": "https://github.com/SonnyLabs/sonnylabs_py",
        "Homepage": "https://sonnylabs.ai",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Security",
        "Topic :: Software Development :: Testing",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    keywords="ai security prompt injection vulnerability scanner cybersecurity testing",
)