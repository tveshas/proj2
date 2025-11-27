# Deployment Guide

This FastAPI application needs to be deployed to a platform that supports Python web applications. GitHub Pages only hosts static sites, so you'll need to use one of these options:

## Option 1: Railway (Recommended - Easy Setup)

1. Go to [Railway](https://railway.app)
2. Sign up/login with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your `tveshas/proj2` repository
5. Railway will automatically detect the Python app
6. Add environment variables in Railway dashboard:
   - `EMAIL`
   - `SECRET`
   - `OPENAI_API_KEY`
   - `HOST=0.0.0.0`
   - `PORT` (auto-set by Railway)
7. Railway will provide an HTTPS URL automatically

## Option 2: Render

1. Go to [Render](https://render.com)
2. Sign up/login with GitHub
3. Click "New" → "Web Service"
4. Connect your GitHub repository `tveshas/proj2`
5. Use these settings:
   - **Build Command**: `pip install -r requirements.txt && playwright install chromium`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables in Render dashboard
7. Render provides HTTPS automatically

## Option 3: Fly.io

1. Install Fly CLI: `curl -L https://fly.io/install.sh | sh`
2. Run `fly launch` in the project directory
3. Follow the prompts
4. Set secrets: `fly secrets set EMAIL=... SECRET=... OPENAI_API_KEY=...`
5. Deploy: `fly deploy`

## Option 4: Heroku

1. Install Heroku CLI
2. Run `heroku create your-app-name`
3. Set config vars: `heroku config:set EMAIL=... SECRET=... OPENAI_API_KEY=...`
4. Deploy: `git push heroku main`

## Environment Variables Required

Make sure to set these in your deployment platform:

- `EMAIL`: Your email address
- `SECRET`: Your secret string
- `OPENAI_API_KEY`: Your OpenAI API key
- `HOST`: `0.0.0.0` (usually set automatically)
- `PORT`: Usually set automatically by the platform

## Testing Deployment

After deployment, test your endpoint:

```bash
curl -X POST https://your-app-url.com/quiz \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email",
    "secret": "your-secret",
    "url": "https://tds-llm-analysis.s-anand.net/demo"
  }'
```

## Important Notes

- The deployment platform must support:
  - Python 3.11+
  - Installing system dependencies (for Playwright)
  - Long-running processes (for quiz solving)
- Make sure your OpenAI API key has sufficient credits
- The quiz solver runs asynchronously, so the API responds immediately while processing happens in the background

