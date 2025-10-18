# Development Guide

*Read this in other languages: [日本語](DEVELOPMENT.ja.md)*

This guide provides comprehensive information for developers working on the Bunka-no-Mori Cultural Pass Facility Agent.

## 🛠️ Development Environment Setup

### Prerequisites

- **Python 3.9+**: Required for modern async/await syntax and type hints
- **AWS Account**: With Bedrock service access
- **Git**: For version control
- **Code Editor**: VS Code, PyCharm, or similar with Python support

### Local Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/bunka-no-mori-facility-agent.git
   cd bunka-no-mori-facility-agent
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv .venv
   
   # On Windows
   .venv\Scripts\activate
   
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure AWS credentials**:
   ```bash
   aws configure
   # Or set environment variables:
   # export AWS_ACCESS_KEY_ID=your_access_key
   # export AWS_SECRET_ACCESS_KEY=your_secret_key
   # export AWS_DEFAULT_REGION=us-east-1
   ```

## 🏗️ Project Architecture

### Core Components

```
├── agent.py              # Main AgentCore application
├── facility_scraper.py   # Web scraping engine
├── config.py            # Configuration management
├── deploy.py            # Deployment utilities
└── setup.py             # Package configuration
```

### Key Technologies

- **Amazon Bedrock AgentCore**: AI agent runtime platform
- **Strands Framework**: Agent development framework
- **BeautifulSoup4**: HTML parsing for web scraping
- **Requests**: HTTP client for web requests
- **Docker**: Containerization for deployment

## 🔧 Configuration

### Environment Variables

Create a `.env` file (not tracked in git) with:

```bash
# AWS Configuration
AWS_REGION=us-east-1
MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0

# Development Settings
DEBUG=true
LOG_LEVEL=INFO

# Optional: Custom endpoints
BEDROCK_ENDPOINT_URL=https://bedrock-runtime.us-east-1.amazonaws.com
```

### Facility Configuration

Facilities are configured in `config.py`:

```python
FACILITIES = {
    "suzuki_daisetsu": {
        "name": "Suzuki Daisetsu Museum",
        "url": "https://www.kanazawa-museum.jp/daisetsu/",
        "scraper_type": "standard",
        "regular_closure": "monday",
        "holiday_handling": "next_weekday"
    },
    # ... more facilities
}
```

## 🕷️ Web Scraping Development

### Adding New Facilities

1. **Research the facility website**:
   - Identify closure information location
   - Understand the HTML structure
   - Check for dynamic content loading

2. **Implement scraper method**:
   ```python
   def scrape_facility_name(self, date_str: str) -> dict:
       """
       Scrape closure information for Facility Name
       
       Args:
           date_str: Date in YYYY-MM-DD format
           
       Returns:
           dict: Closure information with status and reason
       """
       try:
           response = self.session.get(facility_url, timeout=10)
           soup = BeautifulSoup(response.content, 'html.parser')
           
           # Implement facility-specific parsing logic
           closure_info = self._parse_closure_info(soup, date_str)
           
           return {
               'is_closed': closure_info['closed'],
               'reason': closure_info['reason'],
               'confidence': closure_info['confidence']
           }
       except Exception as e:
           return self._handle_scraping_error(e, 'facility_name')
   ```

3. **Add to facility registry**:
   ```python
   # In config.py
   FACILITIES['new_facility'] = {
       'name': 'New Facility Name',
       'url': 'https://facility-website.com',
       'scraper_method': 'scrape_new_facility'
   }
   ```

### Scraping Best Practices

- **Respect robots.txt**: Check and follow website policies
- **Implement delays**: Add reasonable delays between requests
- **Handle errors gracefully**: Network timeouts, parsing errors
- **Cache responses**: Avoid repeated requests for same data
- **User-Agent rotation**: Use appropriate user-agent strings

### Testing Scrapers

```python
# Test individual facility scraper
python -c "
from facility_scraper import FacilityScraper
scraper = FacilityScraper()
result = scraper.scrape_suzuki_daisetsu('2024-01-15')
print(result)
"
```

## 🤖 Agent Development

### Agent Structure

