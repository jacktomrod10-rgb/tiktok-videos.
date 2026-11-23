"""Count A/B/C votes from Windsor TikTok comment rows.

Usage: python3 -I series/pennys/tally.py comments.json
comments.json: a list of rows (or {"data": [...]}) with comment_text, comment_username, comment_likes.

Rules:
- One vote per username: their earliest comment that clearly picks a single letter.
- A comment counts if, after trimming punctuation, it is just "a", "b" or "c"; or starts with
  "a ", "b ", "c " / "a!" etc.; or contains "option a" / "vote b" / "team c".
- Ties: the tied option whose comments have the most total likes wins; still tied, the earliest listed of the tied letters in A, B, C order.
- Zero votes: winner is chosen at random ("Crumbs chose").
"""
import json, re, sys, random

def letter_of(text):
    s = (text or "").strip().lower()
    s = re.sub(r"[\s]+", " ", s)
    bare = re.sub(r"[^a-z ]", "", s).strip()
    if bare in ("a", "b", "c"):
        return bare.upper()
    m = re.match(r"^([abc])(\s|[!.,:)\-]|$)", s)
    if m:
        return m.group(1).upper()
    m = re.search(r"\b(?:option|vote|team|choose|pick|go with)\s*([abc])\b", s)
    if m:
        return m.group(1).upper()
    return None

def main(path):
    data = json.load(open(path))
    rows = data.get("data", data) if isinstance(data, dict) else data
    seen, votes, likes = set(), {"A": 0, "B": 0, "C": 0}, {"A": 0, "B": 0, "C": 0}
    for r in rows:
        user = r.get("comment_username") or r.get("comment_id")
        L = letter_of(r.get("comment_text"))
        if not L or user in seen:
            continue
        seen.add(user)
        votes[L] += 1
        likes[L] += int(r.get("comment_likes") or 0)
    total = sum(votes.values())
    if total == 0:
        winner, rule = random.choice("ABC"), "no votes: random (Crumbs chose)"
    else:
        top = max(votes.values())
        tied = [k for k in "ABC" if votes[k] == top]
        if len(tied) == 1:
            winner, rule = tied[0], "most votes"
        else:
            best = max(likes[k] for k in tied)
            tied2 = [k for k in tied if likes[k] == best]
            winner, rule = tied2[0], "tie broken by comment likes" if len(tied2) == 1 else "tie: first letter"
    print(json.dumps({**votes, "total": total, "winner": winner, "rule": rule}))

if __name__ == "__main__":
    main(sys.argv[1])
