# Deploy to Fly.io (Alternative Free Option)

Fly.io also offers a generous free tier. Here's how to deploy:

## Step 1: Install Fly CLI

```bash
# macOS
curl -L https://fly.io/install.sh | sh

# Or use Homebrew
brew install flyctl
```

## Step 2: Sign Up

```bash
fly auth signup
# Or if you have an account:
fly auth login
```

## Step 3: Create Fly App

```bash
cd /Users/liltv/Desktop/code/p2
fly launch
```

Follow the prompts:
- App name: `quiz-solver-api` (or choose your own)
- Region: Choose closest to you
- PostgreSQL: No (we don't need a database)
- Redis: No

## Step 4: Configure Secrets

```bash
fly secrets set EMAIL="your-email@example.com"
fly secrets set SECRET="your-secret-string"
fly secrets set OPENAI_API_KEY="your-openai-api-key"
```

## Step 5: Deploy

```bash
fly deploy
```

## Step 6: Get Your URL

```bash
fly status
```

Your app will be available at: `https://quiz-solver-api.fly.dev`

## Auto-Deploy with GitHub Actions

The `.github/workflows/deploy-backend.yml` can be updated to use Fly.io instead of Railway.

## Free Tier Limits

- **3 shared-cpu-1x VMs** (256MB RAM each)
- **3GB persistent volume storage**
- **160GB outbound data transfer**

## Troubleshooting

- View logs: `fly logs`
- SSH into app: `fly ssh console`
- Check status: `fly status`

