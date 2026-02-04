Testing MBSE Bridge with ngrok & GitHub Actions

Goal: Allow local MBSE Bridge to receive a GitHub push event (via an action that POSTs the push payload) using a public ngrok URL.

Steps:

1) Install ngrok and run it locally (exposes your local port 5000):
   - Download/install ngrok (https://ngrok.com/)
   - Start: ngrok http 5000
   - Note the generated public HTTPS URL (e.g., https://abcd1234.ngrok.io)

2) Configure GitHub repository secrets:
   - Go to your repository Settings → Secrets and variables → Actions → New repository secret
   - Add `MBSE_BRIDGE_WEBHOOK_URL` with value `https://<your-ngrok-id>.ngrok.io/webhook/github`
   - Ensure `GITHUB_WEBHOOK_SECRET` matches the secret in `orchestrator/.env` (the bridge uses this to validate signatures). Set it as the same value in GitHub secrets.

3) Enable the GitHub Action
   - The repo includes `.github/workflows/notify-mbse-bridge-on-push.yml` which runs on push to `mbse/**` and `orchestrator/**`.
   - When you push changes to `mbse/exports` (e.g., modify `sample_capella_export.json`) the Action will run and POST the push event payload to your ngrok URL.

4) Verify locally
   - Check the MBSE bridge logs (docker-compose logs --tail=50 mbse-bridge) — you should see the incoming POST and the bridge forwarding the event to n8n (if n8n is running).

Notes and security
   - Do NOT leave ngrok running publicly longer than needed. Revoke or rotate your `GITHUB_WEBHOOK_SECRET` after testing.
   - For production, host a properly secured endpoint and set the GitHub webhook there (or use the GitHub UI webhook settings instead of relying on the A.C.T. flow).

Troubleshooting
   - If the bridge replies 403, check the signature value and that the secret matches exactly (no trailing newline).
   - If the Action fails, check the action logs (Actions tab) for the cURL output and signature used.
