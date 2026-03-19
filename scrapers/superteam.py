import requests

# Keywords that indicate a coding/building task (not content/design/marketing)
_CODE_KEYWORDS = [
    "build", "develop", "code", "hack", "sdk", "program", "smart contract",
    "anchor", "dapp", "api", "solana", "blockchain", "protocol", "deploy",
    "integration", "extension", "vault", "escrow", "challenge", "project",
    "trading", "defi", "web3", "submission",
]

_SKIP_KEYWORDS = [
    "thread", "tweet", "ambassador", "video content", "article", "write ",
    "sticker", "design ", "feedback", "spotlight", "story", "explain",
    "content bounty", "illustration", "animation",
]

MIN_PRIZE_USD = 300


def _is_coding(title: str) -> bool:
    t = title.lower()
    if any(kw in t for kw in _SKIP_KEYWORDS):
        return False
    return any(kw in t for kw in _CODE_KEYWORDS)


def fetch(limit=20):
    """Fetch open coding bounties from Superteam Earn (Solana ecosystem)."""
    url = "https://earn.superteam.fun/api/listings/"
    params = {"type": "bounty", "status": "open", "limit": 50}
    headers = {"User-Agent": "Mozilla/5.0 (compatible; HackathonBot/1.0)"}
    results = []

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
        items = resp.json()
        if not isinstance(items, list):
            items = items.get("bounties", items.get("data", []))

        for item in items:
            reward = item.get("rewardAmount", 0) or 0
            title = item.get("title", "N/A")
            token = item.get("token", "USDC")

            if reward < MIN_PRIZE_USD:
                continue
            if not _is_coding(title):
                continue

            slug = item.get("slug", item.get("id", ""))
            sponsor = item.get("sponsor", {}).get("name", "")
            submissions = item.get("_count", {}).get("Submission", None)

            results.append({
                "source": "Superteam Earn",
                "title": title,
                "url": f"https://earn.superteam.fun/listing/{slug}" if slug else "https://earn.superteam.fun/",
                "prize": f"${reward:,.0f} {token}",
                "deadline": item.get("deadline", "N/A"),
                "participants": submissions,
                "raw": f"{title} {sponsor} Solana Web3 bounty build".strip()[:500],
            })

            if len(results) >= limit:
                break

    except Exception as e:
        print(f"[Superteam] Error: {e}")

    return results
