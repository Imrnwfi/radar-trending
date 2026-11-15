#!/usr/bin/env python3
"""Bina history/scores.json: skor setiap topik bagi 14 kemas kini terakhir (kira-kira 7 hari).

Sumber: sejarah git bagi data.json, ditambah data.json semasa (kalau belum di-commit).
Jalankan dari akar repo:  python3 tools/build_scores.py
"""
import json, subprocess, sys

KEEP = 14

def snap(d):
    return {"label": d.get("updated_label") or d.get("date"), "date": d.get("date"),
            "s": {i["id"]: i.get("score") for i in d.get("items", []) if i.get("id")}}

def main():
    shas = subprocess.run(["git", "log", "--format=%H", "--", "data.json"], capture_output=True, text=True, check=True).stdout.split()
    points, seen = [], set()
    try:
        cur = json.load(open("data.json"))
        p = snap(cur); points.append(p); seen.add(p["label"])
    except Exception as e:
        print("data.json tak boleh dibaca:", e, file=sys.stderr)
    for sha in shas:
        if len(points) >= KEEP: break
        try:
            d = json.loads(subprocess.run(["git", "show", sha + ":data.json"], capture_output=True, text=True, check=True).stdout)
        except Exception:
            continue
        p = snap(d)
        if p["label"] in seen: continue
        seen.add(p["label"]); points.append(p)
    points.reverse()
    json.dump({"points": points}, open("history/scores.json", "w"), ensure_ascii=False, separators=(",", ":"))
    print(len(points), "titik:", ", ".join(p["label"] for p in points))

if __name__ == "__main__":
    main()
