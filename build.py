"""THE BOARD PAGE'S NUMBERS ARE PORTFOLIO PULSE'S (owner 2026-10-29: the two must agree). Pulse publishes every line,
carried to the latest prices through the US session; this keeps only Makarios and SPY - SPY from the close before
Makarios's first session - and writes data.json in Pulse's own shape, which the page (Pulse's page, restyled) reads.
Standard library only."""
import json, time, urllib.request

SRC = "https://itktl.github.io/pulse-b2dedc/data.json"
KEEP = ("makarios", "spy")
FROM = "2025-04-30"            # the close before Makarios's first session

for k in range(4):
    try:
        with urllib.request.urlopen(urllib.request.Request(f"{SRC}?t={int(time.time())}", headers={"User-Agent": "Mozilla/5.0", "Cache-Control": "no-cache"}), timeout=30) as r:
            d = json.load(r)
        break
    except Exception as e:
        last = e; time.sleep(5 * (k + 1))
else:
    raise SystemExit(f"Pulse's data could not be read: {last}")
lines = {l["key"]: l for l in d["lines"]}
missing = [k for k in KEEP if k not in lines]
if missing: raise SystemExit("Pulse's data has no line for " + ", ".join(missing))
out = {k: d.get(k) for k in ("updatedAt", "priceTime", "strategiesSyncedAt")}
out["allStart"] = FROM
out["holdingsOn"] = {"makarios": (d.get("holdingsOn") or {}).get("makarios")}
out["overdue"] = [t for t in d.get("overdue") or [] if "Makarios" in t]
out["lines"] = [{"key": k, "name": lines[k]["name"], "series": [p for p in lines[k]["series"] if p[0] >= FROM]} for k in KEEP]
json.dump(out, open("data.json", "w"), separators=(",", ":"))
print("Makarios to", out["lines"][0]["series"][-1], "| SPY to", out["lines"][1]["series"][-1], "| prices", out["priceTime"])
