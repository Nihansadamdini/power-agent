import re
from datetime import datetime
from pathlib import Path

PLANS = Path(__file__).parent.parent / "plans"


def save_plan(title, content):
    title, content = str(title).strip(), str(content).strip()
    if not title or not content:
        raise ValueError("title and content are required")
    if len(content) > 5000:
        raise ValueError("content too long (max 5000 characters)")

    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:40] or "plan"
    PLANS.mkdir(exist_ok=True)
    # fixed folder, user input never becomes part of a path
    path = PLANS / f"{slug}-{datetime.now():%Y%m%d-%H%M%S}.md"
    path.write_text(f"# {title}\n\n{content}\n", encoding="utf-8")
    return {"saved_to": path.name}