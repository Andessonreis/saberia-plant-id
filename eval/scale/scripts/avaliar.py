"""Avaliação do classificador do app com as mesmas regras do PlantClassifier.kt.

Uso:
  python avaliar.py embed   <modelo.onnx> <dir_dados>               # calcula e guarda os vetores das fotos
  python avaliar.py metrics <plant-index.bin> <species.json> <dir_dados> <saida.json> [refs_meta.json] [dir_fotos_referencia]

As predições por foto vão para <saida>_predicoes.json (a comparação com a nuvem usa <dir_dados>/metricas_app_predicoes.json).
<dir_dados> tem test/meta.jsonl (+ fotos) e ood/meta.jsonl (+ fotos), gerados por fetch_test.py e fetch_ood.py.

Pré-processamento idêntico ao app (PlantClassifier.decode/embed):
  - orientação EXIF: só rotações de 90/180/270 graus (o app ignora espelhamentos);
  - inSampleSize: maior potência de 2 com min(lado)/(2*amostra) >= 2*224, aplicada na decodificação JPEG
    (redução por DCT, como o BitmapFactory);
  - Bitmap.createScaledBitmap(filter=true): interpolação bilinear sem suavização (cv2.INTER_LINEAR);
  - recorte central 224x224; normalização (x/255 - média)/desvio, canais RGB.
Pontuação idêntica a PlantClassifier.score (float32, vetores do índice em float16).
"""
import json, math, os, sys, collections
import numpy as np


# ---------------------------------------------------------------- índice e pontuação do app
def read_index(path):
    raw = open(path, "rb").read()
    n = int.from_bytes(raw[:4], "little")
    h = json.loads(raw[4:4 + n].decode())
    v = np.frombuffer(raw[4 + n:], dtype="<f2").astype(np.float32).reshape(-1, h["dim"])
    L = len(h["labels"])
    text, refs = v[:L], v[L:L + len(h["refs"])]
    cat = np.array([i for i, l in enumerate(h["labels"]) if l.get("id")])
    by_label = collections.defaultdict(list)
    for j, lab in enumerate(h["refs"]): by_label[lab].append(j)
    return h, text, refs, cat, {k: np.array(v) for k, v in by_label.items()}


def softmax(x, scale):
    z = (x - x.max(axis=-1, keepdims=True)) * np.float32(scale)
    e = np.exp(z.astype(np.float64)).astype(np.float32)
    return e / e.sum(axis=-1, keepdims=True)


def score(X, idx):
    """Devolve (ordem dos candidatos da base [n, C], prob [n, C], inCatalog [n], confiança [n])."""
    h, text, refs, cat, by_label = idx
    t = X @ text.T
    in_cat = softmax(t, h["scale"])[:, cat].sum(1)
    sims = X @ refs.T
    comb = np.empty((len(X), len(cat)), np.float32)
    for i, lab in enumerate(cat):
        r = by_label.get(lab)
        vis = np.zeros(len(X), np.float32) if r is None else -np.sort(-sims[:, r], axis=1)[:, :h["k"]].mean(1)
        comb[:, i] = t[:, lab] + np.float32(h["weight"]) * vis
    prob = softmax(comb, h["scale"] / (1 + h["weight"]))
    order = np.argsort(-prob, axis=1, kind="stable")
    conf = prob[np.arange(len(X)), order[:, 0]] * in_cat
    return order, prob, in_cat, conf


# ---------------------------------------------------------------- pré-processamento do app
MEAN = np.array([0.48145466, 0.4578275, 0.40821073], np.float32)
STD = np.array([0.26862954, 0.26130258, 0.27577711], np.float32)


