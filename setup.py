"""Setup script for the Adversarial Knowledge Cartographer."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="adversarial-knowledge-cartographer",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="An autonomous research system that builds knowledge graphs of conflicting viewpoints",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/adversarial-knowledge-cartographer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Researchers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "hypothesis>=6.100.0",
            "pytest-mock>=3.14.0",
            "pytest-asyncio>=0.23.0",
        ],
    },
)
