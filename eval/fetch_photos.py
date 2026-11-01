import json, os, sys, time, requests
OUT = sys.argv[1]
N = int(sys.argv[2]) if len(sys.argv) > 2 else 8
SPECIES = sys.argv[3].split(",") if len(sys.argv) > 3 else ["Ziziphus joazeiro","Cereus jamacaru","Spondias tuberosa","Myracrodruon urundeuva","Aloe vera",
 "Sideroxylon obtusifolium","Mimosa tenuiflora","Commiphora leptophloeos","Anadenanthera colubrina",
 "Erythrina velutina","Cenostigma pyramidale","Pilosocereus gounellei","Lippia alba","Plectranthus barbatus",
 "Cymbopogon citratus","Amburana cearensis","Hymenaea courbaril","Libidibia ferrea","Handroanthus impetiginosus",
 "Ficus benjamina","Mentha spicata","Jatropha mollissima"]
H = {"User-Agent": "plant-eval-script/0.1 (research test)"}
meta = []
for sp in SPECIES:
    d = os.path.join(OUT, sp.replace(" ", "_")); os.makedirs(d, exist_ok=True)
    got = 0
    for place in ("6878", None):  # Brazil first, then anywhere
        if got >= N: break
        p = {"taxon_name": sp, "quality_grade": "research", "photos": "true", "per_page": 40,
             "photo_license": "cc-by,cc-by-nc,cc0,cc-by-sa,cc-by-nc-sa", "order_by": "votes"}
        if place: p["place_id"] = place
        if os.environ.get("D1"): p["d1"] = os.environ["D1"]; p["order_by"] = "observed_on"
        r = requests.get("https://api.inaturalist.org/v1/observations", params=p, headers=H, timeout=30).json()
        seen = {m["obs"] for m in meta if m["species"] == sp}
        for o in r.get("results", []):
            if got >= N: break
            if o["id"] in seen or o["taxon"]["name"] != sp and not o["taxon"]["name"].startswith(sp): continue
            ph = o["photos"][0]
            url = ph["url"].replace("square", "medium")
            try:
                b = requests.get(url, headers=H, timeout=30).content
            except Exception as e:
                continue
            fn = os.path.join(d, f"{o['id']}.jpg"); open(fn, "wb").write(b)
            meta.append({"species": sp, "obs": o["id"], "file": fn, "license": ph.get("license_code"), "attribution": ph.get("attribution"), "place": o.get("place_guess")})
            got += 1; time.sleep(0.3)
        time.sleep(1)
    print(sp, got, flush=True)
json.dump(meta, open(os.path.join(OUT, ("meta_extra.json" if len(sys.argv) > 3 else "meta.json")), "w"), ensure_ascii=False, indent=1)
