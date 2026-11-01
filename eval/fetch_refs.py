import json, os, sys, time, requests, concurrent.futures as cf
S, N = sys.argv[1], int(sys.argv[2])
OUT = f"{S}/refs"
db = json.load(open(f"{S}/db/caatinga_species.json"))
H = {"User-Agent": "plant-eval-script/0.1 (research test)"}
meta = []
for s in db["species"]:
    d = os.path.join(OUT, s["id"]); os.makedirs(d, exist_ok=True)
    have = len(os.listdir(d))
    if have >= N: print(s["id"], have, "cached", flush=True); continue
    got = have; used = None
    for name in [s["scientific_name"]] + s["synonyms"]:
        if got >= N: break
        for place in ("6878", None):
            if got >= N: break
            p = {"taxon_name": name.replace("×", "x"), "quality_grade": "research", "photos": "true", "per_page": 50,
                 "photo_license": "cc-by,cc-by-nc,cc0,cc-by-sa,cc-by-nc-sa", "order_by": "votes", "d2": "2024-12-31"}
            if place: p["place_id"] = place
            try: r = requests.get("https://api.inaturalist.org/v1/observations", params=p, headers=H, timeout=30).json()
            except Exception: time.sleep(5); continue
            todo = [o for o in r.get("results", []) if not os.path.exists(os.path.join(d, f"{o['id']}.jpg"))][:N-got]
            def dl(o):
                try: return o, requests.get(o["photos"][0]["url"].replace("square", "small"), headers=H, timeout=30).content
                except Exception: return o, None
            with cf.ThreadPoolExecutor(8) as ex:
                for o, b in ex.map(dl, todo):
                    if not b: continue
                    ph = o["photos"][0]
                    open(os.path.join(d, f"{o['id']}.jpg"), "wb").write(b); got += 1; used = name
                    meta.append({"id": s["id"], "obs": o["id"], "taxon": o["taxon"]["name"], "license": ph.get("license_code"), "attribution": ph.get("attribution")})
            time.sleep(1)
    print(s["id"], got, used, flush=True)
    json.dump(meta, open(f"{S}/refs_meta.json", "w"), ensure_ascii=False)
