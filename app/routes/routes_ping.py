
from fastapi import APIRouter
import os
import requests

router = APIRouter()

@router.post("/ping-discord")
def ping_discord():
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        return {"error": "Missing DISCORD_WEBHOOK_URL environment variable"}

    message = {"content": "✅ Dev Agent is live and wired up! Progress updates will now be sent regularly."}
    try:
        response = requests.post(webhook_url, json=message)
        response.raise_for_status()
        return {"status": "Ping sent successfully", "code": response.status_code}
    except requests.RequestException as e:
        return {"error": str(e)}
