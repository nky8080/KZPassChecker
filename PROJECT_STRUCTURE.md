# Project Structure

*Read this in other languages: [日本語](PROJECT_STRUCTURE.ja.md)*

## Directory Structure

```
bunka-no-mori-facility-agent/
├── agent.py                    # Main AgentCore application
├── facility_scraper.py         # Facility information scraping engine
├── config.py                   # Configuration file
├── deploy.py                   # Deployment script
├── setup.py                    # Setup script
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git exclusion settings
├── .bedrock_agentcore.yaml     # AgentCore configuration
├── Dockerfile                  # Docker configuration
├── .dockerignore               # Docker exclusion settings
├── LICENSE                     # MIT License
├── README.md                   # Project overview (English)
├── README.ja.md                # Project overview (Japanese)
├── CONTRIBUTING.md             # Contributing guidelines (English)
├── CONTRIBUTING.ja.md          # Contributing guidelines (Japanese)
├── DEVELOPMENT.md              # Development guide (English)
├── DEVELOPMENT.ja.md           # Development guide (Japanese)
├── USAGE.md                    # Usage guide (English)
├── USAGE.ja.md                 # Usage guide (Japanese)
├── PROJECT_STRUCTURE.md        # This file (English)
├── PROJECT_STRUCTURE.ja.md     # This file (Japanese)
├── FINAL_VERIFICATION_SUMMARY.md # Security audit summary
├── cleanup_verification_report.md # Cleanup verification report
└── .kiro/                      # Kiro IDE specifications
    └── specs/
        └── github-publication-prep/
            ├── requirements.md
            ├── design.md
            └── tasks.md
```

## File Descriptions

### Core Application Files

- **agent.py**: Main intelligent agent built with Amazon Bedrock AgentCore and Strands framework
- **facility_scraper.py**: Web scraping engine that retrieves closure information from 18 cultural facilities' official websites
- **config.py**: Configuration file containing facility information, AWS settings, and scraping configurations

### Deployment and Infrastructure

- **deploy.py**: Automated deployment script for AWS AgentCore
- **setup.py**: Local development environment setup script
- **.bedrock_agentcore.yaml**: AgentCore platform configuration file
- **Dockerfile**: Container configuration for deployment
- **.dockerignore**: Docker build exclusion settings

### Configuration and Dependencies

- **requirements.txt**: Python dependencies (optimized for production)
- **.gitignore**: Git exclusion settings (optimized for Python development)
- **LICENSE**: MIT License for open source distribution

### Documentation (Bilingual)

#### English Documentation (Primary)
- **README.md**: Project overview and quick start guide
- **CONTRIBUTING.md**: Guidelines for contributing to the project
- **DEVELOPMENT.md**: Comprehensive development guide
- **USAGE.md**: Detailed usage instructions and API reference
- **PROJECT_STRUCTURE.md**: This project structure documentation

#### Japanese Documentation (Secondary)
- **README.ja.md**: Japanese version of project overview
- **CONTRIBUTING.ja.md**: Japanese version of contributing guidelines
- **DEVELOPMENT.ja.md**: Japanese version of development guide
- **USAGE.ja.md**: Japanese version of usage instructions
- **PROJECT_STRUCTURE.ja.md**: Japanese version of this documentation

### Quality Assurance and Verification

- **FINAL_VERIFICATION_SUMMARY.md**: Comprehensive security audit and cleanup summary
- **cleanup_verification_report.md**: Detailed verification report of cleanup process

### Development Specifications

- **.kiro/specs/**: Kiro IDE specification files for structured development
  - **requirements.md**: Feature requirements specification
  - **design.md**: Technical design document
  - **tasks.md**: Implementation task breakdown

## Development Workflow

### 1. Local Development Setup
```bash
python setup.py  # Setup development environment
pip install -r requirements.txt  # Install dependencies
```

### 2. Testing and Development
```bash
python agent.py  # Run local testing
# Test individual components as needed
```

### 3. Deployment
```bash
python deploy.py  # Deploy to AWS AgentCore
```

### 4. Monitoring
- Use CloudWatch dashboards for monitoring
- Check AgentCore logs for performance metrics

## Architecture Principles

### ✅ Best Practices Compliance

- **Flat Structure**: Optimized for AgentCore applications
- **Configuration Separation**: Clear separation of concerns
- **Proper Exclusions**: Comprehensive .gitignore and .dockerignore
- **Dependency Management**: Clear and optimized requirements
- **Comprehensive Documentation**: Bilingual documentation support
- **Automated Deployment**: Streamlined deployment process
- **Security Audited**: Thoroughly reviewed for security compliance

### 🌐 International Accessibility

- **Primary Language**: English for international developers
- **Secondary Language**: Japanese for local context and users
- **Cross-Language Navigation**: Easy switching between language versions
- **Cultural Context**: Maintains Japanese cultural facility context while being internationally accessible

### 🔒 Security and Quality

- **Security Audited**: All files reviewed and cleaned for public release
- **No Sensitive Data**: All credentials and sensitive information removed
- **Production Ready**: Optimized for production deployment
- **Open Source Compliant**: MIT License for community contribution

## Technology Stack

### Core Technologies
- **Amazon Bedrock AgentCore**: AI agent runtime platform
- **Strands Framework**: Agent development framework
- **Python 3.9+**: Primary programming language
- **BeautifulSoup4**: HTML parsing for web scraping
- **Requests**: HTTP client library

### Infrastructure
- **AWS Bedrock**: AI model hosting
- **Docker**: Containerization
- **CloudWatch**: Monitoring and logging

### Development Tools
- **Kiro IDE**: Structured development environment
- **Git**: Version control
- **GitHub**: Repository hosting and collaboration

---

*This structure supports both local development and cloud deployment while maintaining high code quality and international accessibility.*