The main agent is built using the Strands framework:

```python
from strands import Agent, tool

agent = Agent(
    name="facility_closure_agent",
    instructions="You are an expert on cultural facility information...",
    model=MODEL_ID
)

@tool
def check_facility_closure(date: str, facility: str = None) -> str:
    """Check if facilities are closed on a specific date"""
    # Implementation
```

### Adding New Tools

1. **Define the tool function**:
   ```python
   @tool
   def new_tool_function(param1: str, param2: int = None) -> str:
       """
       Tool description for the agent
       
       Args:
           param1: Description of parameter
           param2: Optional parameter description
           
       Returns:
           str: Description of return value
       """
       # Implementation
   ```

2. **Register with agent**:
   ```python
   agent.add_tool(new_tool_function)
   ```

### Memory Integration

The agent uses AgentCore Memory for persistent knowledge:

```python
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig

memory_config = AgentCoreMemoryConfig(
    memory_id="facility-closure-memory",
    retrieval_config=RetrievalConfig(
        max_results=10,
        score_threshold=0.7
    )
)
```

## 🧪 Testing

### Manual Testing

Test the agent with various queries:

```bash
# Test basic functionality
python agent.py

# Example queries:
# "Is the 21st Century Museum open tomorrow?"
# "Which facilities are closed on January 1st?"
# "Tell me about Kenrokuen Garden's hours"
```

### Automated Testing

Create test scripts for critical functionality:

```python
# test_scrapers.py
import unittest
from facility_scraper import FacilityScraper

class TestFacilityScrapers(unittest.TestCase):
    def setUp(self):
        self.scraper = FacilityScraper()
    
    def test_suzuki_daisetsu_scraper(self):
        result = self.scraper.scrape_suzuki_daisetsu('2024-01-15')
        self.assertIn('is_closed', result)
        self.assertIn('reason', result)
```

## 🚀 Deployment

### Local Development Deployment

```bash
# Deploy to AgentCore development environment
python deploy.py --environment dev
```

### Production Deployment

```bash
# Deploy to production
python deploy.py --environment prod --validate
```

### Docker Deployment

```bash
# Build container
docker build -t facility-agent .

# Run locally
docker run -p 8000:8000 facility-agent
```

## 🔍 Debugging

### Common Issues

1. **Scraping Failures**:
   - Check website structure changes
   - Verify network connectivity
   - Review rate limiting

2. **Agent Response Issues**:
   - Check model configuration
   - Verify tool function signatures
   - Review memory integration

3. **Deployment Problems**:
   - Validate AWS credentials
   - Check region configuration
   - Verify AgentCore permissions

### Debugging Tools

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Test individual components
from facility_scraper import FacilityScraper
scraper = FacilityScraper()
scraper.debug_mode = True
```

## 📊 Performance Optimization

### Scraping Performance

- **Concurrent requests**: Use asyncio for parallel scraping
- **Caching**: Implement response caching
- **Connection pooling**: Reuse HTTP connections

### Agent Performance

- **Memory optimization**: Efficient memory usage patterns
- **Response caching**: Cache frequent queries
- **Tool optimization**: Optimize tool execution time

## 🔒 Security Considerations

### Scraping Security

- **Rate limiting**: Respect website rate limits
- **User-Agent**: Use appropriate identification
- **Error handling**: Don't expose internal errors

### Agent Security

- **Input validation**: Validate all user inputs
- **Output sanitization**: Clean agent responses
- **Credential management**: Secure AWS credential handling

## 📚 Additional Resources

- [Amazon Bedrock AgentCore Documentation](https://docs.aws.amazon.com/bedrock/)
- [Strands Framework Guide](https://strands-docs.example.com)
- [Web Scraping Best Practices](https://scraping-guide.example.com)
- [Python Async Programming](https://docs.python.org/3/library/asyncio.html)

## 🤝 Getting Help

- **Documentation**: Check this guide and README.md
- **Issues**: Open GitHub issues for bugs
- **Discussions**: Use GitHub Discussions for questions
- **Community**: Join the developer community

---

*Happy coding! Thank you for contributing to making cultural exploration more accessible.*