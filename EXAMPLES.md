# MAMAR.AI Examples

This file contains examples of how to use MAMAR.AI in various scenarios.

## 1. Basic Chat Queries

### General Questions
```
User: What is artificial intelligence?
MAMAR.AI: Provides comprehensive explanation using the best available model
```

### Real-time Information (Best with Grok)
```
User: What are the latest developments in AI?
MAMAR.AI: Fetches and summarizes recent AI news
```

### Creative Tasks (Best with GPT-4o)
```
User: Write a cyberpunk short story about AI
MAMAR.AI: Creates an engaging creative narrative
```

### Code Analysis (Best with Claude)
```
User: Explain how async/await works in JavaScript
MAMAR.AI: Provides detailed technical explanation
```

## 2. Web Scraping Examples

### Scrape and Analyze
```
User: Analyze https://news.ycombinator.com
MAMAR.AI: Scrapes the page and provides insights about top stories
```

### Extract Information
```
User: What are the main points from https://example.com/article
MAMAR.AI: Extracts and summarizes key information
```

## 3. CLI Examples

### Interactive Mode
```bash
npm run cli

# Then type commands:
> What is quantum computing?
> model gpt-4o
> Tell me about blockchain
> scrape https://github.com/trending
> status
> exit
```

### Quick Commands
```bash
# Check system status
npm run cli
> status

# Switch models
> model grok
> What's happening in tech today?

# Web scraping
> scrape https://reddit.com/r/programming
```

## 4. API Integration Examples

### Node.js Integration

```javascript
import axios from 'axios';

async function chatWithMAMAR(message, model = null) {
  const response = await axios.post('http://localhost:3000/chat', {
    message,
    model
  });
  
  return response.data;
}

// Usage
const result = await chatWithMAMAR('Explain neural networks');
console.log(result.response);

// With specific model
const grokResult = await chatWithMAMAR('Latest AI news', 'grok');
console.log(grokResult.response);
```

### Python Integration

```python
import requests
import json

def chat_with_mamar(message, model=None):
    response = requests.post('http://localhost:3000/chat', 
        json={'message': message, 'model': model})
    return response.json()

# Usage
result = chat_with_mamar('What is machine learning?')
print(result['response'])

# With Claude for detailed analysis
analysis = chat_with_mamar('Analyze this algorithm complexity', 'claude')
print(analysis['response'])
```

### cURL Examples

```bash
# Basic chat
curl -X POST http://localhost:3000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello MAMAR.AI"}'

# With specific model
curl -X POST http://localhost:3000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain quantum computing", "model": "gpt-4o"}'

# Web scraping
curl -X POST http://localhost:3000/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# Check status
curl http://localhost:3000/status
```

## 5. Web Interface Usage

### Quick Start
1. Open http://localhost:3000
2. Select your preferred AI model (or use AUTO SELECT)
3. Type your message in the input field
4. Click "EXECUTE" or press Enter

### Model Selection
- **AUTO SELECT**: Let MAMAR.AI choose the best model
- **GROK**: Best for real-time, current events
- **GPT-4o**: Best for complex reasoning, creative tasks
- **CLAUDE**: Best for detailed analysis, code review

### Quick Commands
Use the sidebar buttons for common queries:
- **CAPABILITIES**: Learn what MAMAR.AI can do
- **LATEST NEWS**: Get current AI news
- **TECH QUERY**: Ask technical questions
- **CODE HELP**: Get coding assistance

## 6. Advanced Use Cases

### Research Assistant
```
User: Research the latest papers on transformer architectures and summarize key findings
MAMAR.AI: Uses multiple models and web scraping to provide comprehensive research summary
```

### Code Review
```
User: Review this code and suggest improvements:
[paste code here]
MAMAR.AI (Claude): Provides detailed code analysis and suggestions
```

### Content Creation
```
User: Create a blog post outline about cyberpunk aesthetics in modern design
MAMAR.AI (GPT-4o): Generates creative and structured outline
```

### Real-time Analysis
```
User: What's trending on Twitter about AI today?
MAMAR.AI (Grok): Provides up-to-date information about trending topics
```

## 7. Development Examples

### Custom Integration

```javascript
// Create a custom chatbot wrapper
class CustomMAMAR {
  constructor(baseUrl = 'http://localhost:3000') {
    this.baseUrl = baseUrl;
    this.history = [];
  }

  async chat(message, model = null) {
    const response = await fetch(`${this.baseUrl}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, model })
    });

    const data = await response.json();
    
    this.history.push({
      user: message,
      ai: data.response,
      model: data.model,
      timestamp: data.timestamp
    });

    return data;
  }

  getHistory() {
    return this.history;
  }
}

// Usage
const mamar = new CustomMAMAR();
await mamar.chat('Hello!');
await mamar.chat('Tell me about AI');
console.log(mamar.getHistory());
```

### Batch Processing

```javascript
async function processBatch(queries) {
  const results = [];
  
  for (const query of queries) {
    const response = await fetch('http://localhost:3000/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: query })
    });
    
    const data = await response.json();
    results.push({ query, answer: data.response });
  }
  
  return results;
}

// Process multiple queries
const queries = [
  'What is AI?',
  'Explain blockchain',
  'How does quantum computing work?'
];

const results = await processBatch(queries);
console.log(results);
```

## 8. Best Practices

### Choosing the Right Model

**Use Grok when:**
- Need real-time information
- Querying current events
- Want the latest news

**Use GPT-4o when:**
- Need creative output
- Complex reasoning required
- General-purpose queries

**Use Claude when:**
- Need detailed analysis
- Code review and explanation
- Research and technical writing

### Error Handling

```javascript
async function safeChat(message) {
  try {
    const response = await fetch('http://localhost:3000/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    
    if (!data.success) {
      console.error('Chat error:', data.error);
      return null;
    }

    return data.response;
  } catch (error) {
    console.error('Connection error:', error);
    return null;
  }
}
```

## 9. Tips and Tricks

1. **Be Specific**: Clear, specific questions get better answers
2. **Use Context**: Provide context for better understanding
3. **Try Different Models**: Different models excel at different tasks
4. **Combine Scraping**: Include URLs for real-time data
5. **Iterate**: Refine your queries based on responses

## 10. Troubleshooting

### No Response
- Check if server is running (`npm start`)
- Verify API keys are configured in `.env`
- Check console for error messages

### Slow Response
- Web scraping can be slow for large pages
- Complex queries take longer to process
- Consider using faster models (Grok, GPT-4o)

### Scraping Fails
- Some sites block scrapers
- Check if URL is accessible
- Respect robots.txt

---

For more examples and documentation, visit:
- GitHub: https://github.com/bloodbathwest-source/mamar-ai
- Website: https://mamar.ai
