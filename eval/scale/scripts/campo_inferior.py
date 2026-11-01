"""Mini teste com fotos de qualidade inferior (observações "casual" ou "needs_id") das 22 espécies-chave.

Uso:
  python campo_inferior.py fetch   <species.json> <dir_dados>
  python campo_inferior.py avaliar <modelo.onnx> <plant-index.bin> <species.json> <dir_dados> <saida.json>

Regras (iguais para todas as espécies-chave):
- grau "casual" ou "needs_id" no iNaturalist, com foto;
- criadas a partir de 2024-09-01 (depois do corte do pré-treino do BioCLIP-2; ver contaminacao.py);
- identificação da comunidade (community_taxon) na espécie ou abaixo dela, com pelo menos 2 identificadores
  distintos cuja identificação atual concorda com essa espécie;
- fora do conjunto de teste, das referências do índice, da calibração (exclude_obs.txt) e do conjunto fora da base;
- 1 foto por observação (a principal), no máximo 1 observação por observador; até N por espécie (mais recentes primeiro).
Grava em <dir_dados>/campo/ (meta.jsonl + fotos). A avaliação usa o mesmo pré-processamento e pontuação do app
e descarta cópias (dHash <= 6 bits ou cosseno >= 0,99) de referências do índice ou de fotos de teste.
"""
import json, os, sys, glob
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_test import CHAVE, api, dl, tier
from avaliar import read_index, score, preprocess, dhash, wilson

N = 7
CREATED_D1 = "2024-09-01"


def prop(k, n):
    return {"k": int(k), "n": int(n), "p": round(k / n, 4) if n else None, "ic95": wilson(int(k), int(n))}


def fetch(species_json, data):
    db = {s["id"]: s for s in json.load(open(species_json))["species"]}
    out = os.path.join(data, "campo"); os.makedirs(out, exist_ok=True)
    excl = {int(x) for x in open(os.path.join(data, "exclude_obs.txt")).read().split()}
    for split in ("test", "ood"):
        excl |= {json.loads(l)["obs"] for l in open(os.path.join(data, split, "meta.jsonl"))}
    rows, observers = [], set()
    for sid in sorted(CHAVE):
        s = db[sid]
        names = {n.replace("×", "x").lower() for n in [s["scientific_name"]] + s["synonyms"]}
        match = lambda t: any(t.replace("×", "x").lower() == n or t.replace("×", "x").lower().startswith(n + " ") for n in names)
        chosen, vistos = [], 0
        for name in [s["scientific_name"]] + s["synonyms"]:
            id_below = None
            for page in range(5):
                p = {"taxon_name": name, "quality_grade": "casual,needs_id", "photos": "true", "per_page": 200,
                     "order_by": "id", "order": "desc", "created_d1": CREATED_D1}
                if id_below: p["id_below"] = id_below
                res = api(p).get("results", [])
                for o in res:
                    vistos += 1
                    if len(chosen) >= N: break
                    if o["id"] in excl or not o.get("photos") or not o.get("community_taxon_id"): continue
                    ids = [i for i in o.get("identifications", []) if i.get("current") and i.get("taxon")]
                    ct = next((i["taxon"] for i in ids if i["taxon"]["id"] == o["community_taxon_id"]), None)
                    if ct is None or not match(ct["name"]): continue
                    agree = {i["user"]["id"] for i in ids if match(i["taxon"]["name"])}
                    uid = o.get("user", {}).get("id")
                    if len(agree) < 2 or uid in observers: continue
                    ph = o["photos"][0]
                    observers.add(uid); excl.add(o["id"])
                    chosen.append({"species": sid, "obs": o["id"], "photo": ph["id"], "quality_grade": o["quality_grade"],
                                   "captive": o.get("captive"), "community_taxon": ct["name"],
                                   "identificadores_concordantes": len(agree), "created_at": o.get("created_at"),
                                   "observed_on": o.get("observed_on"), "license": ph.get("license_code"),
                                   "attribution": ph.get("attribution"), "url": ph["url"].replace("square", "medium")})
                if len(chosen) >= N or len(res) < 200: break
                id_below = res[-1]["id"]
            if chosen: break
        d = os.path.join(out, sid); os.makedirs(d, exist_ok=True)
        for c in chosen:
            fn = os.path.join(d, f"{c['obs']}_{c['photo']}.jpg")
            if dl((c["url"], fn)): c["file"] = os.path.relpath(fn, out); rows.append(c)
        print(sid, "candidatas vistas", vistos, "escolhidas", len(chosen), flush=True)
    with open(os.path.join(out, "meta.jsonl"), "w") as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("total", len(rows))


