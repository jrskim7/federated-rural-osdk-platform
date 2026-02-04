import os
import json
import hmac
import hashlib
from flask import Flask, request, jsonify
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

GIT_REPO_PATH = os.getenv('GIT_REPO_PATH', '/git_repo')
N8N_WEBHOOK_URL = os.getenv('N8N_WEBHOOK_URL')
GITHUB_WEBHOOK_SECRET = os.getenv('GITHUB_WEBHOOK_SECRET')

def send_to_n8n(payload):
    """Send event to n8n webhook."""
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(N8N_WEBHOOK_URL, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        print(f"Event sent to n8n: {payload.get('eventType')}")
        return True
    except Exception as e:
        print(f"Failed to send to n8n: {e}")
        return False

@app.route('/webhook/github', methods=['POST'])
def handle_github_webhook():
    """Handle GitHub webhooks for MBSE changes."""
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

    if event == 'push':
        changes = []
        for commit in payload.get('commits', []):
            # Look for changes in mbse/ directory
            mbse_changes = []
            for f in commit.get('modified', []) + commit.get('added', []):
                if f.startswith('mbse/'):
                    mbse_changes.append(f)
            
            for f in mbse_changes:
                changes.append({
                    "action": "MODIFY" if f in commit.get('modified', []) else "CREATE",
                    "filePath": f,
                    "elementType": "ModelFile"
                })

        if changes:
            # Create standardized event
            mbse_event = {
                "eventId": f"evt_{hash(str(changes) + commit_hash) % 10**8}",
                "eventType": "MBSE_MODEL_UPDATE",
                "source": "mbse-bridge",
                "repository": payload['repository']['html_url'],
                "commitHash": commit_hash,
                "changes": changes,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            
            success = send_to_n8n(mbse_event)
            return jsonify({"status": "processed" if success else "send_failed"}), 200

    return jsonify({"status": "ignored"}), 200

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    print("MBSE Bridge starting on port 5000")
    app.run(host='0.0.0.0', port=5000, debug=False)