import praw
import os


SUBREDDITS = ["ethdev", "web3", "hackathon", "webdev", "cryptocurrency"]
KEYWORDS = ["hackathon", "bounty", "contest", "competition", "challenge", "prize", "vibe coding"]


def fetch(limit=30):
    """Search relevant posts across crypto/dev subreddits."""
    client_id = os.environ.get("REDDIT_CLIENT_ID")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET")
    if not client_id or not client_secret:
        print("[Reddit] Skipping: REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET not set")
        return []

    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent="HackathonAggregatorBot/1.0",
    )
    results = []
    try:
        for sub in SUBREDDITS:
            for post in reddit.subreddit(sub).new(limit=50):
                text = (post.title + " " + (post.selftext or "")).lower()
                if any(kw in text for kw in KEYWORDS):
                    results.append({
                        "source": f"Reddit r/{sub}",
                        "title": post.title,
                        "url": f"https://reddit.com{post.permalink}",
                        "prize": "N/A",
                        "deadline": "N/A",
                        "raw": f"{post.title} {post.selftext[:400]}",
                    })
            if len(results) >= limit:
                break
    except Exception as e:
        print(f"[Reddit] Error: {e}")
    return results[:limit]
