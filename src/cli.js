import chalk from 'chalk';
import inquirer from 'inquirer';
import dotenv from 'dotenv';
import { AIRouter } from './ai/router.js';
import { WebScraper } from './scraper/scraper.js';

dotenv.config();

const aiRouter = new AIRouter();
const webScraper = new WebScraper();

console.log(chalk.green(`
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
║                  CLI Interface                            ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
`));

console.log(chalk.cyan('Welcome to MAMAR.AI - Cyberpunk AI CLI'));
console.log(chalk.gray('Type "exit" to quit, "help" for commands\n'));

async function chat() {
  const answers = await inquirer.prompt([
    {
      type: 'input',
      name: 'message',
      message: chalk.green('You:'),
      validate: (input) => {
        if (!input.trim()) {
          return 'Please enter a message';
        }
        return true;
      }
    }
  ]);

  const message = answers.message.trim();

  if (message.toLowerCase() === 'exit') {
    console.log(chalk.yellow('\nExiting MAMAR.AI. Stay cyberpunk! 🤖\n'));
    process.exit(0);
  }

  if (message.toLowerCase() === 'help') {
    console.log(chalk.cyan(`
Available Commands:
  - exit          Exit the CLI
  - help          Show this help message
  - model [name]  Switch AI model (grok, gpt-4o, claude)
  - scrape [url]  Scrape a website
  - status        Show system status

Just type your message to chat with MAMAR.AI!
    `));
    return chat();
  }

  if (message.toLowerCase().startsWith('model ')) {
    const model = message.substring(6).trim();
    console.log(chalk.yellow(`Switching to ${model}...\n`));
    // Model switching would be implemented here
    return chat();
  }

  if (message.toLowerCase().startsWith('scrape ')) {
    const url = message.substring(7).trim();
    try {
      console.log(chalk.yellow('Scraping...'));
      const data = await webScraper.scrape(url);
      console.log(chalk.green('\nScraped Data:'));
      console.log(chalk.white(JSON.stringify(data, null, 2)));
    } catch (error) {
      console.log(chalk.red(`\nError: ${error.message}`));
    }
    console.log('');
    return chat();
  }

  if (message.toLowerCase() === 'status') {
    console.log(chalk.cyan(`
System Status:
  - Grok:   ${process.env.ENABLE_GROK === 'true' ? '✓' : '✗'}
  - GPT-4o: ${process.env.ENABLE_GPT4O === 'true' ? '✓' : '✗'}
  - Claude: ${process.env.ENABLE_CLAUDE === 'true' ? '✓' : '✗'}
  - Scraping: ${process.env.ENABLE_WEB_SCRAPING === 'true' ? '✓' : '✗'}
    `));
    return chat();
  }

  try {
    console.log(chalk.yellow('MAMAR.AI is thinking...'));
    
    const scrapedData = await webScraper.scrapeIfNeeded(message);
    const response = await aiRouter.chat(message, null, scrapedData);
    
    console.log(chalk.green(`\nMAMAR.AI (${response.model}):`));
    console.log(chalk.white(response.text));
    console.log('');
  } catch (error) {
    console.log(chalk.red(`\nError: ${error.message}\n`));
  }

  return chat();
}

// Start the chat loop
chat().catch((error) => {
  console.error(chalk.red('Fatal error:'), error);
  process.exit(1);
});
