# 🏆 Hackathon Aggregator — Weekly Coding Competitions Digest Bot

> A fully automated bot that collects coding competitions, hackathons, and bounties from 6+ sources every week, analyzes them with DeepSeek LLM, and delivers a ranked digest with prizes, deadlines, and skill levels to Telegram — hands-free, every Monday at 9 AM UTC.

---

## What it does

Every Monday morning the bot:

1. **Collects** open hackathons and bounties from 6 platforms (Devpost, Superteam Earn, Reddit, GitHub, DoraHacks, Gitcoin)
2. **Filters** expired competitions and removes non-coding tasks (content, marketing)
3. **Analyzes** each competition with DeepSeek LLM — extracts description, skill level, and tech stack
4. **Converts** all prizes to USD (from INR, EUR, tokens, etc.)
5. **Ranks** by prize amount descending, marks deadlines within 14 days with ⏰
6. **Delivers** formatted digest to a Telegram channel or forum topic — fully automatically

---

## Example output

```
🏆 Weekly Coding Competitions | 24 Mar 2026

1. Ranger Build-A-Bear Hackathon
📋 Build Web3 projects on Solana blockchain.
💰 Prize: $1,000,000
📅 Deadline: Apr 06, 2026
🎯 Level: Intermediate | Solana, Web3
👥 Participants: 8
🔗 https://earn.superteam.fun/listing/...

2. GitLab AI Hackathon
📋 Build AI-powered applications using GitLab's platform.
💰 Prize: $65,000
📅 Deadline: Feb 09 - Mar 25, 2026 ⏰ 5d left!
🎯 Level: Advanced | GitLab, Machine Learning/AI
👥 Participants: 5,744
🔗 https://gitlab.devpost.com/

...

Total: 26 competitions
Sources: Devpost (15), Superteam Earn (10), GitHub (1)

🔍 Also check:
• DoraHacks Active Hackathons — https://dorahacks.io/hackathon
• Gitcoin Open Bounties — https://gitcoin.co/explorer
```

---

## Architecture

```
GitHub Actions (cron: every Monday 09:00 UTC)
        │
        ▼
  scrapers/ ──► Devpost JSON API       (top 20 by prize, sorted)
             ──► Superteam Earn API    (Solana bounties & hackathons)
             ──► Reddit RSS feeds      (r/hackathon, r/ethdev, r/web3…)
             ──► GitHub Search API     (repos tagged hackathon/bounty)
             ──► DoraHacks             (Web3 hackathons pointer)
             ──► Gitcoin               (Web3 bounties pointer)
        │
        ▼
  main.py ──► deduplicate (seen.json — committed back to repo)
           ──► filter expired deadlines
           ──► convert all currencies → USD
           ──► mark "ending soon" (≤14 days)
        │
        ▼
  processor.py ──► DeepSeek API → description, skill level, tech stack, prestige flag
        │
        ▼
  main.py ──► sort by prize DESC (prestige items kept even with $0 prize)
        │
        ▼
  notifier.py ──► Telegram Bot API → sendMessage (with optional forum thread_id)
```

---

## Tech stack

| Layer | Technology |
|---|---|
| Runtime | Python 3.11 |
| Scheduling | GitHub Actions (free tier, cron) |
| LLM | DeepSeek Chat API (`deepseek-chat`) |
| Web scraping | requests + BeautifulSoup4 |
| RSS parsing | feedparser |
| Delivery | Telegram Bot API |
| Deduplication | JSON file committed to repo |
| Secrets | GitHub Actions Secrets |

---

## Data sources

| Source | Type | Coverage |
|---|---|---|
| **Devpost** | JSON API | General hackathons worldwide |
| **Superteam Earn** | REST API | Solana / Web3 bounties & hackathons |
| **Reddit** | RSS feeds | r/hackathon, r/ethdev, r/web3, r/webdev |
| **GitHub Search** | REST API | Repos tagged with hackathon/bounty topics |
| **DoraHacks** | Pointer | Web3 multi-chain hackathons |
| **Gitcoin** | Pointer | Web3 open-source bounties |

---

## Cost

| Service | Cost |
|---|---|
| GitHub Actions | Free (uses ~5 min/month of 2000 free) |
| DeepSeek API | ~$0.10–0.30 / month |
| Telegram Bot API | Free |
| **Total** | **~$0.30 / month** |

---

## Setup

1. Fork this repo
2. Create a Telegram bot via [@BotFather](https://t.me/BotFather) and add it to your channel/group
3. Add GitHub Secrets:
   - `TELEGRAM_BOT_TOKEN` — bot token from BotFather
   - `TELEGRAM_CHAT_ID` — channel or group ID (use [@JsonDumpBot](https://t.me/JsonDumpBot) to find it)
   - `TELEGRAM_THREAD_ID` *(optional)* — forum topic ID for supergroups
   - `DEEPSEEK_API_KEY` — from [platform.deepseek.com](https://platform.deepseek.com)
   - `REDDIT_CLIENT_ID` + `REDDIT_CLIENT_SECRET` *(optional)* — from [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)
4. Enable GitHub Actions in your fork
5. Trigger manually: **Actions → Weekly Hackathon Digest → Run workflow**

---

## Project by

Built as part of an automation portfolio.
Interested in a similar bot for your niche? Let's talk.
