"""Baixa fotos de plantas FORA da base (para medir falso positivo).

Uso: python fetch_ood.py <species.json> <dir_dados> <arquivo_exclusao.txt> [alvo=300]

Amostra aleatória de observações "research grade" de plantas (Plantae,
taxon 47126) no Brasil, identificadas até espécie, observadas a partir de 2025-01-01.
Descarta espécies da base (nome aceito ou sinônimo), observações da lista de exclusão,
e mantém no máximo 1 observação por espécie e 1 por observador.
Aleatoriedade: cada consulta pede as 200 observações com ID imediatamente abaixo de um ID sorteado
(semente fixa SEED) entre 250.000.000 e o maior ID existente; apenas a primeira observação
aceitável de cada consulta entra, para espalhar a amostra no tempo e no espaço.
"""
import json, os, random, sys, time, requests, concurrent.futures as cf

SPECIES_JSON, OUT, EXCL = sys.argv[1:4]
TARGET = int(sys.argv[4]) if len(sys.argv) > 4 else 300
API = "https://api.inaturalist.org/v1/observations"
SEED = 20251105
H = {"User-Agent": "saberia-eval/1.0 (avaliacao academica; 1 req/s)"}


def main():
    db = json.load(open(SPECIES_JSON))["species"]
    base = set()
    for s in db:
        for n in [s["scientific_name"]] + s["synonyms"]:
            base.add(" ".join(n.replace("×", "x").lower().split()[:2]))
    excl = {int(x) for x in open(EXCL).read().split()}
    os.makedirs(OUT, exist_ok=True)
    chosen, species, observers = [], set(), set()
    rng = random.Random(SEED)
    top = requests.get(API, params={"per_page": 1, "order_by": "id", "order": "desc"}, headers=H, timeout=60).json()["results"][0]["id"]
    calls = 0
    while len(chosen) < TARGET and calls < 4 * TARGET:
        calls += 1
        p = {"taxon_id": 47126, "place_id": 6878, "quality_grade": "research", "photos": "true", "rank": "species",
             "d1": "2025-01-01", "per_page": 200, "order_by": "id", "order": "desc",
             "id_below": rng.randint(250_000_000, top)}
        try:
            res = requests.get(API, params=p, headers=H, timeout=60).json().get("results", [])
        except Exception:
            time.sleep(10); continue
        for o in res:
            if len(chosen) >= TARGET: break
            t = o.get("taxon") or {}
            name = t.get("name", "")
            key = " ".join(name.replace("×", "x").lower().split()[:2])
            uid = o.get("user", {}).get("id")
            if not o.get("photos") or key in base or key in species or uid in observers or o["id"] in excl:
                continue
            ph = o["photos"][0]
            species.add(key); observers.add(uid)
            chosen.append({"obs": o["id"], "photo": ph["id"], "taxon": name,
                           "observed_on": o.get("observed_on"), "user_id": uid, "license": ph.get("license_code"),
                           "attribution": ph.get("attribution"), "place": o.get("place_guess"),
                           "url": ph["url"].replace("square", "medium")})
            break
        time.sleep(1.1)

    def dl(c):
        fn = os.path.join(OUT, f"{c['obs']}_{c['photo']}.jpg")
        for attempt in range(3):
            try:
                r = requests.get(c["url"], headers=H, timeout=60)
                if r.status_code == 200 and len(r.content) > 2000:
                    open(fn, "wb").write(r.content); c["file"] = os.path.basename(fn); return True
            except Exception:
                pass
            time.sleep(3)
        return False
    with cf.ThreadPoolExecutor(6) as ex:
        oks = list(ex.map(dl, chosen))
    with open(os.path.join(OUT, "meta.jsonl"), "w") as f:
        for c, ok in zip(chosen, oks):
            if ok: f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print("fora da base:", sum(oks), "fotos,", len(species), "espécies", flush=True)


if __name__ == "__main__":
    main()
