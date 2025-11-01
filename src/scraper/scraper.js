import axios from 'axios';
import * as cheerio from 'cheerio';

// Configuration constants
const SCRAPER_LIMITS = {
  HEADINGS: 10,
  PARAGRAPHS: 10,
  LINKS: 20,
  IMAGES: 10
};

export class WebScraper {
  constructor() {
    this.timeout = parseInt(process.env.SCRAPER_TIMEOUT) || 30000;
    this.userAgent = process.env.USER_AGENT || 'Mozilla/5.0 (compatible; MAMAR-AI/1.0)';
  }

  async scrape(url) {
    if (process.env.ENABLE_WEB_SCRAPING !== 'true') {
      throw new Error('Web scraping is disabled');
    }

    // Validate URL to prevent SSRF attacks
    try {
      const urlObj = new URL(url);
      
      // Only allow http and https protocols
      if (!['http:', 'https:'].includes(urlObj.protocol)) {
        throw new Error('Invalid URL protocol. Only HTTP and HTTPS are allowed');
      }
      
      // Block localhost and private IP ranges to prevent SSRF
      const hostname = urlObj.hostname.toLowerCase();
      if (hostname === 'localhost' || 
          hostname === '127.0.0.1' || 
          hostname.startsWith('192.168.') ||
          hostname.startsWith('10.') ||
          hostname.match(/^172\.(1[6-9]|2[0-9]|3[0-1])\./)) {
        throw new Error('Access to local/private networks is not allowed');
      }
    } catch (error) {
      throw new Error(`Invalid URL: ${error.message}`);
    }

    try {
      const response = await axios.get(url, {
        timeout: this.timeout,
        headers: {
          'User-Agent': this.userAgent
        }
      });

      const $ = cheerio.load(response.data);

      // Extract key information
      const data = {
        title: $('title').text().trim(),
        description: $('meta[name="description"]').attr('content') || '',
        headings: [],
        paragraphs: [],
        links: [],
        images: []
      };

      // Extract headings
      $('h1, h2, h3').each((i, elem) => {
        if (i < SCRAPER_LIMITS.HEADINGS) {
          data.headings.push($(elem).text().trim());
        }
      });

      // Extract paragraphs
      $('p').each((i, elem) => {
        if (i < SCRAPER_LIMITS.PARAGRAPHS) {
          const text = $(elem).text().trim();
          if (text.length > 20) {
            data.paragraphs.push(text);
          }
        }
      });

      // Extract links
      $('a[href]').each((i, elem) => {
        if (i < SCRAPER_LIMITS.LINKS) {
          const href = $(elem).attr('href');
          const text = $(elem).text().trim();
          if (href && text) {
            data.links.push({ text, href });
          }
        }
      });

      // Extract images
      $('img[src]').each((i, elem) => {
        if (i < SCRAPER_LIMITS.IMAGES) {
          const src = $(elem).attr('src');
          const alt = $(elem).attr('alt') || '';
          if (src) {
            data.images.push({ src, alt });
          }
        }
      });

      return data;
    } catch (error) {
      console.error('Scraping error:', error.message);
      throw new Error(`Failed to scrape ${url}: ${error.message}`);
    }
  }

  async scrapeIfNeeded(message) {
    // Check if message contains a URL
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    const urls = message.match(urlRegex);

    if (urls && urls.length > 0) {
      try {
        return await this.scrape(urls[0]);
      } catch (error) {
        console.error('Auto-scrape failed:', error.message);
        return null;
      }
    }

    return null;
  }

  async extractText(url) {
    const data = await this.scrape(url);
    
    // Combine all text content
    let text = `Title: ${data.title}\n\n`;
    
    if (data.description) {
      text += `Description: ${data.description}\n\n`;
    }
    
    if (data.headings.length > 0) {
      text += `Headings:\n${data.headings.join('\n')}\n\n`;
    }
    
    if (data.paragraphs.length > 0) {
      text += `Content:\n${data.paragraphs.join('\n\n')}`;
    }
    
    return text;
  }
}
