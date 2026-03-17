import os
import json
from openai import OpenAI

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com",
)

SYSTEM_PROMPT = """You are an assistant that analyzes coding competitions, hackathons, and bounties.
For each item, extract and format the following information IN ENGLISH:
- title: short competition name
- description: what participants need to build (1-2 sentences)
- prize: prize amount or reward (if mentioned)
- deadline: submission deadline (if mentioned)
- level: required skill level — one of: Beginner / Intermediate / Advanced
- technologies: main technologies or stack required (if mentioned)
- relevant: true if this is a real coding competition/hackathon/bounty with rewards, false if spam/unrelated

Respond with a JSON array of objects with these exact keys.
Be concise. Always write in English."""


def analyze(items: list) -> list:
    """Send items to DeepSeek for analysis. Returns enriched list."""
    if not DEEPSEEK_API_KEY:
        print("[Processor] DEEPSEEK_API_KEY not set, skipping enrichment.")
        return _fallback(items)

    results = []
    batch_size = 10
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        payload = json.dumps([
            {"index": j, "title": it["title"], "raw": it["raw"], "source": it["source"]}
            for j, it in enumerate(batch)
        ], ensure_ascii=False)

        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Analyze these competitions:\n{payload}"},
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
            )
            content = response.choices[0].message.content
            parsed = json.loads(content)
            analyzed = parsed if isinstance(parsed, list) else parsed.get("items", parsed.get("competitions", []))
            for j, item in enumerate(batch):
                enriched = analyzed[j] if j < len(analyzed) else {}
                if not enriched.get("relevant", True):
                    continue
                results.append({**item, **enriched})
        except Exception as e:
            print(f"[Processor] Batch {i // batch_size} error: {e}")
            results.extend(batch)

    return results


def _fallback(items: list) -> list:
    """Return items as-is when no API key is available."""
    return [{"relevant": True, "level": "Unknown", "technologies": "N/A",
             "description": it.get("raw", "")[:200], **it} for it in items]