def preprocess(path, size=224):
    import cv2
    from PIL import Image
    im = Image.open(path)
    W, H = im.size
    sample = 1
    while min(W, H) // (sample * 2) >= size * 2: sample *= 2
    orient = 1
    try: orient = im.getexif().get(0x0112, 1)
    except Exception: pass
    if sample > 1 and im.format == "JPEG": im.draft("RGB", (W // sample, H // sample))
    im = im.convert("RGB")
    if sample > 1 and im.size[0] > W // sample + 1: im = im.reduce(sample)
    rot = {3: 180, 6: 270, 8: 90}.get(orient)  # PIL gira no sentido anti-horário
    if rot: im = im.rotate(rot, expand=True)
    a = np.asarray(im)
    s = size / min(a.shape[1], a.shape[0])
    w, h = max(size, round(a.shape[1] * s)), max(size, round(a.shape[0] * s))
    a = cv2.resize(a, (w, h), interpolation=cv2.INTER_LINEAR)
    l, t = (w - size) // 2, (h - size) // 2
    a = a[t:t + size, l:l + size].astype(np.float32) / 255
    return ((a - MEAN) / STD).transpose(2, 0, 1)[None]


def cmd_embed(model, data):
    import onnxruntime as ort
    so = ort.SessionOptions(); so.intra_op_num_threads = os.cpu_count()
    so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    sess = ort.InferenceSession(model, so, providers=["CPUExecutionProvider"])
    for split in ("test", "ood"):
        meta = [json.loads(l) for l in open(os.path.join(data, split, "meta.jsonl"))]
        cache = os.path.join(data, f"emb_{split}.npz")
        have = {}
        if os.path.exists(cache):
            z = np.load(cache); have = dict(zip(z["files"], z["X"]))
        files = [m["file"] for m in meta]
        for i, f in enumerate(files):
            if f in have: continue
            have[f] = sess.run(None, {"pixel_values": preprocess(os.path.join(data, split, f))})[0][0]
            if i % 200 == 0:
                print(split, i, len(files), flush=True)
                np.savez(cache, files=np.array(list(have)), X=np.stack(list(have.values())))
        np.savez(cache, files=np.array(list(have)), X=np.stack(list(have.values())))
        print(split, "ok", len(have), flush=True)


# ---------------------------------------------------------------- estatística
Z = 1.959963984540054


def wilson(k, n):
    if n == 0: return [None, None]
    p = k / n; d = 1 + Z * Z / n
    c = (p + Z * Z / (2 * n)) / d; m = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / d
    return [round(max(0.0, c - m), 4), round(min(1.0, c + m), 4)]


def prop(k, n):
    return {"k": int(k), "n": int(n), "p": round(k / n, 4) if n else None, "ic95": wilson(k, n)}


def macro_boot(per, seed=20251105, reps=2000):
    """Média das taxas por espécie, com IC 95% por bootstrap estratificado (reamostra fotos dentro de cada espécie)."""
    rng = np.random.default_rng(seed)
    arrs = [np.array(v, float) for v in per.values() if len(v)]
    est = float(np.mean([a.mean() for a in arrs]))
    bs = [np.mean([rng.choice(a, len(a)).mean() for a in arrs]) for _ in range(reps)]
    return {"media": round(est, 4), "ic95": [round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)],
            "especies": len(arrs), "bootstrap": reps, "seed": seed}


# ---------------------------------------------------------------- métricas
def genus_sets(db):
    return {s["id"]: {n.split()[0].lower() for n in [s["scientific_name"]] + s["synonyms"]} for s in db}


def load_split(data, split):
    meta = [json.loads(l) for l in open(os.path.join(data, split, "meta.jsonl"))]
    z = np.load(os.path.join(data, f"emb_{split}.npz"))
    emb = dict(zip(z["files"], z["X"]))
    meta = [m for m in meta if m["file"] in emb]
    return meta, np.stack([emb[m["file"]] for m in meta]).astype(np.float32)


def dhash(path, n=8):
    from PIL import Image
    im = Image.open(path).convert("L").resize((n + 1, n), Image.BILINEAR)
    a = np.asarray(im, np.int16)
    return int("".join("1" if x else "0" for x in (a[:, 1:] > a[:, :-1]).ravel()), 2)


def dedupe(meta, X, refs, ref_hashes, cos_thr=0.99, ham_thr=6):
    """Remove duplicatas reais: mesma imagem (ou recorte/recompressão) de uma referência do índice ou de
    outra foto do teste. Critério: dHash de 64 bits com distância de Hamming <= ham_thr, ou cosseno >= cos_thr.
    (Cosseno 0,95-0,98 foi inspecionado visualmente: são fotos diferentes da mesma espécie, não duplicatas.)"""
    hs = [dhash(m["_path"]) for m in meta]
    vs_ref = (X @ refs.T).max(1)
    G = X @ X.T
    ham = lambda a, b: bin(a ^ b).count("1")
    keep, dropped = [], []
    for i, m in enumerate(meta):
        why = None
        if vs_ref[i] >= cos_thr: why = f"quase igual a referência do índice (cos={vs_ref[i]:.3f})"
        else:
            r = next((h for h in ref_hashes if ham(hs[i], h) <= ham_thr), None)
            if r is not None: why = "mesma imagem que uma referência do índice (dHash)"
            else:
                prev = next((j for j in keep if G[i, j] >= cos_thr or ham(hs[i], hs[j]) <= ham_thr), None)
                if prev is not None: why = f"mesma imagem que outra foto do teste ({meta[prev]['file']})"
        if why: dropped.append({"file": m["file"], "motivo": why})
        else: keep.append(i)
    return keep, dropped


def cmd_metrics(index_path, species_json, data, out_path, refs_meta=None, refs_dir=None):
    idx = read_index(index_path)
    import glob
    ref_hashes = [dhash(f) for f in sorted(glob.glob(os.path.join(refs_dir, "*", "*.jpg")))] if refs_dir else []
    h, text, refs, cat, _ = idx
    thr = h["threshold"]
    db = json.load(open(species_json))["species"]
    sid2pos = {h["labels"][lab]["id"]: i for i, lab in enumerate(cat)}
    gen = genus_sets(db)
    names = {s["id"]: s["scientific_name"] for s in db}
    pos2sid = {v: k for k, v in sid2pos.items()}
    distractors = {l["name"].lower() for l in h["labels"] if not l.get("id")}

    meta, X = load_split(data, "test")
    for m in meta: m["_path"] = os.path.join(data, "test", m["file"])
    keep, dropped = dedupe(meta, X, refs, ref_hashes)
    meta = [meta[i] for i in keep]; X = X[keep]
    y = np.array([sid2pos[m["species"]] for m in meta])
    order, prob, in_cat, conf = score(X, idx)
    t1 = order[:, 0] == y
    t3 = (order[:, :3] == y[:, None]).any(1)
    acc = conf >= thr
    g1 = np.array([bool(gen[pos2sid[o]] & gen[m["species"]]) for o, m in zip(order[:, 0], meta)])

    meta_o, Xo = load_split(data, "ood")
    for m in meta_o: m["_path"] = os.path.join(data, "ood", m["file"])
    keep_o, dropped_o = dedupe(meta_o, Xo, refs, ref_hashes)
    meta_o = [meta_o[i] for i in keep_o]; Xo = Xo[keep_o]
    order_o, _, in_cat_o, conf_o = score(Xo, idx)
    acc_o = conf_o >= thr
    in_dis = np.array([m["taxon"].lower() in distractors for m in meta_o])
    base_genera = set().union(*gen.values())
    cong = np.array([m["taxon"].split()[0].lower() in base_genera for m in meta_o])

    ref_auth = set()
    if refs_meta:
        for r in json.load(open(refs_meta)):
            a = (r.get("attribution") or "").split(",")[0].replace("(c)", "").strip().lower()
            if a: ref_auth.add(a)
    auth = np.array([(m.get("attribution") or "").split(",")[0].replace("(c)", "").strip().lower() for m in meta])
    same_obs = np.array([a in ref_auth for a in auth])

    def block(mask):
        n = int(mask.sum()); a = acc & mask
        return {
            "n": n,
            "top1": prop(t1[mask].sum(), n),
            "top3": prop(t3[mask].sum(), n),
            "top1_genero": prop(g1[mask].sum(), n),
            "no_limiar": {
                "aceitas": prop(a.sum(), n),
                "acerto_entre_aceitas": prop((t1 & a).sum(), a.sum()),
                "erro_entre_aceitas": prop((~t1 & a).sum(), a.sum()),
                "acerto_e_aceita_sobre_total": prop((t1 & a).sum(), n),
                "recusadas": prop((~a & mask).sum(), n),
            },
        }

    sp_ids = sorted({m["species"] for m in meta}, key=lambda s: names[s])
    sp_arr = np.array([m["species"] for m in meta])
    from fetch_test import CHAVE
    chave = np.array([s in CHAVE for s in sp_arr])
    per = {}
    for s in sp_ids:
        mk = sp_arr == s
        b = block(mk)
        conf_mat = collections.Counter(pos2sid[o] for o in order[mk, 0][~t1[mk]])
        b.update({"nome": names[s], "chave": s in CHAVE,
                  "confusoes_mais_comuns": [{"especie": names[k], "n": v} for k, v in conf_mat.most_common(3)]})
        per[s] = b
    lic = collections.Counter(m["license"] or "sem-licenca-aberta" for m in meta)
    win = collections.Counter(m["window"] for m in meta)
    res = {
        "limiar_app": thr,
        "teste_na_base": {
            "fotos": len(meta), "especies": len(sp_ids),
            "removidas_por_duplicata": len(dropped), "duplicatas": dropped,
            "licencas": dict(lic), "periodo_observacao": dict(win),
            "geral_micro": block(np.ones(len(meta), bool)),
            "geral_macro_top1": macro_boot({s: t1[sp_arr == s] for s in sp_ids}),
            "geral_macro_top3": macro_boot({s: t3[sp_arr == s] for s in sp_ids}),
            "especies_chave": block(chave),
            "especies_chave_macro_top1": macro_boot({s: t1[sp_arr == s] for s in sp_ids if s in CHAVE}),
            "demais_especies": block(~chave),
            "sensibilidade_observador_tambem_nas_referencias": {
                "observador_nas_referencias": block(same_obs), "observador_novo": block(~same_obs)},
            "por_especie": per,
        },
        "fora_da_base": {
            "fotos": len(meta_o), "especies": len({m["taxon"] for m in meta_o}),
            "removidas_por_duplicata": len(dropped_o),
            "falso_positivo_no_limiar": prop(acc_o.sum(), len(meta_o)),
            "falso_positivo_especie_esta_na_lista_de_distratores": prop((acc_o & in_dis).sum(), in_dis.sum()),
            "falso_positivo_especie_fora_da_lista_de_distratores": prop((acc_o & ~in_dis).sum(), (~in_dis).sum()),
            "falso_positivo_mesmo_genero_de_especie_da_base": prop((acc_o & cong).sum(), cong.sum()),
            "falso_positivo_genero_ausente_da_base": prop((acc_o & ~cong).sum(), (~cong).sum()),
            "aceitas_exemplos": [{"taxon": m["taxon"], "previsto": names[pos2sid[o]], "confianca": round(float(c), 3)}
                                 for m, o, c in zip(meta_o, order_o[:, 0], conf_o) if c >= thr],
        },
    }
    # predições por foto, para a comparação com outros sistemas na mesma amostra
    preds = [{"file": m["file"], "species": m["species"], "top3": [pos2sid[o] for o in order[i, :3]],
              "conf": round(float(conf[i]), 4), "aceita": bool(acc[i])} for i, m in enumerate(meta)]
    preds_o = [{"file": m["file"], "taxon": m["taxon"], "top1": pos2sid[order_o[i, 0]], "conf": round(float(conf_o[i]), 4),
                "aceita": bool(acc_o[i])} for i, m in enumerate(meta_o)]
    json.dump({"test": preds, "ood": preds_o}, open(os.path.splitext(out_path)[0] + "_predicoes.json", "w"), ensure_ascii=False)
    json.dump(res, open(out_path, "w"), ensure_ascii=False, indent=1)
    g = res["teste_na_base"]["geral_micro"]
    print("fotos", len(meta), "top1", g["top1"], "top3", g["top3"], "FP", res["fora_da_base"]["falso_positivo_no_limiar"])


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    if sys.argv[1] == "embed": cmd_embed(*sys.argv[2:4])
    elif sys.argv[1] == "metrics": cmd_metrics(*sys.argv[2:])