def avaliar(model, index_path, species_json, data, out_path):
    import onnxruntime as ort
    sess = ort.InferenceSession(model, providers=["CPUExecutionProvider"])
    idx = read_index(index_path)
    h, text, refs, cat, _ = idx
    sid2pos = {h["labels"][lab]["id"]: i for i, lab in enumerate(cat)}
    pos2sid = {v: k for k, v in sid2pos.items()}
    meta = [json.loads(l) for l in open(os.path.join(data, "campo", "meta.jsonl"))]
    X = np.stack([sess.run(None, {"pixel_values": preprocess(os.path.join(data, "campo", m["file"]))})[0][0] for m in meta]).astype(np.float32)
    # cópias de referência do índice ou de foto do teste principal
    z = np.load(os.path.join(data, "emb_test.npz")); Xt = z["X"].astype(np.float32)
    ref_files = [l.strip() for l in open(os.path.join(data, "refs_files.txt")) if l.strip()]
    other_h = [dhash(f) for f in ref_files] + [dhash(os.path.join(data, "test", f)) for f in z["files"]]
    cos = np.maximum((X @ refs.T).max(1), (X @ Xt.T).max(1))
    keep = []
    for i, m in enumerate(meta):
        hh = dhash(os.path.join(data, "campo", m["file"]))
        if cos[i] >= 0.99 or any(bin(hh ^ o).count("1") <= 6 for o in other_h): m["descartada"] = "cópia"; continue
        keep.append(i)
    dropped = [m for m in meta if "descartada" in m]
    meta = [meta[i] for i in keep]; X = X[keep]
    order, prob, in_cat, conf = score(X, idx)
    y = np.array([sid2pos[m["species"]] for m in meta])
    t1 = order[:, 0] == y; t3 = (order[:, :3] == y[:, None]).any(1); acc = conf >= h["threshold"]
    qg = np.array([m["quality_grade"] for m in meta])

    def bloco(mask):
        n = int(mask.sum())
        return {"n": n, "top1": prop(t1[mask].sum(), n), "top3": prop(t3[mask].sum(), n),
                "aceitas_no_limiar": prop(acc[mask].sum(), n), "acerto_entre_aceitas": prop((t1 & acc & mask).sum(), (acc & mask).sum())}

    allm = np.ones(len(meta), bool)
    res = {"rotulo": "MINI TESTE: fotos de qualidade inferior (iNaturalist casual/needs_id), espécies-chave",
           "n_fotos": len(meta), "descartadas_por_copia": len(dropped), "especies": len({m["species"] for m in meta}),
           "geral": bloco(allm), "casual": bloco(qg == "casual"), "needs_id": bloco(qg == "needs_id"),
           "por_especie": {s: {"n": int((np.array([m["species"] for m in meta]) == s).sum()),
                               "top1_acertos": int(t1[np.array([m["species"] for m in meta]) == s].sum())}
                           for s in sorted({m["species"] for m in meta})},
           "fotos": [{"obs": m["obs"], "foto": m["photo"], "especie": m["species"], "grau": m["quality_grade"],
                      "cultivada": m["captive"], "identificadores_concordantes": m["identificadores_concordantes"],
                      "criada_em": m["created_at"][:10], "licenca": m["license"], "credito": m["attribution"],
                      "top3": [pos2sid[o] for o in order[i, :3]], "confianca": round(float(conf[i]), 4)}
                     for i, m in enumerate(meta)]}
    json.dump(res, open(out_path, "w"), ensure_ascii=False, indent=1)
    for k in ("geral", "casual", "needs_id"):
        b = res[k]; print(k, b["n"], b["top1"]["p"], b["top1"]["ic95"], b["top3"]["p"], b["top3"]["ic95"], b["aceitas_no_limiar"]["p"], b["acerto_entre_aceitas"]["p"])


if __name__ == "__main__":
    if sys.argv[1] == "fetch": fetch(*sys.argv[2:4])
    else: avaliar(*sys.argv[2:7])
