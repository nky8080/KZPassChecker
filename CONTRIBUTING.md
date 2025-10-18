# Contributing to Bunka-no-Mori Cultural Pass Facility Agent

*Read this in other languages: [日本語](CONTRIBUTING.ja.md)*

Thank you for your interest in contributing to the Bunka-no-Mori Cultural Pass Facility Agent! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Issues

Before creating an issue, please:

1. **Search existing issues** to avoid duplicates
2. **Use the issue template** if available
3. **Provide detailed information** including:
   - Steps to reproduce the problem
   - Expected vs actual behavior
   - Environment details (Python version, OS, etc.)
   - Error messages or logs

### Suggesting Enhancements

We welcome suggestions for new features or improvements:

1. **Check existing feature requests** first
2. **Describe the use case** clearly
3. **Explain the expected benefit** to users
4. **Consider implementation complexity**

### Code Contributions

#### Development Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/bunka-no-mori-facility-agent.git
   cd bunka-no-mori-facility-agent
   ```

3. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

#### Making Changes

1. **Follow the coding standards**:
   - Use Python PEP 8 style guidelines
   - Add docstrings to functions and classes
   - Include type hints where appropriate
   - Keep functions focused and modular

2. **Test your changes**:
   - Ensure existing functionality still works
   - Add tests for new features
   - Test with multiple facilities if applicable

3. **Update documentation**:
   - Update README.md if needed
   - Add or update docstrings
   - Update USAGE.md for new features

#### Submitting Changes

1. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add: Brief description of your changes"
   ```

2. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create a Pull Request**:
   - Use a clear, descriptive title
   - Describe what changes you made and why
   - Reference any related issues
   - Include screenshots if applicable

## 🏗️ Development Guidelines

### Code Style

- **Python Style**: Follow PEP 8 guidelines
- **Naming Conventions**: Use descriptive variable and function names
- **Comments**: Write clear, concise comments for complex logic
- **Error Handling**: Include appropriate error handling and logging

### Facility Scraper Development

When adding support for new facilities or updating existing scrapers:

1. **Study the facility's website structure**
2. **Implement robust scraping logic** that handles:
   - Different page layouts
   - Temporary changes in website structure
   - Network timeouts and errors
3. **Test thoroughly** with various dates and scenarios
4. **Document the scraping approach** in code comments

### Testing

- **Manual Testing**: Test with real facility websites
- **Edge Cases**: Consider holidays, maintenance periods, etc.
- **Error Scenarios**: Test network failures, parsing errors
- **Date Handling**: Test with various date formats and edge cases

## 🌐 Internationalization

### Language Support

- **Primary Language**: English (for international accessibility)
- **Secondary Language**: Japanese (for local users)
- **Documentation**: Maintain both English and Japanese versions

### Adding Translations

1. **Create `.ja.md` versions** of documentation files
2. **Keep content synchronized** between language versions
3. **Use appropriate cultural context** for each language
4. **Test with native speakers** when possible

## 🔒 Security Considerations

### Responsible Disclosure

If you discover security vulnerabilities:

1. **Do not create public issues** for security problems
2. **Contact maintainers privately** first
3. **Provide detailed information** about the vulnerability
4. **Allow time for fixes** before public disclosure

### Scraping Ethics

- **Respect robots.txt** files
- **Implement reasonable delays** between requests
- **Handle rate limiting** gracefully
- **Monitor for website changes** that might indicate scraping issues

## 📋 Pull Request Checklist

Before submitting a pull request, ensure:

- [ ] Code follows the project's style guidelines
- [ ] Changes have been tested thoroughly
- [ ] Documentation has been updated if necessary
- [ ] Commit messages are clear and descriptive
- [ ] No sensitive information (API keys, credentials) is included
- [ ] Changes are focused and atomic (one feature per PR)

## 🎯 Priority Areas for Contribution

We especially welcome contributions in these areas:

1. **Facility Coverage**: Adding support for new cultural facilities
2. **Scraping Reliability**: Improving robustness of existing scrapers
3. **Error Handling**: Better error messages and recovery mechanisms
4. **Documentation**: Improving user guides and API documentation
5. **Testing**: Adding comprehensive test coverage
6. **Performance**: Optimizing scraping speed and resource usage

## 📞 Getting Help

If you need help with contributing:

- **Check the documentation**: [DEVELOPMENT.md](DEVELOPMENT.md) and [USAGE.md](USAGE.md)
- **Open a discussion**: Use GitHub Discussions for questions
- **Join the community**: Connect with other contributors

## 🙏 Recognition

Contributors will be recognized in:

- **README.md acknowledgments**
- **Release notes** for significant contributions
- **GitHub contributor statistics**

Thank you for helping make cultural exploration in Ishikawa Prefecture more accessible and enjoyable!

---

*By contributing to this project, you agree to abide by our code of conduct and licensing terms.*