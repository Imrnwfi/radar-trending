#!/usr/bin/env python3
"""Bina dua fail dari sejarah git data.json (ditambah data.json semasa):

- history/scores.json  : skor setiap topik bagi 14 kemas kini terakhir (kira-kira 7 hari), untuk graf trend.
- history/archive.json : topik yang dah keluar dari senarai semasa (60 hari terakhir), versi terakhir setiap satu.

Jalankan dari akar repo:  python3 tools/build_scores.py
"""
import json, subprocess, sys
from datetime import date, timedelta

KEEP = 14
ARCHIVE_DAYS = 60

def snap(d):
    return {"label": d.get("updated_label") or d.get("date"), "date": d.get("date"),
            "s": {i["id"]: i.get("score") for i in d.get("items", []) if i.get("id")}}

def versions():
    """Semua versi data.json, terbaru dahulu (semasa dulu, kemudian commit)."""
    try:
        yield json.load(open("data.json"))
    except Exception as e:
        print("data.json tak boleh dibaca:", e, file=sys.stderr)
    shas = subprocess.run(["git", "log", "--format=%H", "--", "data.json"], capture_output=True, text=True, check=True).stdout.split()
    for sha in shas:
        try:
            yield json.loads(subprocess.run(["git", "show", sha + ":data.json"], capture_output=True, text=True, check=True).stdout)
        except Exception:
            continue

def main():
    points, seen_labels = [], set()
    current_ids, archive = None, {}
    cutoff = (date.today() - timedelta(days=ARCHIVE_DAYS)).isoformat()
    for d in versions():
        label = d.get("updated_label") or d.get("date")
        if current_ids is None:
            current_ids = {i.get("id") for i in d.get("items", [])}
        if label not in seen_labels and len(points) < KEEP:
            seen_labels.add(label); points.append(snap(d))
        if (d.get("date") or "") < cutoff:
            continue
        for it in d.get("items", []):
            iid = it.get("id")
            if not iid or iid in current_ids or iid in archive:
                continue
            a = dict(it); a["_last"] = label; a["_lastDate"] = d.get("date")
            archive[iid] = a
    points.reverse()
    json.dump({"points": points}, open("history/scores.json", "w"), ensure_ascii=False, separators=(",", ":"))
    arch = sorted(archive.values(), key=lambda x: x.get("_lastDate") or "", reverse=True)
    json.dump({"items": arch}, open("history/archive.json", "w"), ensure_ascii=False, separators=(",", ":"))
    print(len(points), "titik skor;", len(arch), "topik dalam arkib:", ", ".join(a["id"] for a in arch))

if __name__ == "__main__":
    main()
