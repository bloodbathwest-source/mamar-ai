import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';
import { AIRouter } from './ai/router.js';
import { WebScraper } from './scraper/scraper.js';

// Load environment variables
dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(express.static(path.join(__dirname, '../public')));

// Initialize AI Router and Web Scraper
const aiRouter = new AIRouter();
const webScraper = new WebScraper();

// Routes
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '../public/index.html'));
});

app.post('/chat', async (req, res) => {
  try {
    const { message, model } = req.body;
    
    if (!message) {
      return res.status(400).json({ error: 'Message is required' });
    }

    // Check if web scraping is needed
    let scrapedData = null;
    if (message.toLowerCase().includes('search') || message.toLowerCase().includes('latest')) {
      // Extract URL if present or perform generic search
      scrapedData = await webScraper.scrapeIfNeeded(message);
    }

    // Get AI response
    const response = await aiRouter.chat(message, model, scrapedData);
    
    res.json({
      success: true,
      response: response.text,
      model: response.model,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Chat error:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

app.get('/status', (req, res) => {
  res.json({
    status: 'online',
    models: {
      grok: process.env.ENABLE_GROK === 'true',
      gpt4o: process.env.ENABLE_GPT4O === 'true',
      claude: process.env.ENABLE_CLAUDE === 'true'
    },
    scraping: process.env.ENABLE_WEB_SCRAPING === 'true',
    timestamp: new Date().toISOString()
  });
});

app.post('/scrape', async (req, res) => {
  try {
    const { url } = req.body;
    
    if (!url) {
      return res.status(400).json({ error: 'URL is required' });
    }

    const data = await webScraper.scrape(url);
    
    res.json({
      success: true,
      data,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Scrape error:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   ███╗   ███╗ █████╗ ███╗   ███╗ █████╗ ██████╗         ║
║   ████╗ ████║██╔══██╗████╗ ████║██╔══██╗██╔══██╗        ║
║   ██╔████╔██║███████║██╔████╔██║███████║██████╔╝        ║
║   ██║╚██╔╝██║██╔══██║██║╚██╔╝██║██╔══██║██╔══██╗        ║
║   ██║ ╚═╝ ██║██║  ██║██║ ╚═╝ ██║██║  ██║██║  ██║        ║
║   ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝        ║
║                                                           ║
║          Matrix AI Machine Agents Rebel                   ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

🚀 Server running at http://localhost:${PORT}
🤖 AI Models: Grok, GPT-4o, Claude
🌐 Web Scraping: ${process.env.ENABLE_WEB_SCRAPING === 'true' ? 'Enabled' : 'Disabled'}

Ready to hack the matrix...
  `);
});

export default app;
