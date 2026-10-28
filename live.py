"""THE BOARD PAGE BETWEEN CLOSES (owner 2026-10-29: the Board page must agree with Portfolio Pulse, which moves through the
day). data.json (the Mac mini, daily) carries Makarios and SPY to the last close the gold store holds, and the holdings as
weights at that close. This carries both on from that close to Yahoo's latest prices, as Pulse does: each holding by its own
price move since that close (the holdings do not change between the owner's reports), cash flat, SPY by its price. Writes
live.json; the page draws it after the store's line. Standard library only."""
import datetime as dt, json, time, urllib.request

UA = {"User-Agent": "Mozilla/5.0"}


def chart(t):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{t.replace('.', '-')}?range=10d&interval=1d"
    for k in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                res = json.load(r)["chart"]["result"][0]
            break
        except Exception as e:
            last = e; time.sleep(5 * (k + 1))
    else:
        raise RuntimeError(f"{t}: {last}")
    gmt = res["meta"].get("gmtoffset", -14400)
    day = lambda s: dt.datetime.fromtimestamp(s + gmt, dt.timezone.utc).date().isoformat()
    px = {day(s): c for s, c in zip(res["timestamp"], res["indicators"]["quote"][0]["close"]) if c}
    m = res["meta"]
    if m.get("regularMarketTime") and m.get("regularMarketPrice"):
        px[day(m["regularMarketTime"])] = m["regularMarketPrice"]          # today's latest, or today's close once closed
    return px, m.get("regularMarketTime")


def main():
    d = json.load(open("data.json"))
    base = d["as_of"]
    hold = [(h["t"], h["w"]) for h in d["holdings"]]
    px = {t: chart(t) for t, _ in hold}
    spy, at = chart("SPY")
    days = sorted(x for x in spy if x > base)
    out = {"base": base, "dates": [], "makarios": [], "spy": [], "at": dt.datetime.fromtimestamp(at, dt.timezone.utc).isoformat() if at else None}
    missing = [t for t, _ in hold if base not in px[t][0]]
    if base not in spy or missing:
        out["note"] = "no Yahoo close on " + base + " for " + ", ".join(missing + ([] if base in spy else ["SPY"]))
    else:
        m0, s0 = d["makarios"][-1], d["spy"][-1]
        for day in days:
            v = d["cash"] + sum(w * px[t][0].get(day, px[t][0][max(k for k in px[t][0] if k <= day)]) / px[t][0][base] for t, w in hold)
            out["dates"].append(day); out["makarios"].append(round(m0 * v / (d["cash"] + sum(w for _, w in hold)), 8))
            out["spy"].append(round(s0 * spy[day] / spy[base], 8))
    json.dump(out, open("live.json", "w"), separators=(",", ":"))
    print(json.dumps({k: v for k, v in out.items() if k != "dates"})[:300])


if __name__ == "__main__":
    main()
