export const config = {
  ai: {
    models: {
      grok: {
        name: 'Grok',
        provider: 'xAI',
        endpoint: 'https://api.x.ai/v1/chat/completions',
        model: 'grok-beta',
        bestFor: ['real-time info', 'current events', 'news']
      },
      gpt4o: {
        name: 'GPT-4o',
        provider: 'OpenAI',
        model: 'gpt-4o',
        bestFor: ['complex reasoning', 'creative tasks', 'analysis']
      },
      claude: {
        name: 'Claude',
        provider: 'Anthropic',
        model: 'claude-3-opus-20240229',
        bestFor: ['detailed explanations', 'code analysis', 'research']
      }
    },
    defaults: {
      maxTokens: 2000,
      temperature: 0.7
    }
  },
  
  scraper: {
    timeout: 30000,
    maxRetries: 3,
    userAgent: 'Mozilla/5.0 (compatible; MAMAR-AI/1.0)',
    limits: {
      headings: 10,
      paragraphs: 10,
      links: 20,
      images: 10
    }
  },
  
  server: {
    port: 3000,
    host: 'localhost'
  },
  
  cyberpunk: {
    theme: {
      primaryColor: '#00ff41',
      backgroundColor: '#0a0e27',
      terminalBackground: '#0d1117'
    },
    effects: {
      matrixRain: true,
      glitchEffect: true,
      neonGlow: true
    }
  }
};

export default config;
