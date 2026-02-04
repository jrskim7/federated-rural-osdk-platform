import os
import json
import hmac
import hashlib
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "http://n8n:5678/webhook/mbse-change")
GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")


def send_to_n8n(payload: dict) -> bool:
    import requests
    try:
        r = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=10)
        r.raise_for_status()
        return True
    except Exception as e:
        print("Failed to send to n8n:", e)
        return False


@app.route("/webhook/github", methods=["POST"])
def handle_github_webhook():
    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({"status": "no_payload"}), 400

    # simple signature check (if secret provided)
    if GITHUB_WEBHOOK_SECRET:
        signature = request.headers.get("X-Hub-Signature-256") or request.headers.get("X-Hub-Signature")
        if signature:
            sha_name, signature = signature.split("=")
            mac = hmac.new(GITHUB_WEBHOOK_SECRET.encode(), msg=request.data, digestmod=hashlib.sha256)
            if not hmac.compare_digest(mac.hexdigest(), signature):
                return jsonify({"status": "invalid_signature"}), 403

    commit_hash = None
    changes = []
    if payload.get("head_commit"):
        commit_hash = payload["head_commit"].get("id")
        # Minimal change record
        for f in payload["head_commit"].get("added", []) + payload["head_commit"].get("modified", []):
            changes.append({"filePath": f, "action": "MODIFY"})

    event = {
        "eventId": f"evt_{int(datetime.utcnow().timestamp())}",
        "eventType": "MBSE_MODEL_UPDATE",
        "source": "github",
        "repository": payload.get("repository", {}).get("html_url"),
        "commitHash": commit_hash,
        "changes": changes,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    ok = send_to_n8n(event)
    return jsonify({"status": "sent" if ok else "failed"}), 200


@app.route("/run/capella-to-arcgis", methods=["POST"])
def run_capella_to_arcgis():
    # This runs the converter against the MBSE export path
    from capella_to_geojson import convert
    mbse_path = request.json.get("mbse_path") if request.json else None
    out_path = request.json.get("out_path") if request.json else None
    try:
        res = convert(mbse_path, out_path)
        return jsonify({"status": "ok", "result": res}), 200
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)