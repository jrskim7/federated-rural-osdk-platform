import os
import sys
import json
import hmac
import hashlib
from flask import Flask, request, jsonify
import requests
from datetime import datetime
from dotenv import load_dotenv

# Force unbuffered output
sys.stdout = sys.stderr

# Load from explicit paths
load_dotenv('/app/.env')
load_dotenv('/git_repo/orchestrator/.env')
load_dotenv()

app = Flask(__name__)

GIT_REPO_PATH = os.getenv('GIT_REPO_PATH', '/git_repo')
N8N_WEBHOOK_URL = os.getenv('N8N_WEBHOOK_URL')
GITHUB_WEBHOOK_SECRET = os.getenv('GITHUB_WEBHOOK_SECRET')

def send_to_n8n(payload):
    """Send event to n8n webhook."""
    try:
        print(f"[SEND_N8N] Attempting to send to: {N8N_WEBHOOK_URL}", flush=True)
        headers = {'Content-Type': 'application/json'}
        response = requests.post(N8N_WEBHOOK_URL, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        print(f"[SEND_N8N] Event sent successfully: {payload.get('eventType')}", flush=True)
        return True
    except Exception as e:
        print(f"[SEND_N8N] Failed to send to n8n: {e}", flush=True)
        return False

@app.route('/webhook/github', methods=['POST'])
def handle_github_webhook():
    """Handle GitHub webhooks for MBSE changes."""
    print(f"[DEBUG] Webhook received, checking N8N_WEBHOOK_URL: {N8N_WEBHOOK_URL}")
    
    # Verify signature (security)
    signature = request.headers.get('X-Hub-Signature-256', '')
    if GITHUB_WEBHOOK_SECRET:
        body = request.get_data()
        expected = hmac.new(
            GITHUB_WEBHOOK_SECRET.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(f"sha256={expected}", signature):
            return jsonify({"error": "Invalid signature"}), 403

    event = request.headers.get('X-GitHub-Event', '')
    payload = request.json
    commit_hash = payload.get('after', '')[:8] if payload.get('after') else 'unknown'

    print(f"[DEBUG] GitHub event type: {event}, commit: {commit_hash}")

    if event == 'push':
        # Get all changed files
        all_changes = []
        for commit in payload.get('commits', []):
            all_files = commit.get('modified', []) + commit.get('added', [])
            print(f"[DEBUG] Commit changes: {all_files}")
            for f in all_files:
                all_changes.append({
                    "action": "MODIFY" if f in commit.get('modified', []) else "CREATE",
                    "filePath": f,
                    "elementType": "file"
                })

        # Always forward the event to n8n
        if all_changes or True:  # Always process push events
            mbse_event = {
                "eventId": f"evt_{hash(str(all_changes) + commit_hash) % 10**8}",
                "eventType": "GITHUB_PUSH",
                "source": "mbse-bridge",
                "repository": payload.get('repository', {}).get('html_url', 'unknown'),
                "commitHash": commit_hash,
                "changes": all_changes[:10],  # Limit to first 10 changes
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            
            print(f"[DEBUG] Forwarding event to n8n: {mbse_event['eventType']}")
            success = send_to_n8n(mbse_event)
            return jsonify({"status": "processed" if success else "send_failed"}), 200

    print(f"[DEBUG] Event not processed, type: {event}")
    return jsonify({"status": "ignored"}), 200

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    print("MBSE Bridge starting on port 5000")
    app.run(host='0.0.0.0', port=5000, debug=False)