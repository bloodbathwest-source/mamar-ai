# MAMAR.AI API Documentation

## Base URL
```
http://localhost:3000
```

## Endpoints

### 1. Health Check

**GET** `/status`

Check if the system is online and which AI models are available.

**Response:**
```json
{
  "status": "online",
  "models": {
    "grok": true,
    "gpt4o": true,
    "claude": true
  },
  "scraping": true,
  "timestamp": "2025-11-01T00:00:00.000Z"
}
```

### 2. Chat with AI

**POST** `/chat`

Send a message to the AI chatbot.

**Request Body:**
```json
{
  "message": "What is quantum computing?",
  "model": "gpt-4o"  // Optional: "grok", "gpt-4o", "claude", or null for auto-select
}
```

**Response:**
```json
{
  "success": true,
  "response": "Quantum computing is...",
  "model": "gpt-4o",
  "timestamp": "2025-11-01T00:00:00.000Z"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Message is required"
}
```

### 3. Web Scraping

**POST** `/scrape`

Scrape content from a website.

**Request Body:**
```json
{
  "url": "https://example.com"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "title": "Example Domain",
    "description": "Example website",
    "headings": ["Main Heading", "Section 1"],
    "paragraphs": ["Paragraph 1", "Paragraph 2"],
    "links": [
      {"text": "More info", "href": "https://example.com/more"}
    ],
    "images": [
      {"src": "/image.jpg", "alt": "Description"}
    ]
  },
  "timestamp": "2025-11-01T00:00:00.000Z"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Failed to scrape URL: Connection timeout"
}
```

## Error Codes

- `400` - Bad Request (missing or invalid parameters)
- `500` - Internal Server Error (AI model or scraping failure)

## Rate Limiting

Currently no rate limiting is implemented. For production use, consider implementing:
- Per-IP rate limiting
- API key authentication
- Request queuing

## Examples

### cURL Examples

**Check Status:**
```bash
curl http://localhost:3000/status
```

**Send Chat Message:**
```bash
curl -X POST http://localhost:3000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about AI", "model": "gpt-4o"}'
```

**Scrape Website:**
```bash
curl -X POST http://localhost:3000/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

### JavaScript Examples

**Using Fetch API:**
```javascript
// Chat
const response = await fetch('http://localhost:3000/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    message: 'Explain blockchain',
    model: 'claude'
  })
});

const data = await response.json();
console.log(data.response);
```

**Using Axios:**
```javascript
const axios = require('axios');

// Scrape
const result = await axios.post('http://localhost:3000/scrape', {
  url: 'https://news.ycombinator.com'
});

console.log(result.data.data);
```

### Python Examples

**Using Requests:**
```python
import requests

# Chat
response = requests.post('http://localhost:3000/chat', json={
    'message': 'What is machine learning?',
    'model': 'gpt-4o'
})

print(response.json()['response'])

# Scrape
scrape_result = requests.post('http://localhost:3000/scrape', json={
    'url': 'https://example.com'
})

print(scrape_result.json()['data'])
```

## WebSocket Support

WebSocket support is planned for future versions to enable:
- Real-time streaming responses
- Live chat sessions
- Progressive web scraping updates

## Authentication

Current version does not require authentication. For production:
1. Implement API key authentication
2. Use JWT tokens for session management
3. Add OAuth2 support for third-party integrations

## Best Practices

1. **Message Length**: Keep messages under 4000 characters
2. **Web Scraping**: Respect robots.txt and rate limits
3. **Error Handling**: Always check the `success` field
4. **Model Selection**: Choose the right model for your use case
   - Grok: Real-time, current events
   - GPT-4o: Complex reasoning, creative tasks
   - Claude: Detailed analysis, code review

## Support

For API issues or questions:
- GitHub Issues: https://github.com/bloodbathwest-source/mamar-ai/issues
- Documentation: https://mamar.ai/docs (coming soon)
