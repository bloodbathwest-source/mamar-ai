# Security Policy

## Supported Versions

Currently supported versions of MAMAR.AI:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

We take the security of MAMAR.AI seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Where to Report

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them via:
- Email: security@mamar.ai (if available)
- GitHub Security Advisories: https://github.com/bloodbathwest-source/mamar-ai/security/advisories/new

### What to Include

Please include the following information:
- Type of vulnerability
- Full paths of source file(s) related to the vulnerability
- Location of the affected source code (tag/branch/commit or direct URL)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Depends on severity
  - Critical: 1-7 days
  - High: 7-30 days
  - Medium: 30-90 days
  - Low: 90+ days

## Security Best Practices

### For Users

#### API Key Protection
- **Never commit** `.env` files to version control
- Use environment variables for all secrets
- Rotate API keys regularly
- Use different keys for development and production
- Limit API key permissions to minimum required

#### Production Deployment
- Always use HTTPS in production
- Enable firewall rules
- Keep Node.js and dependencies updated
- Use a reverse proxy (nginx, Cloudflare)
- Implement rate limiting
- Monitor for unusual activity

#### Input Validation
- Be cautious with URLs sent for scraping
- Don't scrape untrusted or malicious sites
- Validate user inputs before processing
- Sanitize outputs before display

### For Developers

#### Code Security
```javascript
// ❌ DON'T: Hardcode secrets
const apiKey = 'sk-1234567890abcdef';

// ✅ DO: Use environment variables
const apiKey = process.env.OPENAI_API_KEY;
```

```javascript
// ❌ DON'T: Log sensitive data
console.log('API Key:', process.env.OPENAI_API_KEY);

// ✅ DO: Log safely
console.log('API Key configured:', !!process.env.OPENAI_API_KEY);
```

#### Dependency Management
```bash
# Check for vulnerabilities
npm audit

# Fix vulnerabilities
npm audit fix

# Update dependencies
npm update
```

#### Web Scraping Security
- Respect robots.txt
- Implement rate limiting
- Use timeouts to prevent hangs
- Sanitize scraped content before use
- Don't execute scripts from scraped pages

## Known Security Considerations

### Current Implementation

1. **API Key Exposure**
   - Risk: API keys in environment variables
   - Mitigation: Never commit `.env`, use secure key management
   - Status: User responsibility

2. **Rate Limiting**
   - Risk: API abuse, cost overruns
   - Mitigation: Implement rate limiting (not yet implemented)
   - Status: Planned for v1.1

3. **Input Validation**
   - Risk: Malicious URLs for scraping
   - Mitigation: Basic URL validation exists
   - Status: Can be improved

4. **XSS Prevention**
   - Risk: Malicious content in scraped data
   - Mitigation: Client-side sanitization needed
   - Status: Planned improvement

5. **Authentication**
   - Risk: Open API endpoints
   - Mitigation: Add API key authentication
   - Status: Planned for v1.2

### Recommended Additional Security Measures

#### 1. Rate Limiting
```javascript
import rateLimit from 'express-rate-limit';

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
});

app.use('/chat', limiter);
```

#### 2. Input Sanitization
```javascript
import validator from 'validator';

app.post('/chat', (req, res) => {
  const message = validator.escape(req.body.message);
  // Process sanitized message
});
```

#### 3. CORS Configuration
```javascript
import cors from 'cors';

app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(',') || 'http://localhost:3000',
  credentials: true
}));
```

#### 4. Helmet for Security Headers
```javascript
import helmet from 'helmet';

app.use(helmet());
```

#### 5. API Authentication
```javascript
function authenticate(req, res, next) {
  const apiKey = req.headers['x-api-key'];
  
  if (!apiKey || apiKey !== process.env.API_SECRET) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  
  next();
}

app.use('/chat', authenticate);
```

## Vulnerability Disclosure Policy

### Responsible Disclosure
We request that you:
- Give us reasonable time to fix the vulnerability before public disclosure
- Make a good faith effort to avoid privacy violations, data destruction, and service disruption
- Do not exploit the vulnerability beyond what is necessary to demonstrate it
- Do not access, modify, or delete data that doesn't belong to you

### What We Promise
- Respond to your report promptly
- Keep you informed of our progress
- Credit you in our security advisories (if you wish)
- Not take legal action if you follow this policy

## Security Update Process

When a security issue is identified:

1. **Assessment**: Evaluate severity and impact
2. **Fix Development**: Create and test fix
3. **Release**: Deploy fix to supported versions
4. **Notification**: Notify users via:
   - GitHub Security Advisory
   - Release notes
   - Email (if critical)
5. **Documentation**: Update CHANGELOG and security docs

## Security Checklist for Deployment

- [ ] `.env` file is not in version control
- [ ] All API keys are properly configured
- [ ] HTTPS is enabled (production)
- [ ] Firewall rules are configured
- [ ] Rate limiting is implemented
- [ ] Input validation is in place
- [ ] Dependencies are up to date
- [ ] Security headers are configured
- [ ] Logging is enabled
- [ ] Monitoring is set up
- [ ] Backups are configured
- [ ] Error messages don't leak sensitive info

## Dependencies and Supply Chain

### Dependency Security
- All dependencies are from npm registry
- Use `npm audit` regularly
- Keep dependencies updated
- Review dependency changes in updates
- Use package-lock.json for consistency

### Current Dependencies
Major dependencies and their security considerations:
- **express**: Well-maintained, widely used
- **openai**: Official OpenAI SDK
- **anthropic**: Official Anthropic SDK
- **axios**: Popular HTTP client
- **cheerio**: Lightweight HTML parser
- **dotenv**: Environment variable loader

## Compliance

### Data Privacy
- MAMAR.AI does not store conversation history by default
- API keys are never logged or transmitted
- Web scraping respects privacy policies
- No personal data is collected without consent

### Terms of Service Compliance
When using MAMAR.AI, ensure compliance with:
- OpenAI Terms of Service
- Anthropic Terms of Service
- xAI Terms of Service
- Website scraping terms and robots.txt

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Node.js Security Best Practices](https://nodejs.org/en/docs/guides/security/)
- [npm Security Best Practices](https://docs.npmjs.com/packages-and-modules/securing-your-code)
- [Express Security Best Practices](https://expressjs.com/en/advanced/best-practice-security.html)

## Contact

For security concerns:
- Security Email: security@mamar.ai
- GitHub Security: https://github.com/bloodbathwest-source/mamar-ai/security

---

Last Updated: 2025-11-01
Version: 1.0.0
