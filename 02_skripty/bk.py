# -*- coding: utf-8 -*-
"""BlenderKit: поиск и скачивание моделей (ключ берётся из blenderkit_data/config/preferences.json, не печатается).
python bk.py search "запрос" [n]      -> список + миниатюры в 03_materialy/blenderkit/_thumbs
python bk.py get <asset_id> [имя]     -> 03_materialy/blenderkit/<имя>.blend"""
import json, os, sys, uuid, urllib.request, urllib.parse
ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "03_materialy", "blenderkit")
os.makedirs(os.path.join(ROOT, "_thumbs"), exist_ok=True)
KEY = json.load(open(os.path.expanduser(r"~\blenderkit_data\config\preferences.json"), encoding="utf-8"))["api_key"]
API = "https://www.blenderkit.com/api/v1/"
def req(url, auth=True):
    r = urllib.request.Request(url, headers={"User-Agent": "blenderkit-script", **({"Authorization": "Bearer " + KEY} if auth else {})})
    return urllib.request.urlopen(r, timeout=60)
def search(q, n=12):
    url = API + "search/?" + urllib.parse.urlencode({"query": "asset_type:model is_free:true " + q, "page_size": n, "addon_version": "3.21.4"})
    d = json.load(req(url))
    out = []
    for i, a in enumerate(d.get("results", [])):
        th = a.get("thumbnailMiddleUrl") or a.get("thumbnailSmallUrl")
        tp = os.path.join(ROOT, "_thumbs", a["id"] + ".jpg")
        if th and not os.path.exists(tp):
            try: open(tp, "wb").write(req(th, False).read())
            except Exception: pass
        out.append(dict(id=a["id"], name=a.get("name"), free=a.get("isFree"), files=a.get("files", []), dims=[a.get("dictParameters", {}).get(k) for k in ("dimensionX", "dimensionY", "dimensionZ")]))
        print(i, a["id"], "FREE" if a.get("isFree") else "paid", a.get("name"), out[-1]["dims"])
    db = os.path.join(ROOT, "_index.json"); old = json.load(open(db, encoding="utf-8")) if os.path.exists(db) else {}
    old.update({o["id"]: o for o in out}); json.dump(old, open(db, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
def get(aid, name=None):
    a = json.load(open(os.path.join(ROOT, "_index.json"), encoding="utf-8"))[aid]
    f = next(x for x in a["files"] if x["fileType"] == "blend")
    j = json.load(req(f["downloadUrl"] + "?scene_uuid=" + str(uuid.uuid4())))
    out = os.path.join(ROOT, (name or a["name"]).replace(" ", "_").replace("/", "_") + ".blend")
    open(out, "wb").write(req(j["filePath"], False).read())
    print("SAVED", out, os.path.getsize(out))
if __name__ == "__main__":
    if sys.argv[1] == "search": search(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 12)
    else: get(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
