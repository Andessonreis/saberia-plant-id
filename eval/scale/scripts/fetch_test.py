"""Baixa o conjunto de teste (fotos de espécies da base) do iNaturalist.

Uso: python fetch_test.py <species.json> <dir_dados> <arquivo_exclusao.txt>

- <species.json>: data/caatinga_species.json (deste repositório)
- <dir_dados>: onde as fotos e o meta.jsonl são gravados (fora do repositório)
- <arquivo_exclusao.txt>: IDs de observação (um por linha) que NÃO podem entrar no teste
  (fotos de referência do índice e fotos usadas antes para calibrar o limiar)

Regras de amostragem (iguais para todas as espécies):
- observações "research grade" com foto, nome aceito ou sinônimo da base;
- 1 foto por observação (a primeira, que é a principal do observador);
- no máximo 1 observação por observador por espécie;
- preferência: observadas a partir de 2025-01-01; depois, anteriores (até 3x o alvo de candidatas, mais recentes primeiro);
  dentro de cada período, licença CC0/CC-BY/CC-BY-SA, depois CC-BY-NC(-SA), depois sem licença aberta;
- alvo de N_CHAVE fotos para as espécies-chave e N_OUTRAS para as demais; se não houver, fica o n real.
"""
import json, os, sys, time, requests, concurrent.futures as cf

N_CHAVE, N_OUTRAS = 100, 30
CHAVE = {"sarcomphalus_joazeiro", "cereus_jamacaru", "spondias_tuberosa", "astronium_urundeuva", "erythrina_velutina",
         "commiphora_leptophloeos", "mimosa_tenuiflora", "sideroxylon_obtusifolium", "aloe_vera", "lippia_alba",
         "coleus_barbatus", "cenostigma_pyramidale", "xiquexique_gounellei", "amburana_cearensis", "anadenanthera_colubrina",
         "libidibia_ferrea", "cymbopogon_citratus", "handroanthus_impetiginosus", "jatropha_mollissima",
         "opuntia_ficus_indica", "melocactus_zehntneri", "schinus_terebinthifolia"}
API = "https://api.inaturalist.org/v1/observations"
H = {"User-Agent": "saberia-eval/1.0 (avaliacao academica; 1 req/s)"}
FREE, NC = "cc0,cc-by,cc-by-sa", "cc-by-nc,cc-by-nc-sa"
WINDOWS = [{"d1": "2025-01-01"}, {"d2": "2024-12-31"}]
_last = [0.0]


def api(params):
    for attempt in range(6):
        wait = 1.05 - (time.time() - _last[0])
        if wait > 0: time.sleep(wait)
        _last[0] = time.time()
        try:
            r = requests.get(API, params=params, headers=H, timeout=60)
            if r.status_code == 429 or r.status_code >= 500:
                time.sleep(10 * (attempt + 1)); continue
            return r.json()
        except Exception:
            time.sleep(5 * (attempt + 1))
    return {"results": [], "total_results": 0}


def tier(lic):
    return 0 if lic in FREE.split(",") else 1 if lic in NC.split(",") else 2


def dl(job):
    url, fn = job
    for attempt in range(3):
        try:
            r = requests.get(url, headers=H, timeout=60)
            if r.status_code == 200 and len(r.content) > 2000:
                open(fn, "wb").write(r.content); return True
        except Exception:
            pass
        time.sleep(3 * (attempt + 1))
    return False


def main():
    SPECIES_JSON, OUT, EXCL = sys.argv[1:4]
    db = json.load(open(SPECIES_JSON))["species"]
    excl = {int(x) for x in open(EXCL).read().split()}
    meta_path = os.path.join(OUT, "meta.jsonl")
    done_marks = {f[:-5] for f in os.listdir(OUT) if f.endswith(".done")} if os.path.isdir(OUT) else set()
    os.makedirs(OUT, exist_ok=True)
    # observações já usadas por outra espécie (não deve ocorrer, mas evita duplicar entre classes)
    used_obs = set()
    if os.path.exists(meta_path):
        used_obs = {json.loads(l)["obs"] for l in open(meta_path)}
    for s in db:
        sid = s["id"]
        if sid in done_marks: continue
        target = N_CHAVE if sid in CHAVE else N_OUTRAS
        names = [s["scientific_name"]] + s["synonyms"]
        ok_names = {n.replace("×", "x").lower() for n in names}
        def match(tname):
            t = tname.replace("×", "x").lower()
            return any(t == n or t.startswith(n + " ") for n in ok_names)
        chosen, observers = [], set()
        for wi, win in enumerate(WINDOWS):
            if len(chosen) >= target: break
            # candidatos do período (mais recentes primeiro); a licença é ordenada localmente
            cands, seen = [], set()
            for name in names:
                id_below, found = None, False
                for page in range(4):
                    p = {"taxon_name": name.replace("×", "x"), "quality_grade": "research", "photos": "true",
                         "per_page": 200, "order_by": "id", "order": "desc", **win}
                    if id_below: p["id_below"] = id_below
                    res = api(p).get("results", [])
                    for o in res:
                        if o["id"] in seen or o["id"] in excl or o["id"] in used_obs: continue
                        if not o.get("photos") or not o.get("taxon") or not match(o["taxon"]["name"]): continue
                        seen.add(o["id"]); cands.append(o); found = True
                    if len(res) < 200 or len(cands) >= 3 * target: break
                    id_below = res[-1]["id"]
                if found: break  # o nome já foi resolvido pelo iNaturalist; sinônimos trariam as mesmas observações
            for want in (0, 1, 2):
                for o in cands:
                    if len(chosen) >= target: break
                    ph = o["photos"][0]
                    lc = ph.get("license_code")
                    uid = o.get("user", {}).get("id")
                    if tier(lc) != want or uid in observers or o["id"] in used_obs: continue
                    observers.add(uid); used_obs.add(o["id"])
                    chosen.append({"species": sid, "obs": o["id"], "photo": ph["id"], "taxon": o["taxon"]["name"],
                                   "observed_on": o.get("observed_on"), "user_id": uid,
                                   "user_login": o.get("user", {}).get("login"), "license": lc,
                                   "attribution": ph.get("attribution"), "place": o.get("place_guess"),
                                   "window": "2025+" if wi == 0 else "<=2024",
                                   "url": ph["url"].replace("square", "medium")})
        d = os.path.join(OUT, sid); os.makedirs(d, exist_ok=True)
        jobs = [(c["url"], os.path.join(d, f"{c['obs']}_{c['photo']}.jpg")) for c in chosen]
        with cf.ThreadPoolExecutor(6) as ex:
            oks = list(ex.map(dl, jobs))
        with open(meta_path, "a") as f:
            for c, ok, j in zip(chosen, oks, jobs):
                if ok:
                    c["file"] = os.path.relpath(j[1], OUT); f.write(json.dumps(c, ensure_ascii=False) + "\n")
        open(os.path.join(OUT, sid + ".done"), "w").close()
        print(sid, "alvo", target, "baixadas", sum(oks), flush=True)


if __name__ == "__main__":
    main()
