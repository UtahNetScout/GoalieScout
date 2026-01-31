# Contributing to Black Ops Goalie Scouting Platform

Thank you for your interest in contributing to the Black Ops Goalie Scouting Platform! This document provides guidelines for contributing to the project.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [How to Contribute](#how-to-contribute)
5. [Coding Standards](#coding-standards)
6. [Testing Guidelines](#testing-guidelines)
7. [Submitting Changes](#submitting-changes)

## Code of Conduct

We are committed to providing a welcoming and inclusive experience for everyone. We expect all contributors to:

- Be respectful and considerate
- Welcome newcomers and help them get started
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment tool (venv, virtualenv, or conda)

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/GoalieScout.git
   cd GoalieScout
   ```

3. Add the upstream repository:
   ```bash
   git remote add upstream https://github.com/UtahNetScout/GoalieScout.git
   ```

## Development Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install the package in development mode:
   ```bash
   pip install -e .
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

## How to Contribute

### Reporting Bugs

When reporting bugs, please include:

- A clear description of the issue
- Steps to reproduce the problem
- Expected behavior vs. actual behavior
- Your environment (OS, Python version, etc.)
- Any relevant error messages or logs

### Suggesting Enhancements

We welcome suggestions for new features or improvements! Please:

- Check if the feature has already been requested
- Clearly describe the feature and its benefits
- Provide examples of how it would be used
- Consider whether it aligns with the project's goals

### Contributing Code

1. **Find or Create an Issue**: Look for existing issues or create a new one describing what you plan to work on.

2. **Create a Branch**: Create a branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Changes**: Implement your changes following our coding standards.

4. **Test Your Changes**: Ensure all tests pass and add new tests for your changes.

5. **Commit Your Changes**: Write clear, descriptive commit messages:
   ```bash
   git commit -m "Add feature: brief description"
   ```

6. **Push to Your Fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Submit a Pull Request**: Open a PR against the main repository's `main` branch.

## Coding Standards

### Python Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use meaningful variable and function names
- Keep functions focused and concise
- Add docstrings to all functions, classes, and modules

### Example Function Documentation

```python
def analyze_goalie(profile: GoalieProfile, model: str = 'openai') -> AIAnalysis:
    """Analyze a goalie's performance using AI.
    
    Args:
        profile: The goalie profile to analyze
        model: AI model to use (openai, anthropic, ollama)
        
    Returns:
        AIAnalysis object with ratings and insights
        
    Raises:
        ValueError: If profile is invalid or model is unsupported
    """
    pass
```

### Import Organization

Organize imports in the following order:
1. Standard library imports
2. Third-party imports
3. Local application imports

```python
import os
from typing import Dict, List

import requests
from bs4 import BeautifulSoup

from goaliescout.data import GoalieProfile
```

## Testing Guidelines

### Writing Tests

- Write unit tests for all new functions and classes
- Use pytest for testing
- Aim for high test coverage (>80%)
- Test edge cases and error conditions

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=goaliescout

# Run specific test file
pytest tests/test_analytics.py
```

### Test Example

```python
def test_calculate_career_stats():
    """Test career statistics calculation."""
    profile = create_sample_profile()
    stats = GoalieAnalytics.calculate_career_stats(profile)
    
    assert stats['career_games'] > 0
    assert 0.0 <= stats['career_save_percentage'] <= 1.0
    assert stats['career_gaa'] >= 0.0
```

## Submitting Changes

### Pull Request Checklist

Before submitting a pull request, ensure:

- [ ] Code follows the project's style guidelines
- [ ] All tests pass
- [ ] New tests are added for new functionality
- [ ] Documentation is updated if needed
- [ ] Commit messages are clear and descriptive
- [ ] The PR description explains what changed and why

### Pull Request Description Template

```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Enhancement
- [ ] Documentation update

## Testing
Describe how you tested your changes

## Related Issues
Closes #issue_number
```

### Code Review Process

1. A maintainer will review your PR
2. Address any feedback or requested changes
3. Once approved, your PR will be merged

## Adding New AI Models

If you're adding support for a new AI model:

1. Create a new service class inheriting from `AIService`
2. Implement all required methods
3. Add configuration options to `.env.example`
4. Update documentation
5. Add tests for the new service

## Adding New Data Sources

When adding support for new data sources:

1. Create a new scraper class inheriting from `GoalieScraper`
2. Implement scraping logic with proper rate limiting
3. Add error handling and logging
4. Respect robots.txt and terms of service
5. Add tests with mock data

## Documentation

### Updating Documentation

- Keep README.md up to date
- Update docstrings when changing function signatures
- Add examples for new features
- Document configuration options

### Documentation Style

- Use clear, concise language
- Provide code examples where helpful
- Include screenshots for UI changes
- Keep formatting consistent

## Questions?

If you have questions about contributing:

- Open an issue with the "question" label
- Join our community discussions
- Review existing issues and PRs for examples

## License

By contributing to this project, you agree that your contributions will be licensed under the same license as the project.

## Recognition

Contributors will be recognized in our README.md and release notes. Thank you for helping make this project better!
