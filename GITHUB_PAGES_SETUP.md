# GitHub Pages Deployment Setup

This guide will help you deploy both the frontend (on GitHub Pages) and backend (via Railway/Render) using GitHub.

## Step 1: Enable GitHub Pages

1. Go to your repository: https://github.com/tveshas/proj2
2. Click **Settings** → **Pages**
3. Under **Source**, select **GitHub Actions**
4. Save the settings

## Step 2: Deploy Backend (Choose One)

### Option A: Railway (Recommended)

1. Go to https://railway.app and sign up with GitHub
2. Create a new project → **Deploy from GitHub repo**
3. Select `tveshas/proj2`
4. Railway will auto-detect and deploy
5. Add environment variables in Railway dashboard:
   - `EMAIL`
   - `SECRET`
   - `OPENAI_API_KEY`
6. Copy your Railway URL (e.g., `https://your-app.railway.app`)

### Option B: Render

1. Go to https://render.com and sign up with GitHub
2. New → **Web Service** → Connect `tveshas/proj2`
3. Settings:
   - **Build Command**: `pip install -r requirements.txt && playwright install chromium`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables
5. Copy your Render URL

## Step 3: Connect Frontend to Backend

1. Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add secret:
   - **Name**: `API_ENDPOINT`
   - **Value**: Your Railway/Render URL (e.g., `https://your-app.railway.app`)
4. Save

## Step 4: Deploy Frontend

1. Push any change to trigger the GitHub Actions workflow:
   ```bash
   git add frontend/
   git commit -m "Add frontend for GitHub Pages"
   git push
   ```
2. Go to **Actions** tab in your GitHub repo
3. Wait for "Deploy to GitHub Pages" workflow to complete
4. Your site will be live at: `https://tveshas.github.io/proj2/`

## Step 5: Update API Endpoint (Optional)

If you need to change the API endpoint later:
1. Update the secret `API_ENDPOINT` in GitHub Settings
2. Re-run the "Deploy to GitHub Pages" workflow

## Testing

1. Visit your GitHub Pages site: `https://tveshas.github.io/proj2/`
2. Fill in the form with:
   - Your email
   - Your secret
   - A quiz URL (e.g., `https://tds-llm-analysis.s-anand.net/demo`)
3. Submit and verify it calls your backend API

## Troubleshooting

- **Frontend not loading**: Check GitHub Pages settings are enabled
- **API calls failing**: Verify `API_ENDPOINT` secret is set correctly
- **Backend not deploying**: Check Railway/Render logs for errors
- **CORS errors**: Make sure your backend allows requests from `https://tveshas.github.io`

## Notes

- GitHub Pages is **free** and hosts the frontend
- Railway/Render free tier hosts the backend
- Both update automatically when you push to `main` branch
- Your API endpoint will be `https://your-app.railway.app` or similar

