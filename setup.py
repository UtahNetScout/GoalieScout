"""Setup configuration for Black Ops Goalie Scouting Platform."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="goaliescout",
    version="0.1.0",
    author="Black Ops Goalie Scouting Platform Team",
    description="AI-driven hockey goalie scouting and analysis platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Sports/Analytics",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "openai>=1.0.0",
        "anthropic>=0.7.0",
        "click>=8.1.0",
        "rich>=13.0.0",
        "python-dotenv>=1.0.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "scipy>=1.11.0",
        "sqlalchemy>=2.0",
        "alembic>=1.12.0",
        "markdown>=3.5.0",
        "jinja2>=3.1.0",
        "tenacity>=8.0.0",
        "pydantic>=2.0.0",
        "apscheduler>=3.10.0",
        "aiohttp>=3.13.3",
        "fuzzywuzzy>=0.18.0",
        "python-Levenshtein>=0.21.0",
    ],
    entry_points={
        "console_scripts": [
            "goaliescout=goaliescout.cli:main",
        ],
    },
)
