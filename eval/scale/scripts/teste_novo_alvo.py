"""Subamostra de teste NOVA, só das 3 espécies reforçadas, para estimar o ganho do índice v1.0.1 sem o viés
de ter escolhido as referências olhando o teste principal.

Uso:
  python teste_novo_alvo.py fetch   <species.json> <dir_dados> <attr_refs_novas.json>
  python teste_novo_alvo.py avaliar <modelo.onnx> <species.json> <dir_dados> <saida.json> nome=<indice.bin> [nome=<indice.bin> ...]

Regras da coleta:
- aroeira-do-sertão, mulungu e umburana-de-cambão; grau "pesquisa" ou "needs_id" com identificação da comunidade
  na espécie e >= 2 identificadores concordando; qualquer licença (só para medir, nada é redistribuído);
- observação que não foi usada em nada antes: fora do teste principal, do conjunto fora da base, do mini teste,
  das referências do índice publicado, da calibração e das referências novas;
- 1 observação por observador (a mais recente), 1 foto (a principal);
- marca se o observador já tem foto no teste principal (observador_no_teste) e se a observação foi criada a partir
  de 2025-12-01, para os recortes.
Grava em <dir_dados>/novo_alvo/. Na avaliação, saem as cópias (dHash <= 6 ou cosseno >= 0,99) de qualquer foto
de teste ou referência (publicada ou nova).
"""
import json, os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_test import api, dl
from avaliar import read_index, score, preprocess, dhash, wilson

ALVO = ["astronium_urundeuva", "erythrina_velutina", "commiphora_leptophloeos"]


def prop(k, n):
    return {"k": int(k), "n": int(n), "p": round(k / n, 4) if n else None, "ic95": wilson(int(k), int(n))}


def fetch(species_json, data, attr_new):
    db = {s["id"]: s for s in json.load(open(species_json))["species"]}
    excl = {int(x) for x in open(os.path.join(data, "exclude_obs.txt")).read().split()}
    test_users = {}
    for split in ("test", "ood", "campo"):
        for l in open(os.path.join(data, split, "meta.jsonl")):
            m = json.loads(l); excl.add(m["obs"])
            if split == "test": test_users.setdefault(m["species"], set()).add(m["user_id"])
    excl |= {v["obs"] for v in json.load(open(attr_new)).values()}
    out = os.path.join(data, "novo_alvo"); os.makedirs(out, exist_ok=True)
    rows = []
    for sid in ALVO:
        s = db[sid]
        names = {n.lower() for n in [s["scientific_name"]] + s["synonyms"]}
        match = lambda t: any(t.lower() == n or t.lower().startswith(n + " ") for n in names)
        users, chosen = set(), []
        id_below = None
        for page in range(10):
            p = {"taxon_name": s["scientific_name"], "quality_grade": "research,needs_id", "photos": "true",
                 "per_page": 200, "order_by": "id", "order": "desc"}
            if id_below: p["id_below"] = id_below
            res = api(p).get("results", [])
            for o in res:
                uid = o.get("user", {}).get("id")
                if o["id"] in excl or uid in users or not o.get("photos"): continue
                ids = [i for i in o.get("identifications", []) if i.get("current") and i.get("taxon")]
                ct = next((i["taxon"] for i in ids if i["taxon"]["id"] == o.get("community_taxon_id")), None)
                if ct is None or not match(ct["name"]): continue
                if len({i["user"]["id"] for i in ids if match(i["taxon"]["name"])}) < 2: continue
                users.add(uid); ph = o["photos"][0]
                chosen.append({"species": sid, "obs": o["id"], "photo": ph["id"], "quality_grade": o["quality_grade"],
                               "user_id": uid, "observador_no_teste": uid in test_users.get(sid, set()),
                               "created_at": o.get("created_at"), "license": ph.get("license_code"),
                               "attribution": ph.get("attribution"), "url": ph["url"].replace("square", "medium")})
            if len(res) < 200: break
            id_below = res[-1]["id"]
        d = os.path.join(out, sid); os.makedirs(d, exist_ok=True)
        for c in chosen:
            fn = os.path.join(d, f"{c['obs']}_{c['photo']}.jpg")
            if os.path.exists(fn) or dl((c["url"], fn)): c["file"] = os.path.relpath(fn, out); rows.append(c)
        print(sid, "observações novas", len(chosen), "de observador novo", sum(not c["observador_no_teste"] for c in chosen), flush=True)
    with open(os.path.join(out, "meta.jsonl"), "w") as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")


