import os
import logging
from datetime import datetime
from pathlib import Path

import requests
from jinja2 import Environment, FileSystemLoader, select_autoescape

TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"
logger = logging.getLogger("haven.email")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

_env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=select_autoescape(["html", "xml"])
)

def _mail_enabled():
    return os.getenv("MAIL_ENABLED", "false").lower() in {"1", "true", "yes", "on"}

def _base_context():
    app_base_url = os.getenv("APP_BASE_URL", "http://localhost:5000")
    return {
        "app_name": os.getenv("APP_NAME", "Haven"),
        "tagline": os.getenv("APP_TAGLINE", "a warm space for your mind to rest"),
        "support_email": os.getenv("SUPPORT_EMAIL", "support@haven.app"),
        "app_base_url": app_base_url,
        "brand_logo_url": os.getenv(
            "BRAND_LOGO_URL",
            f"{app_base_url}/static/branding/haven.png"
        ),
        "brand_mark_url": os.getenv(
            "BRAND_MARK_URL",
            f"{app_base_url}/static/branding/haven-mark.png"
        ),
        "footer_note": os.getenv(
            "MAIL_FOOTER_NOTE",
            "you're receiving this because you interacted with our app."
        ),
        "year": datetime.utcnow().year
    }

def render_template(template_name, context):
    template = _env.get_template(template_name)
    return template.render(**context)

def send_email(to_email, subject, template_name, context, tags=None):
    """
    Sends a transactional email via Resend.
    Requires RESEND_API_KEY, MAIL_FROM. Set MAIL_ENABLED=true to send.
    """
    base_context = _base_context()
    merged = {**base_context, **context, "subject": subject}
    html = render_template(template_name, merged)

    if not _mail_enabled():
        logger.info("Email skipped (MAIL_ENABLED=false) to=%s subject=%s", to_email, subject)
        return {"status": "skipped", "reason": "MAIL_ENABLED is false", "to": to_email}

    api_key = os.getenv("RESEND_API_KEY")
    mail_from = os.getenv("MAIL_FROM")
    reply_to = os.getenv("MAIL_REPLY_TO")

    if not api_key or not mail_from:
        logger.warning("Email skipped (missing config) to=%s subject=%s", to_email, subject)
        return {"status": "skipped", "reason": "Missing RESEND_API_KEY or MAIL_FROM", "to": to_email}

    payload = {
        "from": mail_from,
        "to": [to_email] if isinstance(to_email, str) else to_email,
        "subject": subject,
        "html": html
    }

    if reply_to:
        payload["reply_to"] = reply_to
    if tags:
        payload["tags"] = tags

    resp = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json=payload,
        timeout=15
    )
    if not resp.ok:
        logger.error("Email error to=%s subject=%s status=%s body=%s", to_email, subject, resp.status_code, resp.text)
        return {"status": "error", "status_code": resp.status_code, "body": resp.text}
    message_id = resp.json().get("id")
    logger.info("Email sent to=%s subject=%s id=%s", to_email, subject, message_id)
    return {"status": "sent", "id": message_id}
