# Contributing to MAMAR.AI

Thank you for your interest in contributing to MAMAR.AI! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

1. **Fork the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/mamar-ai.git
   cd mamar-ai
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment**
   ```bash
   cp .env.example .env
   # Add your API keys to .env
   ```

4. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 📝 Development Guidelines

### Code Style

- Use ES6+ JavaScript features
- Follow existing code formatting
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions small and focused

### Project Structure

```
mamar-ai/
├── src/
│   ├── index.js          # Main Express server
│   ├── ai/               # AI provider integrations
│   │   └── router.js     # AI model routing logic
│   ├── scraper/          # Web scraping modules
│   │   └── scraper.js    # Web scraper implementation
│   └── cli.js            # CLI interface
├── public/               # Frontend files
│   ├── index.html        # Web interface
│   ├── styles.css        # Cyberpunk theme styles
│   └── script.js         # Frontend JavaScript
├── config/               # Configuration files
│   └── config.js         # App configuration
└── ...
```

### Making Changes

1. **Add Features**
   - Create new files in appropriate directories
   - Update README.md if adding major features
   - Add configuration options to .env.example if needed

2. **Fix Bugs**
   - Identify the root cause
   - Write a minimal fix
   - Test thoroughly

3. **Update Documentation**
   - Keep README.md up to date
   - Update API.md for API changes
   - Add comments to complex code

### Testing

Before submitting:

1. **Manual Testing**
   ```bash
   npm start
   # Test the web interface at http://localhost:3000
   ```

2. **CLI Testing**
   ```bash
   npm run cli
   # Test CLI commands
   ```

3. **Syntax Check**
   ```bash
   node --check src/index.js
   node --check src/ai/router.js
   node --check src/scraper/scraper.js
   ```

## 🔧 Areas for Contribution

### High Priority

- [ ] Add automated tests (Jest, Mocha)
- [ ] Implement rate limiting
- [ ] Add WebSocket support for streaming
- [ ] Enhance error handling
- [ ] Add request caching
- [ ] Implement user authentication

### Medium Priority

- [ ] Add more AI model integrations
- [ ] Improve web scraping (handle JavaScript, SPAs)
- [ ] Add conversation history
- [ ] Create browser extension
- [ ] Mobile app (React Native)
- [ ] Multi-language support

### Documentation

- [ ] Video tutorials
- [ ] API examples in more languages
- [ ] Architecture diagrams
- [ ] Performance benchmarks
- [ ] Security best practices guide

## 📋 Pull Request Process

1. **Update your branch**
   ```bash
   git fetch origin
   git rebase origin/main
   ```

2. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add feature description"
   ```

   Use conventional commits:
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `style:` Code style changes
   - `refactor:` Code refactoring
   - `test:` Adding tests
   - `chore:` Maintenance tasks

3. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Create Pull Request**
   - Go to GitHub and create a PR
   - Describe your changes clearly
   - Reference any related issues
   - Wait for review

## 🐛 Reporting Bugs

When reporting bugs, include:

- **Description**: Clear description of the issue
- **Steps to Reproduce**: Detailed steps
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Environment**: OS, Node version, etc.
- **Screenshots**: If applicable
- **Logs**: Error messages or stack traces

Example:
```
### Bug Description
Chat functionality fails when using Claude model

### Steps to Reproduce
1. Select Claude from model selector
2. Send message "Hello"
3. Error appears in console

### Expected
AI response from Claude

### Actual
500 error: "API key not configured"

### Environment
- OS: Ubuntu 22.04
- Node: 18.17.0
- Browser: Chrome 119
```

## 💡 Feature Requests

When suggesting features:

- **Use Case**: Why is this needed?
- **Proposed Solution**: How should it work?
- **Alternatives**: Other approaches considered?
- **Additional Context**: Screenshots, examples, etc.

## 🤝 Code of Conduct

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone.

### Our Standards

✅ **Positive Behavior:**
- Be respectful and inclusive
- Welcome newcomers
- Accept constructive criticism
- Focus on what's best for the community
- Show empathy

❌ **Unacceptable Behavior:**
- Harassment or discrimination
- Trolling or insulting comments
- Personal or political attacks
- Publishing others' private information
- Unprofessional conduct

## 📚 Resources

- [Node.js Documentation](https://nodejs.org/docs)
- [Express.js Guide](https://expressjs.com/en/guide)
- [OpenAI API](https://platform.openai.com/docs)
- [Anthropic Claude API](https://docs.anthropic.com)
- [xAI Grok API](https://x.ai/api)

## 🎓 Learning Resources

New to the project? Check out:

1. **JavaScript/Node.js**
   - [MDN JavaScript Guide](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
   - [Node.js Beginners Guide](https://nodejs.dev/learn)

2. **AI APIs**
   - OpenAI Cookbook
   - Anthropic Documentation
   - xAI Developer Portal

3. **Web Development**
   - HTML/CSS fundamentals
   - Modern JavaScript (ES6+)
   - RESTful APIs

## 📞 Contact

- GitHub Issues: For bugs and features
- Discussions: For questions and ideas
- Email: support@mamar.ai (if available)

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to MAMAR.AI! 🤖✨
