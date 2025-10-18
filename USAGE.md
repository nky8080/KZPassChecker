# Usage Guide

*Read this in other languages: [日本語](USAGE.ja.md)*

This guide provides comprehensive usage instructions for the Bunka-no-Mori Cultural Pass Facility Agent.

## 🚀 Quick Start

### Basic Usage

Once deployed, you can interact with the agent using natural language queries about facility closure information.

### Example Queries

```
"Is the 21st Century Museum open on December 25th?"
"Which facilities are closed on January 1st?"
"Tell me about Kenrokuen Garden's operating hours for next Monday"
"Are there any temporary closures at Suzuki Daisetsu Museum this week?"
"What facilities can I visit on a Monday?"
```

## 🏛️ Facility Information

### Supported Facilities

The agent provides information for all 18 facilities covered by the Bunka-no-Mori Cultural Pass:

#### Museums and Cultural Centers

1. **Suzuki Daisetsu Museum** (鈴木大拙館)
   - Regular closure: Mondays (next weekday if holiday)
   - Special features: Philosophy and Zen culture

2. **21st Century Museum of Contemporary Art, Kanazawa** (金沢21世紀美術館)
   - Regular closure: Year-end/New Year only
   - Special features: Contemporary art exhibitions

3. **Ishikawa Museum of Living Crafts** (いしかわ生活工芸ミュージアム)
   - Regular closure: Irregular schedule
   - Special features: Traditional crafts and modern design

4. **National Museum of Modern Art, Tokyo (Crafts Gallery)** (国立工芸館)
   - Regular closure: Mondays (next weekday if holiday)
   - Special features: Traditional and contemporary crafts

#### Historic Sites and Traditional Architecture

5. **Samurai House Ruins Nomura-ke** (武家屋敷跡 野村家)
   - Regular closure: Year-end/New Year only
   - Special features: Edo period samurai residence

6. **National Important Cultural Property Seisonkaku** (国指定重要文化財 成巽閣)
   - Regular closure: Irregular schedule
   - Special features: Traditional Japanese architecture

#### Gardens and Parks

7. **Special Place of Scenic Beauty Kenrokuen Garden** (特別名勝 兼六園)
   - Regular closure: Open year-round
   - Special features: One of Japan's three most beautiful gardens

8. **Kanazawa Castle Park** (金沢城公園)
   - Regular closure: Open year-round
   - Special features: Historic castle grounds and reconstructed buildings

#### Specialized Museums

9. **Kanazawa Phonograph Museum** (金沢蓄音器館)
   - Regular closure: Mondays (next weekday if holiday)
   - Special features: Antique phonographs and music history

10. **Kanazawa Yasue Gold Leaf Museum** (金沢箔工芸館)
    - Regular closure: Mondays (next weekday if holiday)
    - Special features: Gold leaf crafts and techniques

### Closure Types Handled

The agent understands and reports various types of closures:

- **Regular weekly closures** (e.g., "Closed Mondays")
- **Holiday schedule variations** (e.g., "Open on holiday Mondays")
- **Temporary closures** for maintenance or special events
- **Exhibition changeover periods**
- **Seasonal closures** (rare, but some facilities have seasonal schedules)
- **Weather-related closures** (emergency situations)

## 💬 Query Patterns

### Date Formats

The agent accepts various date formats:

```
"December 25th"
"2024-12-25"
"next Monday"
"tomorrow"
"this weekend"
"January 1st, 2024"
```

### Facility References

You can refer to facilities in multiple ways:

```
# By full name
"21st Century Museum of Contemporary Art, Kanazawa"

# By common name
"21st Century Museum"

# By Japanese name
"金沢21世紀美術館"

# By category
"art museums"
"gardens"
"historic sites"
```

### Query Types

#### Single Facility Queries
```
"Is Suzuki Daisetsu Museum open on Monday?"
"What are the closure days for Kenrokuen Garden?"
```

#### Multiple Facility Queries
```
"Which museums are open on January 1st?"
"List all facilities closed on Mondays"
"What can I visit this weekend?"
```

