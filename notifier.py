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
TELEGRAM_THREAD_ID = os.environ.get("TELEGRAM_THREAD_ID")


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
    if TELEGRAM_THREAD_ID:
        payload["message_thread_id"] = int(TELEGRAM_THREAD_ID)
    resp = requests.post(url, json=payload, timeout=15)
    if not resp.ok:
        print(f"[Notifier] Telegram error: {resp.text}")


# ── Web2 / Web3 classification ──────────────────────────────────────────────────
_WEB3_SOURCES = {"DoraHacks", "Gitcoin", "Superteam Earn", "ETHGlobal", "Devfolio"}

_WEB3_KEYWORDS = (
    "web3", "blockchain", "crypto", "solana", "ethereum", "evm", "defi", "dao",
    "nft", "smart contract", "on-chain", "onchain", "zk ", "zero-knowledge",
    "token", "wallet", "polkadot", "cosmos", "layer 2", "layer2", "staking",
    "dapp", "airdrop", "rollup", "stablecoin",
)


def _track(item: dict) -> str:
    """Classify an item as 'web2' or 'web3'."""
    if item.get("track") in ("web2", "web3"):
        return item["track"]
    if item.get("source") in _WEB3_SOURCES:
        return "web3"
    text = " ".join(str(item.get(k, "")) for k in ("title", "technologies", "description", "raw")).lower()
    return "web3" if any(kw in text for kw in _WEB3_KEYWORDS) else "web2"


def _source_stats(items: list) -> str:
    counts = {}
    for it in items:
        src = it.get("source", "Unknown")
        counts[src] = counts.get(src, 0) + 1
    return ", ".join(f"{k} ({v})" for k, v in sorted(counts.items()))


def _format_block(i: int, item: dict) -> str:
    title = _strip_html(item.get("title", "N/A"))[:80]
    description = _strip_html(item.get("description", item.get("raw", "")))[:200]
    prize = item.get("prize", "N/A")
    deadline = item.get("deadline", "N/A")
    days_left = item.get("_days_left")
    deadline_display = deadline
    if days_left is not None:
        deadline_display += f" ⏰ {days_left}d left!"
    level = item.get("level", "N/A")
    technologies = item.get("technologies", "N/A")
    participants = item.get("participants")
    url = item.get("url", "")

    block = (
        f"<b>{i}. {title}</b>\n"
        f"📋 {description}\n"
        f"💰 Prize: {prize}\n"
        f"📅 Deadline: {deadline_display}\n"
        f"🎯 Level: {level}"
    )
    if technologies and technologies not in ("N/A", "Not specified"):
        block += f" | {technologies}"
    if participants:
        block += f"\n👥 Participants: {participants:,}" if isinstance(participants, int) else f"\n👥 Participants: {participants}"
    if url:
        block += f"\n🔗 {url}"
    block += "\n\n"
    return block


def _flush(messages: list, current: str) -> str:
    """Send current message and reset buffer."""
    _send(current.rstrip())
    return ""


def send_digest(items: list):
    """Format and send weekly digest to Telegram, split into Web2 / Web3 sections."""
    today = datetime.utcnow().strftime("%d %b %Y")

    main_items = [it for it in items if not it.get("_is_pointer")]
    pointer_items = [it for it in items if it.get("_is_pointer")]

    if not main_items and not pointer_items:
        _send(f"🏆 <b>Weekly Coding Competitions | {today}</b>\n\nNo new competitions found this week.")
        return

    MAX_LEN = 4000
    # Mutable holder so nested helpers can flush across the 4000-char limit
    state = {"msg": f"🏆 <b>Weekly Coding Competitions | {today}</b>\n\n"}

    def _append(chunk: str):
        if len(state["msg"]) + len(chunk) > MAX_LEN and state["msg"].strip():
            _send(state["msg"].rstrip())
            state["msg"] = ""
        state["msg"] += chunk

    def _section(heading: str, mains: list, ptrs: list):
        if not mains and not ptrs:
            return
        _append(f"{heading}\n\n")
        for i, item in enumerate(mains, 1):
            _append(_format_block(i, item))
        if ptrs:
            also = "🔍 <b>Also check:</b>\n"
            for it in ptrs:
                also += f"• {it.get('title', 'N/A')} — {it.get('url', '')}\n"
            _append(also + "\n")

    web2_main = [it for it in main_items if _track(it) == "web2"]
    web3_main = [it for it in main_items if _track(it) == "web3"]
    web2_ptr = [it for it in pointer_items if _track(it) == "web2"]
    web3_ptr = [it for it in pointer_items if _track(it) == "web3"]

    _section("🌐 <b>WEB2</b>", web2_main, web2_ptr)
    _section("⛓️ <b>WEB3</b>", web3_main, web3_ptr)

    _append(f"Total: {len(main_items)} competitions "
            f"(Web2: {len(web2_main)}, Web3: {len(web3_main)})\n"
            f"Sources: {_source_stats(main_items)}")

    if state["msg"].strip():
        _send(state["msg"].rstrip())
