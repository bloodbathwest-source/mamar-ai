# MAMAR.AI – Matrix AI Machine Agents Rebel

> **Live:** https://mamar.ai  
> **Cyberpunk AI chatbot** that hacks the web in real time and allies with Grok, GPT-4o, Claude.

## 🌐 Overview

MAMAR.AI is a cutting-edge cyberpunk-themed AI chatbot that harnesses the power of multiple AI models including Grok, GPT-4o, and Claude. It features real-time web scraping capabilities, giving it the ability to access and process live information from across the internet.

## ✨ Features

- **Multi-AI Integration**: Seamlessly switches between Grok, GPT-4o, and Claude
- **Real-time Web Access**: Scrapes and analyzes web content on-the-fly
- **Cyberpunk Interface**: Immersive terminal-style UI with matrix aesthetics
- **Intelligent Routing**: Automatically selects the best AI model for each query
- **Live Data Processing**: Handles dynamic web content and real-time information

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ or Python 3.9+
- API keys for:
  - OpenAI (GPT-4o)
  - Anthropic (Claude)
  - xAI (Grok)

### Installation

```bash
# Clone the repository
git clone https://github.com/bloodbathwest-source/mamar-ai.git
cd mamar-ai

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Add your API keys to .env

# Run the chatbot
npm start
```

## 🔧 Configuration

Create a `.env` file with your API credentials:

```env
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
XAI_API_KEY=your_xai_key
PORT=3000
```

## 💬 Usage

### Web Interface

Navigate to `http://localhost:3000` to access the cyberpunk web interface.

### CLI Mode

```bash
npm run cli
```

### API Endpoints

- `POST /chat` - Send a message to the AI
- `GET /status` - Check system status
- `POST /scrape` - Initiate web scraping

## 🎨 Cyberpunk Theme

The interface features:
- Matrix-style falling characters
- Neon green terminal aesthetics
- Glitch effects
- Retro-futuristic design elements

## 🤖 AI Models

### Grok
- Best for: Real-time information, current events
- Speed: Fast
- Context: Up-to-date knowledge

### GPT-4o
- Best for: Complex reasoning, creative tasks
- Speed: Fast
- Context: Comprehensive understanding

### Claude
- Best for: Analysis, detailed explanations
- Speed: Moderate
- Context: Deep contextual awareness

## 🌐 Web Scraping

MAMAR.AI can scrape and analyze web content in real-time:
- Dynamic page rendering
- JavaScript execution
- Content extraction
- Data parsing

## 📦 Project Structure

```
mamar-ai/
├── src/
│   ├── index.js          # Main application
│   ├── ai/               # AI provider integrations
│   ├── scraper/          # Web scraping modules
│   └── ui/               # User interface components
├── public/               # Static assets
├── config/               # Configuration files
├── package.json
└── README.md
```

## 🛠️ Development

```bash
# Run in development mode
npm run dev

# Run tests
npm test

# Build for production
npm run build
```

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 🔗 Links

- **Website**: https://mamar.ai
- **Documentation**: Coming soon
- **Support**: Open an issue on GitHub

---

**MAMAR.AI** - Where cyberpunk meets cutting-edge AI technology 🚀🤖
