"""Baixa fotos candidatas a referência (licença livre) para espécies fracas, sem vazamento para o teste.

Uso: python fetch_refs_novas.py <species.json> <dir_dados> <especie1,especie2,...> [max_obs_por_especie]
Grava <dir_dados>/refs_novas/<especie>/<obs>_<foto>.jpg e <dir_dados>/refs_novas_attr.json
(mesmo formato de refs2_attr.json, usado por melhorar_refs.py).

Regras:
- grau "pesquisa", foto com licença CC0, CC-BY ou CC-BY-SA (nada NC, nada "todos os direitos reservados");
- observação fora do teste, do conjunto fora da base, do mini teste, das referências do índice e da calibração
  (<dir_dados>/exclude_obs.txt);
- observador SEM nenhuma foto no teste (nem no mini teste) da mesma espécie: evita referência do mesmo pé de planta
  fotografado em outro dia pela mesma pessoa;
- 1 observação por observador; até 3 fotos por observação (partes diferentes da planta: tronco, folha, flor, fruto);
- ordem: mais votadas primeiro, depois as mais recentes (variedade de fotógrafos e de situações).
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_test import api, dl

FREE = "cc0,cc-by,cc-by-sa"


def main():
    species_json, data, species = sys.argv[1:4]
    max_obs = int(sys.argv[4]) if len(sys.argv) > 4 else 40
    db = {s["id"]: s for s in json.load(open(species_json))["species"]}
    excl = {int(x) for x in open(os.path.join(data, "exclude_obs.txt")).read().split()}
    test_users = {}
    for split in ("test", "ood", "campo"):
        p = os.path.join(data, split, "meta.jsonl")
        if not os.path.exists(p): continue
        for l in open(p):
            m = json.loads(l); excl.add(m["obs"])
            if m.get("user_id"): test_users.setdefault(m.get("species"), set()).add(m["user_id"])
    attr_path = os.path.join(data, "refs_novas_attr.json")
    attr = json.load(open(attr_path)) if os.path.exists(attr_path) else {}
    for sp in species.split(","):
        s = db[sp]
        blocked = test_users.get(sp, set())
        cands, users = [], set()
        for order_by in ("votes", "id"):
            for page in (1, 2, 3):
                if len(cands) >= max_obs: break
                res = api({"taxon_name": s["scientific_name"], "quality_grade": "research", "photos": "true",
                           "photo_license": FREE, "per_page": 200, "page": page, "order_by": order_by, "order": "desc"}).get("results", [])
                for o in res:
                    uid = o.get("user", {}).get("id")
                    if len(cands) >= max_obs: break
                    if o["id"] in excl or uid in blocked or uid in users: continue
                    if any(c["id"] == o["id"] for c in cands): continue
                    users.add(uid); cands.append(o)
                if len(res) < 200: break
        d = os.path.join(data, "refs_novas", sp); os.makedirs(d, exist_ok=True)
        n = 0
        for o in cands:
            for ph in o["photos"][:3]:
                if ph.get("license_code") not in FREE.split(","): continue
                key = f"{o['id']}_{ph['id']}"
                fn = os.path.join(d, key + ".jpg")
                if key not in attr and not dl((ph["url"].replace("square", "medium"), fn)): continue
                attr[key] = {"id": sp, "obs": o["id"], "photo": ph["id"], "taxon": o["taxon"]["name"],
                             "license": ph.get("license_code"), "attribution": ph.get("attribution"),
                             "user_id": o["user"]["id"], "created_at": o.get("created_at"),
                             "url": f"https://www.inaturalist.org/photos/{ph['id']}"}
                n += 1
        print(sp, "observadores bloqueados (estão no teste)", len(blocked), "observações novas", len(cands), "fotos", n, flush=True)
    json.dump(attr, open(attr_path, "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
