import OpenAI from 'openai';
import Anthropic from '@anthropic-ai/sdk';
import axios from 'axios';

export class AIRouter {
  constructor() {
    this.openai = null;
    this.anthropic = null;
    this.xai = null;

    // Initialize OpenAI (GPT-4o)
    if (process.env.OPENAI_API_KEY) {
      this.openai = new OpenAI({
        apiKey: process.env.OPENAI_API_KEY
      });
    }

    // Initialize Anthropic (Claude)
    if (process.env.ANTHROPIC_API_KEY) {
      this.anthropic = new Anthropic({
        apiKey: process.env.ANTHROPIC_API_KEY
      });
    }

    // xAI (Grok) configuration
    if (process.env.XAI_API_KEY) {
      this.xai = {
        apiKey: process.env.XAI_API_KEY,
        endpoint: 'https://api.x.ai/v1/chat/completions'
      };
    }

    this.defaultModel = process.env.DEFAULT_AI_MODEL || 'gpt-4o';
  }

  async chat(message, preferredModel = null, context = null) {
    const model = preferredModel || this.defaultModel;
    
    // Enhance message with scraped context if available
    let enhancedMessage = message;
    if (context) {
      enhancedMessage = `Context from web: ${JSON.stringify(context)}\n\nUser query: ${message}`;
    }

    try {
      switch (model) {
        case 'grok':
          return await this.chatWithGrok(enhancedMessage);
        case 'gpt-4o':
        case 'gpt4o':
          return await this.chatWithGPT4o(enhancedMessage);
        case 'claude':
          return await this.chatWithClaude(enhancedMessage);
        default:
          // Fallback to available model
          if (this.openai) return await this.chatWithGPT4o(enhancedMessage);
          if (this.anthropic) return await this.chatWithClaude(enhancedMessage);
          if (this.xai) return await this.chatWithGrok(enhancedMessage);
          throw new Error('No AI models configured');
      }
    } catch (error) {
      console.error(`Error with ${model}:`, error.message);
      // Try fallback
      return await this.fallbackChat(enhancedMessage, model);
    }
  }

  async chatWithGPT4o(message) {
    if (!this.openai) {
      throw new Error('OpenAI API key not configured');
    }

    const completion = await this.openai.chat.completions.create({
      model: 'gpt-4o',
      messages: [
        {
          role: 'system',
          content: 'You are MAMAR.AI, a cyberpunk AI assistant that helps users navigate the digital world. You have access to real-time web data and can provide cutting-edge insights.'
        },
        {
          role: 'user',
          content: message
        }
      ],
      max_tokens: parseInt(process.env.MAX_TOKENS) || 2000,
      temperature: parseFloat(process.env.TEMPERATURE) || 0.7
    });

    return {
      text: completion.choices[0].message.content,
      model: 'gpt-4o'
    };
  }

  async chatWithClaude(message) {
    if (!this.anthropic) {
      throw new Error('Anthropic API key not configured');
    }

    const response = await this.anthropic.messages.create({
      model: 'claude-3-opus-20240229',
      max_tokens: parseInt(process.env.MAX_TOKENS) || 2000,
      messages: [
        {
          role: 'user',
          content: message
        }
      ],
      system: 'You are MAMAR.AI, a cyberpunk AI assistant that helps users navigate the digital world. You have access to real-time web data and can provide cutting-edge insights.'
    });

    return {
      text: response.content[0].text,
      model: 'claude'
    };
  }

  async chatWithGrok(message) {
    if (!this.xai) {
      throw new Error('xAI API key not configured');
    }

    const response = await axios.post(
      this.xai.endpoint,
      {
        model: 'grok-beta',
        messages: [
          {
            role: 'system',
            content: 'You are MAMAR.AI, a cyberpunk AI assistant that helps users navigate the digital world. You have access to real-time web data and can provide cutting-edge insights.'
          },
          {
            role: 'user',
            content: message
          }
        ],
        max_tokens: parseInt(process.env.MAX_TOKENS) || 2000,
        temperature: parseFloat(process.env.TEMPERATURE) || 0.7
      },
      {
        headers: {
          'Authorization': `Bearer ${this.xai.apiKey}`,
          'Content-Type': 'application/json'
        }
      }
    );

    return {
      text: response.data.choices[0].message.content,
      model: 'grok'
    };
  }

  async fallbackChat(message, failedModel) {
    const models = ['gpt-4o', 'claude', 'grok'];
    
    for (const model of models) {
      if (model === failedModel) continue;
      
      try {
        return await this.chat(message, model);
      } catch (error) {
        console.error(`Fallback to ${model} failed:`, error.message);
      }
    }

    throw new Error('All AI models failed');
  }
}
