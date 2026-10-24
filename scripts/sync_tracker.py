"""Rebuild the data block of tracker/jarvis-sprint.html from docs/PLAN.md (single source of truth)."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
plan = (ROOT / "docs" / "PLAN.md").read_text(encoding="utf-8")
html_path = ROOT / "tracker" / "jarvis-sprint.html"
html = html_path.read_text(encoding="utf-8")

MONTHS = {"Oct": 10, "Nov": 11, "Dec": 12}


def iso(text: str) -> str:
    m = re.search(r"(Oct|Nov|Dec) (\d+)", text)
    return f"2026-{MONTHS[m.group(1)]:02d}-{int(m.group(2)):02d}"


weeks, days, cur = [], [], None
for line in plan.splitlines():
    h = re.match(r"## Week (\d+) \((\w+ \d+)-(?:(\w+) )?(\d+)\): (.+)", line)
    if h:
        n, a, mon2, d2, focus = h.groups()
        start = iso(a)
        end_month = MONTHS[mon2] if mon2 else int(start[5:7])
        cur = {"w": int(n), "from": start, "to": f"2026-{end_month:02d}-{int(d2):02d}", "focus": focus, "done": ""}
        weeks.append(cur)
        continue
    r = re.match(r"\| (\d+) \| \w+ (\w+ \d+) \| (.+?) \| (.+?) \|$", line)
    if r and cur:
        days.append({"n": int(r.group(1)), "date": iso(r.group(2)), "task": r.group(3), "done": r.group(4), "w": cur["w"]})
for w in weeks:
    ws = [d for d in days if d["w"] == w["w"]]
    w["done"] = next((d["done"] for d in ws if d["done"] != "n/a"), "")
    w["focus"] = w["focus"] + ": " + "; ".join(d["task"] for d in ws if d["task"] != "Catch-up")[:140]

log_rows = []
log_file = ROOT / "docs" / "LOG.md"
if log_file.exists():
    for line in log_file.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 5 and re.match(r"\d{4}-\d{2}-\d{2}$", cells[0]):
            log_rows.append({"date": cells[0], "hours": cells[1] if cells[1].replace(".", "").isdigit() else "0",
                             "did": cells[2], "broke": cells[3], "next": cells[4]})

goal = ("Rebuild Jarvis from scratch: local Ollama assistant with tools, MCP server, Qdrant note memory, "
        "voice, README and demo. Deadline Fri Dec 4, 2026. Free and local only.")
rules = [
    "1 hour per day, 6 task days a week, 1 catch-up day",
    "Tracking restarts Sat Oct 24, 2026 (the old build is lost; old log does not count)",
    "End every session with one line: Next session: ___ and git push",
    "Skipped 2 days in a row: drop the lowest-value task of that week, do not stack a backlog",
]
block = (
    "// ---- EDIT THIS DATA IN CODE ----\n"
    f"const GOAL = {json.dumps(goal)};\n"
    f"const RULES = {json.dumps(rules, indent=2)};\n"
    f"const PLAN = {json.dumps(weeks, indent=2, ensure_ascii=False)};\n"
    f"const DAYS = {json.dumps(days, indent=2, ensure_ascii=False)};\n"
    f"const LOG = {json.dumps(log_rows, indent=2, ensure_ascii=False)};\n"
    "// ---- END DATA ----"
)
html = re.sub(r"// ---- EDIT THIS DATA IN CODE ----.*?// ---- END DATA ----", lambda m: block, html, flags=re.S)

if 'id="today"' not in html:
    html = html.replace("<h2>Progress</h2>", '<h2>Today</h2>\n<div id="today" class="entry"></div>\n\n<h2>Progress</h2>')
    html = html.replace("render();\n</script>", """(function(){
  const t=today(), d=DAYS.find(x=>x.date===t)||DAYS.find(x=>x.date>t);
  const el=document.getElementById('today');
  if(!d){el.textContent='No task scheduled.';return}
  const isToday=d.date===t;
  el.innerHTML=`<b>${isToday?'Today':'Next'}: Day ${d.n} (${esc(d.date)})</b><div>${esc(d.task)}</div><div class="mut">Done when: ${esc(d.done)}</div>`;
})();
render();
</script>""")
html_path.write_text(html, encoding="utf-8")
print(f"weeks={len(weeks)} days={len(days)}")
