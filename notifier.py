import html
import os
import re
import requests
from datetime import datetime


def _strip_html(text: str) -> str:
    """Remove HTML tags and decode entities."""
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


def _send(text: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[Notifier] TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set.")
        print(text)
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    resp = requests.post(url, json=payload, timeout=15)
    if not resp.ok:
        print(f"[Notifier] Telegram error: {resp.text}")


def _source_stats(items: list) -> str:
    counts = {}
    for it in items:
        src = it.get("source", "Unknown")
        counts[src] = counts.get(src, 0) + 1
    return ", ".join(f"{k} ({v})" for k, v in sorted(counts.items()))


def send_digest(items: list):
    """Format and send weekly digest to Telegram."""
    today = datetime.utcnow().strftime("%d %b %Y")
    if not items:
        _send(f"🏆 <b>Weekly Coding Competitions | {today}</b>\n\nNo new competitions found this week.")
        return

    header = f"🏆 <b>Weekly Coding Competitions | {today}</b>\n\n"
    messages = [header]
    current_msg = header
    MAX_LEN = 4000

    for i, item in enumerate(items, 1):
        title = _strip_html(item.get("title", "N/A"))[:80]
        description = _strip_html(item.get("description", item.get("raw", "")))[:200]
        prize = item.get("prize", "N/A")
        deadline = item.get("deadline", "N/A")
        level = item.get("level", "N/A")
        technologies = item.get("technologies", "N/A")
        url = item.get("url", "")

        block = (
            f"<b>{i}. {title}</b>\n"
            f"📋 {description}\n"
            f"💰 Prize: {prize}\n"
            f"📅 Deadline: {deadline}\n"
            f"🎯 Level: {level}"
        )
        if technologies and technologies != "N/A":
            block += f" ({technologies})"
        if url:
            block += f"\n🔗 {url}"
        block += "\n\n"

        if len(current_msg) + len(block) > MAX_LEN:
            _send(current_msg.rstrip())
            current_msg = block
        else:
            current_msg += block

    stats = f"Total found: {len(items)}\nSources: {_source_stats(items)}"
    if len(current_msg) + len(stats) > MAX_LEN:
        _send(current_msg.rstrip())
        _send(stats)
    else:
        _send(current_msg.rstrip() + "\n\n" + stats)
