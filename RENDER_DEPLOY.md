# Deploy to Render (Free Tier)

Render offers a free tier that's perfect for this FastAPI application. Follow these steps:

## Step 1: Sign Up for Render

1. Go to https://render.com
2. Click **Get Started for Free**
3. Sign up with your **GitHub account** (recommended for easy deployment)

## Step 2: Create a New Web Service

1. Once logged in, click **New +** → **Web Service**
2. Click **Connect account** next to GitHub (if not already connected)
3. Select your repository: **tveshas/proj2**
4. Click **Connect**

## Step 3: Configure the Service

Render will auto-detect the `render.yaml` file, but you can also configure manually:

- **Name**: `quiz-solver-api` (or any name you prefer)
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt && playwright install chromium`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Plan**: Select **Free** (or Starter if you need more resources)

## Step 4: Add Environment Variables

In the Render dashboard, go to **Environment** section and add:

- `EMAIL` = your email address
- `SECRET` = your secret string
- `OPENAI_API_KEY` = your OpenAI API key
- `HOST` = `0.0.0.0` (optional, Render sets this automatically)
- `PORT` = (auto-set by Render, don't change)

## Step 5: Deploy

1. Click **Create Web Service**
2. Render will automatically:
   - Clone your repository
   - Install dependencies
   - Install Playwright browsers
   - Start your FastAPI server
3. Wait for deployment to complete (usually 5-10 minutes first time)

## Step 6: Get Your URL

Once deployed, Render will provide you with a URL like:
- `https://quiz-solver-api.onrender.com`

**Note**: On the free tier, your service will spin down after 15 minutes of inactivity. The first request after spin-down may take 30-60 seconds to wake up.

## Step 7: Test Your Deployment

```bash
curl -X POST https://your-app.onrender.com/health
```

Should return: `{"status":"healthy"}`

Test the quiz endpoint:
```bash
curl -X POST https://your-app.onrender.com/quiz \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email",
    "secret": "your-secret",
    "url": "https://tds-llm-analysis.s-anand.net/demo"
  }'
```

## Auto-Deploy

Render automatically deploys when you push to the `main` branch. No manual deployment needed!

## Free Tier Limits

- **512 MB RAM**
- **0.5 CPU**
- **Spins down after 15 min inactivity** (first request after spin-down is slower)
- **Unlimited bandwidth** (within reason)

## Troubleshooting

- **Build fails**: Check the build logs in Render dashboard
- **Service won't start**: Check environment variables are set correctly
- **Playwright issues**: Make sure `playwright install chromium` runs in build command
- **Timeout errors**: Free tier has request timeouts, but 3-minute quiz timeout should be fine

## Update Your Google Form

Once deployed, update your Google Form submission with:
- **API endpoint URL**: `https://your-app.onrender.com/quiz`

That's it! Your API will be live and accessible via HTTPS.