def avaliar(model, species_json, data, out_path, *indices):
    import onnxruntime as ort
    sess = ort.InferenceSession(model, providers=["CPUExecutionProvider"])
    meta = [json.loads(l) for l in open(os.path.join(data, "novo_alvo", "meta.jsonl"))]
    X = np.stack([sess.run(None, {"pixel_values": preprocess(os.path.join(data, "novo_alvo", m["file"]))})[0][0] for m in meta]).astype(np.float32)
    idxs = [(a.split("=", 1)[0], read_index(a.split("=", 1)[1])) for a in indices]
    z = np.load(os.path.join(data, "emb_test.npz")); Xt = z["X"].astype(np.float32)
    allrefs = np.concatenate([i[1][2] for i in idxs])
    hs_test = [dhash(os.path.join(data, "test", f)) for f, sp in zip(z["files"], z["files"]) if sp.split("/")[0] in ALVO]
    ref_files = [l.strip() for l in open(os.path.join(data, "refs_files.txt")) if l.strip() and any(f"/{a}/" in l for a in ALVO)]
    hs_ref = [dhash(f) for f in ref_files]
    cos = np.maximum((X @ Xt.T).max(1), (X @ allrefs.T).max(1))
    keep = [i for i, m in enumerate(meta) if cos[i] < 0.99 and not any(
        bin(dhash(os.path.join(data, "novo_alvo", m["file"])) ^ o).count("1") <= 6 for o in hs_test + hs_ref)]
    dropped = len(meta) - len(keep)
    meta = [meta[i] for i in keep]; X = X[keep]
    sp = np.array([m["species"] for m in meta]); novo = np.array([not m["observador_no_teste"] for m in meta])
    recente = np.array([m["created_at"][:10] >= "2025-12-01" for m in meta])
    res = {"rotulo": "Subamostra NOVA (observações não usadas antes), só aroeira-do-sertão, mulungu e umburana-de-cambão",
           "n": len(meta), "descartadas_por_copia": dropped, "indices": {}}
    for name, idx in idxs:
        h = idx[0]; cat = idx[3]
        sid2pos = {h["labels"][lab]["id"]: i for i, lab in enumerate(cat)}
        order, prob, in_cat, conf = score(X, idx)
        y = np.array([sid2pos[s] for s in sp])
        t1 = order[:, 0] == y; t3 = (order[:, :3] == y[:, None]).any(1)

        def b(mask):
            return {"n": int(mask.sum()), "top1": prop(t1[mask].sum(), mask.sum()), "top3": prop(t3[mask].sum(), mask.sum())}
        allm = np.ones(len(meta), bool)
        res["indices"][name] = {"todas": b(allm), "observador_novo": b(novo), "criadas_desde_2025_12": b(recente),
                                "por_especie": {s: b(sp == s) for s in ALVO}, "_t1": t1.tolist()}
    names = [n for n, _ in idxs]
    if len(names) == 2:
        a, c = np.array(res["indices"][names[0]]["_t1"]), np.array(res["indices"][names[1]]["_t1"])
        import math
        g, p = int((~a & c).sum()), int((a & ~c).sum()); n = g + p
        res["pareado"] = {"erradas_que_viraram_certas": g, "certas_que_viraram_erradas": p,
                          "mcnemar_p": round(min(1.0, 2 * sum(math.comb(n, i) for i in range(min(g, p) + 1)) / 2 ** n), 4) if n else 1.0}
    for v in res["indices"].values(): v.pop("_t1")
    res["fotos"] = [{"obs": m["obs"], "foto": m["photo"], "especie": m["species"], "grau": m["quality_grade"],
                     "observador_no_teste": m["observador_no_teste"], "criada_em": m["created_at"][:10],
                     "licenca": m["license"], "credito": m["attribution"]} for m in meta]
    json.dump(res, open(out_path, "w"), ensure_ascii=False, indent=1)
    for name, v in res["indices"].items():
        print(name, {k: (v[k]["n"], v[k]["top1"]["p"], v[k]["top1"]["ic95"], v[k]["top3"]["p"]) for k in ("todas", "observador_novo", "criadas_desde_2025_12")},
              {s: (x["top1"]["k"], x["n"]) for s, x in v["por_especie"].items()})
    print(res.get("pareado"), "descartadas", dropped)


if __name__ == "__main__":
    if sys.argv[1] == "fetch": fetch(*sys.argv[2:5])
    else: avaliar(*sys.argv[2:])