#### Planning Queries
```
"Plan a visit for next Tuesday - which facilities are available?"
"I have three days in Kanazawa, what's the best schedule?"
```

## 🔍 Advanced Features

### Detailed Information Requests

```
"Tell me about temporary closures at all museums this month"
"Are there any special exhibitions affecting regular hours?"
"Which facilities have extended hours during holidays?"
```

### Comparative Queries

```
"Compare the opening schedules of art museums"
"Which facilities are most reliable for weekend visits?"
```

### Historical Information

```
"Has the 21st Century Museum been closed recently?"
"What were the closure patterns last month?"
```

## 📅 Planning Your Visit

### Best Practices

1. **Check Multiple Days**: Ask about several days to find the best visiting time
2. **Consider Alternatives**: If your preferred facility is closed, ask for similar options
3. **Plan for Holidays**: Japanese holidays can affect schedules significantly
4. **Check for Updates**: Ask about recent changes or temporary closures

### Sample Planning Conversation

```
User: "I'm visiting Kanazawa next Monday. What cultural facilities can I visit?"

Agent: "Next Monday, most facilities will be closed due to regular Monday closures. However, these facilities will be open:
- 21st Century Museum of Contemporary Art (open daily except year-end)
- Kenrokuen Garden (open year-round)
- Kanazawa Castle Park (open year-round)
- Samurai House Ruins Nomura-ke (open daily except year-end)

Would you like me to suggest an alternative day when more facilities are available?"

User: "What about Tuesday?"

Agent: "Tuesday is an excellent choice! All 18 facilities should be open, including:
- Suzuki Daisetsu Museum
- National Museum of Modern Art (Crafts Gallery)
- All the museums that close on Mondays
Plus all the facilities that are open on Mondays.

Would you like me to suggest a visiting route or provide more details about specific facilities?"
```

## 🛠️ Technical Usage

### API Integration

If you're integrating the agent into your own application:

```python
from agent import facility_agent

# Query the agent
response = facility_agent.query("Is the museum open tomorrow?")
print(response)
```

### Batch Queries

For multiple queries:

```python
queries = [
    "Suzuki Daisetsu Museum status for 2024-01-15",
    "21st Century Museum status for 2024-01-15",
    "Kenrokuen Garden status for 2024-01-15"
]

results = [facility_agent.query(q) for q in queries]
```

## 🔧 Troubleshooting

### Common Issues

#### "I don't have current information"
- The agent may not have recent data for a specific facility
- Try asking about a different date or facility
- Check if the facility website is accessible

#### Unclear responses
- Be more specific about the date and facility
- Use full facility names when possible
- Ask follow-up questions for clarification

#### Outdated information
- The agent scrapes real-time data, but websites may have delays
- For critical visits, consider calling the facility directly
- Report persistent inaccuracies as issues

### Getting Better Results

1. **Be specific**: Include exact dates and facility names
2. **Ask follow-ups**: Request clarification if needed
3. **Use context**: Mention your visit plans for better recommendations
4. **Check multiple sources**: For important visits, verify with official websites

## 📞 Support and Feedback

### Getting Help

- **Documentation**: Check [DEVELOPMENT.md](DEVELOPMENT.md) for technical details
- **Issues**: Report bugs or inaccuracies on GitHub
- **Feature Requests**: Suggest improvements via GitHub Issues

### Providing Feedback

Help improve the agent by reporting:
- Inaccurate closure information
- Facilities with changed schedules
- Suggestions for new features
- Usability improvements

## 🌟 Tips for Best Experience

1. **Plan Ahead**: Check schedules a few days before your visit
2. **Have Alternatives**: Always have backup plans for closed facilities
3. **Consider Seasons**: Some facilities may have seasonal variations
4. **Check Weather**: Outdoor facilities may close during severe weather
5. **Verify Critical Information**: For important visits, double-check with official sources

---

*Enjoy exploring Ishikawa Prefecture's rich cultural heritage with confidence!*