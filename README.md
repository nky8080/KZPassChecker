# Kanazawa Cultural Zone Pass Facility Checker

*Read this in other languages: [日本語](README.ja.md)*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Amazon Bedrock AgentCore](https://img.shields.io/badge/Amazon%20Bedrock-AgentCore-orange.svg)](https://aws.amazon.com/bedrock/)

An intelligent agent built with Amazon Bedrock AgentCore that provides closure information for cultural facilities covered by the Bunka-no-Mori Cultural Pass in Ishikawa Prefecture, Japan.

## 📋 Overview

This project is an AI agent that automatically retrieves and provides closure information for the 18 cultural facilities available through the Bunka-no-Mori Cultural Pass (https://odekakepass.hot-ishikawa.jp/) for specified dates. It scrapes the latest closure information in real-time from each facility's official website, providing accurate and reliable information.

### Key Features

- **Real-time Information Retrieval**: Automatically fetches the latest closure information from each facility's official website
- **Comprehensive Facility Coverage**: Supports all 18 facilities covered by the Bunka-no-Mori Cultural Pass
- **Multiple Closure Pattern Support**: Handles regular closures, temporary closures, exhibition changeover periods, holiday schedules, etc.
- **High Accuracy**: Uses optimized scraping techniques tailored for each facility
- **Cloud Deployment Ready**: Scalable operation with Amazon Bedrock AgentCore

## 🏛️ Supported Facilities

All 18 facilities available through the Bunka-no-Mori Cultural Pass:

1. **Suzuki Daisetsu Museum** - Closed Mondays (next weekday if Monday is a holiday)
2. **21st Century Museum of Contemporary Art, Kanazawa** - Closed only during year-end/New Year period
3. **Ishikawa Museum of Living Crafts** - Irregular closures
4. **Samurai House Ruins Nomura-ke** - Closed only during year-end/New Year period
5. **National Important Cultural Property Seisonkaku** - Irregular closures
6. **Ishikawa Prefectural Museum of History** - Irregular closures
7. **National Museum of Modern Art, Tokyo (Crafts Gallery)** - Closed Mondays (next weekday if Monday is a holiday)
8. **Special Place of Scenic Beauty Kenrokuen Garden** - Open year-round
9. **Kanazawa Castle Park** - Open year-round
10. **Maeda Tosanokami Family Museum** - Closed Mondays (open if Monday is a holiday)
11. **Kanazawa Phonograph Museum** - Closed Mondays (next weekday if Monday is a holiday)
12. **Kanazawa Yasue Gold Leaf Museum** - Closed Mondays (next weekday if Monday is a holiday)
13. **Ishikawa Prefectural Museum of Traditional Arts and Crafts** - Closed Thursdays (next weekday if Thursday is a holiday)
14. **Ishikawa Prefectural Noh Theater** - Irregular closures
15. **Kanazawa Noh Museum** - Closed Mondays (next weekday if Monday is a holiday)
16. **Ishikawa Prefectural Museum of Art** - Irregular closures
17. **Honda Museum** - Closed Mondays (next weekday if Monday is a holiday)
18. **Tokuda Shusei Memorial Museum** - Closed Mondays (next weekday if Monday is a holiday)

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- AWS account with Bedrock access
- Required Python packages (see `requirements.txt`)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/bunka-no-mori-facility-agent.git
cd bunka-no-mori-facility-agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure AWS credentials and region in `config.py`

4. Deploy to Amazon Bedrock AgentCore:
```bash
python deploy.py
```

### Usage

Query the agent about facility closure information:

```
"Is the 21st Century Museum open on December 25th?"
"Which facilities are closed on January 1st?"
"Tell me about Kenrokuen Garden's operating hours for next Monday"
```

## 🛠️ Technical Architecture

### Core Components

- **Agent Core**: Built with Amazon Bedrock AgentCore and Strands framework
- **Facility Scraper**: Custom scraping engine for each facility's website
- **Memory Integration**: Persistent knowledge storage with AgentCore Memory
- **Configuration Management**: Centralized facility and scraping configuration

### Supported Closure Types

- Regular weekly closures (e.g., Mondays)
- Holiday schedule variations
- Temporary closures for maintenance
- Exhibition changeover periods
- Special event closures
- Weather-related closures

## 📚 Documentation

- [Development Guide](DEVELOPMENT.md) - Setup and development instructions
- [Usage Guide](USAGE.md) - Detailed usage examples and API reference
- [Contributing Guide](CONTRIBUTING.md) - How to contribute to the project
- [Project Structure](PROJECT_STRUCTURE.md) - Codebase organization

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on:

- Code of conduct
- Development setup
- Submitting pull requests
- Reporting issues

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Ishikawa Prefecture for the Bunka-no-Mori Cultural Pass program
- All participating cultural facilities for providing public access to their information
- Amazon Web Services for the Bedrock AgentCore platform

## 📞 Support

For questions, issues, or suggestions:

- Open an Issue
- Check the [Documentation](DEVELOPMENT.md)
- Review [Usage Examples](USAGE.md)

---

*This agent helps visitors to Ishikawa Prefecture's cultural facilities by providing up-to-date closure information, making cultural exploration more convenient and enjoyable.*
