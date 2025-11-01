# MAMAR.AI Deployment Guide

## 🚀 Deployment Options

### Option 1: Local Development

1. **Clone and Install**
   ```bash
   git clone https://github.com/bloodbathwest-source/mamar-ai.git
   cd mamar-ai
   npm install
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your API keys:
   - `OPENAI_API_KEY` - Get from https://platform.openai.com
   - `ANTHROPIC_API_KEY` - Get from https://console.anthropic.com
   - `XAI_API_KEY` - Get from https://x.ai (for Grok access)

3. **Run**
   ```bash
   npm start
   ```
   Visit http://localhost:3000

### Option 2: Production Deployment

#### Vercel

1. Install Vercel CLI:
   ```bash
   npm i -g vercel
   ```

2. Deploy:
   ```bash
   vercel
   ```

3. Add environment variables in Vercel dashboard

#### Heroku

1. Create Heroku app:
   ```bash
   heroku create mamar-ai
   ```

2. Set environment variables:
   ```bash
   heroku config:set OPENAI_API_KEY=your_key
   heroku config:set ANTHROPIC_API_KEY=your_key
   heroku config:set XAI_API_KEY=your_key
   ```

3. Deploy:
   ```bash
   git push heroku main
   ```

#### Docker

1. Build image:
   ```bash
   docker build -t mamar-ai .
   ```

2. Run container:
   ```bash
   docker run -p 3000:3000 \
     -e OPENAI_API_KEY=your_key \
     -e ANTHROPIC_API_KEY=your_key \
     -e XAI_API_KEY=your_key \
     mamar-ai
   ```

#### DigitalOcean/AWS/GCP

1. Set up a Node.js server (Ubuntu 22.04 recommended)

2. Install Node.js:
   ```bash
   curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
   sudo apt-get install -y nodejs
   ```

3. Clone and configure:
   ```bash
   git clone https://github.com/bloodbathwest-source/mamar-ai.git
   cd mamar-ai
   npm install
   cp .env.example .env
   nano .env  # Add your API keys
   ```

4. Use PM2 for process management:
   ```bash
   npm install -g pm2
   pm2 start src/index.js --name mamar-ai
   pm2 save
   pm2 startup
   ```

5. Configure nginx as reverse proxy:
   ```nginx
   server {
       listen 80;
       server_name mamar.ai;

       location / {
           proxy_pass http://localhost:3000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
       }
   }
   ```

6. Enable SSL with Let's Encrypt:
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d mamar.ai
   ```

## 🔒 Security Considerations

1. **API Keys**: Never commit `.env` file to git
2. **Rate Limiting**: Implement rate limiting for production
3. **CORS**: Configure CORS properly for your domain
4. **HTTPS**: Always use HTTPS in production
5. **Input Validation**: Sanitize user inputs

## 📊 Monitoring

### PM2 Monitoring
```bash
pm2 monit
pm2 logs mamar-ai
```

### Health Checks
```bash
curl http://localhost:3000/status
```

## 🔄 Updates

```bash
git pull origin main
npm install
pm2 restart mamar-ai
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Change PORT in .env file
PORT=3001
```

### Missing Dependencies
```bash
rm -rf node_modules package-lock.json
npm install
```

### API Key Issues
- Verify keys are correctly set in `.env`
- Check API quotas and billing
- Ensure no extra spaces in keys

## 📈 Scaling

For high traffic:
1. Use a load balancer (nginx, HAProxy)
2. Run multiple instances with PM2:
   ```bash
   pm2 start src/index.js -i max --name mamar-ai
   ```
3. Consider Redis for session management
4. Implement caching for scraped data

## 🌐 Domain Configuration

1. Point your domain to server IP:
   - A record: `@` → `your.server.ip`
   - CNAME: `www` → `mamar.ai`

2. Update `.env`:
   ```
   HOST=mamar.ai
   ```

## 💡 Tips

- Monitor API usage to avoid unexpected costs
- Implement request queuing for high traffic
- Cache frequently accessed web content
- Use CDN for static assets
- Enable gzip compression

---

For support, visit: https://github.com/bloodbathwest-source/mamar-ai/issues
