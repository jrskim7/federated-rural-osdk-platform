# Step 1: Install and run ngrok locally (Mac)

## Install ngrok
```bash
brew install ngrok
```

## Start ngrok (expose port 5000)
```bash
ngrok http 5000
```

You'll see output like:
```
ngrok                                                       (Ctrl+C to quit)

Session Status                online
Account                       your_account
Version                       3.x.x
Region                        us (United States)
Forwarding                    https://abc123def456.ngrok.io -> http://localhost:5000
Forwarding                    http://abc123def456.ngrok.io -> http://localhost:5000
```

**Copy the HTTPS URL** (e.g., `https://abc123def456.ngrok.io`) — you'll use it in GitHub secrets.

---

# Step 2: Add GitHub Secrets

1. Go to your repository on GitHub: https://github.com/YOUR-USERNAME/federated-rural-osdk-platform
2. Click **Settings** (top right) → **Secrets and variables** → **Actions**
3. Click **New repository secret**

Add these TWO secrets:

### Secret 1: MBSE_BRIDGE_WEBHOOK_URL
- Name: `MBSE_BRIDGE_WEBHOOK_URL`
- Value: `https://abc123def456.ngrok.io/webhook/github` (replace with your ngrok URL)
- Click **Add secret**

### Secret 2: GITHUB_WEBHOOK_SECRET
- Name: `GITHUB_WEBHOOK_SECRET`
- Value: Copy the value from `orchestrator/.env` line: `GITHUB_WEBHOOK_SECRET=826c262c29e6d0f189f79e6655954893b1878fe6`
- Click **Add secret**

---

# Step 3: Trigger the workflow

Choose ONE of these:

## Option A: Manual trigger (fastest)
1. Go to **Actions** tab on GitHub
2. Click **Notify MBSE Bridge on push** (on the left)
3. Click **Run workflow** button (top right)
4. Keep defaults, click green **Run workflow** button
5. Watch the job run and check logs

## Option B: Push a small change
1. Make a tiny edit to trigger it (e.g., add a comment to `mbse/exports/sample_capella_export.json`):
   ```bash
   cd /Users/jrbd/Documents/GitHub/federated-rural-osdk-platform
   # Edit the file to add a comment line at the top
   git add mbse/exports/sample_capella_export.json
   git commit -m "test: trigger webhook via push"
   git push
   ```
2. Watch the action run (Actions tab → the workflow job should start)

---

# Step 4: Verify the webhook was received

## Check ngrok terminal
You should see HTTP POST requests logged:
```
POST /webhook/github                     200 OK
```

## Check MBSE bridge logs (Docker)
```bash
cd /Users/jrbd/Documents/GitHub/federated-rural-osdk-platform/orchestrator
docker-compose logs --tail=50 mbse-bridge
```

Look for:
```
172.19.0.1 - - [...] "POST /webhook/github HTTP/1.1" 200
```

## Check n8n logs (if n8n is running)
The bridge should forward the event to n8n webhook. If n8n is up:
```bash
docker-compose logs --tail=50 n8n | grep -i webhook
```

---

# Troubleshooting

| Issue | Solution |
|-------|----------|
| GitHub Action says `MBSE_BRIDGE_WEBHOOK_URL secret not set` | Go back to GitHub Secrets and verify both secrets are added correctly (no extra spaces) |
| ngrok shows 403 Forbidden | The signature validation failed. Make sure `GITHUB_WEBHOOK_SECRET` in GitHub Secrets exactly matches the one in `orchestrator/.env` (character-for-character) |
| curl fails in the action | Check the action logs (Actions tab → job → see the cURL output). Usually a URL or signature issue |
| MBSE bridge logs show no POST | Ngrok URL might be wrong in the GitHub secret. Double-check it matches what ngrok prints |

---

# Clean up after testing

When done, stop ngrok:
```bash
# Ctrl+C in the ngrok terminal
```

(Optional) Rotate your `GITHUB_WEBHOOK_SECRET` to a new value for production (since you exposed it to ngrok).
