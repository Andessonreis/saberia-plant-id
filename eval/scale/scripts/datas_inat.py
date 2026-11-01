"""Baixa do iNaturalist a data de criação (envio) de cada observação e de cada foto do conjunto de teste.

Uso: python datas_inat.py <dir_dados>
Grava <dir_dados>/test/datas_inat.json: {obs_id: {"obs_created_at", "observed_on", "photo_created_at"?}}

- created_at da observação vem de /v1/observations (200 por requisição).
- A data de envio da foto não sai nessa API; usamos o fato de que os IDs de foto do iNaturalist
  são sequenciais no tempo: a data de envio da foto é estimada pelo created_at da observação
  e conferida pela ordem dos IDs (ver contaminacao.py).
"""
import json, os, sys, time, urllib.request

API = "https://api.inaturalist.org/v1/observations?per_page=200&fields=id,created_at,observed_on,updated_at&id="


def get(url):
    for t in range(5):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "saberia-avaliacao/1.0"})
            return json.load(urllib.request.urlopen(req, timeout=60))
        except Exception as e:
            print("erro", e, "tentativa", t + 1, flush=True); time.sleep(5 * (t + 1))
    raise SystemExit("falhou: " + url)


def main():
    data = sys.argv[1]
    out = os.path.join(data, "test", "datas_inat.json")
    res = json.load(open(out)) if os.path.exists(out) else {}
    obs = [json.loads(l)["obs"] for l in open(os.path.join(data, "test", "meta.jsonl"))]
    todo = [o for o in obs if str(o) not in res]
    for i in range(0, len(todo), 200):
        chunk = todo[i:i + 200]
        r = get(API + ",".join(map(str, chunk)))
        for o in r["results"]:
            res[str(o["id"])] = {"obs_created_at": o.get("created_at"), "observed_on": o.get("observed_on")}
        print(f"{min(i + 200, len(todo))}/{len(todo)}", flush=True)
        time.sleep(1.2)
    json.dump(res, open(out, "w"))
    print("faltando:", len([o for o in obs if str(o) not in res]))


if __name__ == "__main__":
    main()
