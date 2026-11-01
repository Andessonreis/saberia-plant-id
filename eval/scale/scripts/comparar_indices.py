"""Compara o índice publicado com índices candidatos nas MESMAS fotos de teste (pareado).

Uso: python comparar_indices.py <saida.json> nome=<metricas.json> [nome=<metricas.json> ...]
O primeiro é a linha de base. Cada <metricas.json> tem ao lado o <metricas>_predicoes.json gerado por avaliar.py.
Reporta top-1/top-3/limiar geral, espécies-chave, as 3 espécies-alvo, fora da base, as espécies que pioraram
e o teste de McNemar exato (fotos que mudaram de certo para errado e vice-versa).
"""
import json, math, os, sys

ALVO = ["astronium_urundeuva", "erythrina_velutina", "commiphora_leptophloeos"]


def mcnemar(b, c):
    n = b + c
    if n == 0: return 1.0
    k = min(b, c)
    p = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return round(min(1.0, 2 * p), 4)


def main():
    out = sys.argv[1]
    runs = [a.split("=", 1) for a in sys.argv[2:]]
    base_name = runs[0][0]
    data = {}
    for name, path in runs:
        met = json.load(open(path))
        pred = json.load(open(os.path.splitext(path)[0] + "_predicoes.json"))["test"]
        data[name] = (met, {p["file"]: p for p in pred})
    bmet, bpred = data[base_name]
    res = {"linha_de_base": base_name, "indices": {}}
    for name, (met, pred) in data.items():
        tb = met["teste_na_base"]
        assert set(pred) == set(bpred), "conjuntos de teste diferentes"
        r = {"geral": {k: tb["geral_micro"][k] for k in ("n", "top1", "top3")} | {"no_limiar": tb["geral_micro"]["no_limiar"]},
             "especies_chave": {k: tb["especies_chave"][k] for k in ("n", "top1", "top3")},
             "demais_especies": {k: tb["demais_especies"][k] for k in ("n", "top1", "top3")},
             "fora_da_base_falso_positivo": met["fora_da_base"]["falso_positivo_no_limiar"],
             "alvo": {s: {k: tb["por_especie"][s][k] for k in ("n", "top1", "top3")} for s in ALVO}}
        if name != base_name:
            t1 = lambda P, f: P[f]["top3"][0] == P[f]["species"]
            ganhou = [f for f in pred if t1(pred, f) and not t1(bpred, f)]
            perdeu = [f for f in pred if not t1(pred, f) and t1(bpred, f)]
            r["pareado_top1"] = {"erradas_que_viraram_certas": len(ganhou), "certas_que_viraram_erradas": len(perdeu),
                                 "mcnemar_p": mcnemar(len(ganhou), len(perdeu))}
            piorou = {}
            for s, v in tb["por_especie"].items():
                b = bmet["teste_na_base"]["por_especie"][s]["top1"]["k"]
                if v["top1"]["k"] < b: piorou[s] = {"antes": b, "depois": v["top1"]["k"], "n": v["n"]}
            r["especies_que_pioraram_top1"] = piorou
            r["fotos_que_viraram_erradas"] = [{"foto": f, "especie": pred[f]["species"], "antes": bpred[f]["top3"][0],
                                               "depois": pred[f]["top3"][0]} for f in perdeu]
        res["indices"][name] = r
    json.dump(res, open(out, "w"), ensure_ascii=False, indent=1)
    for name, r in res["indices"].items():
        g = r["geral"]
        print(name, "top1", g["top1"]["k"], g["top1"]["p"], "top3", g["top3"]["k"], "aceitas", g["no_limiar"]["aceitas"]["p"],
              "acerto_aceitas", g["no_limiar"]["acerto_entre_aceitas"]["p"], "chave", r["especies_chave"]["top1"]["p"],
              "FP", r["fora_da_base_falso_positivo"]["k"],
              {s[:9]: (v["top1"]["k"], v["n"], v["top3"]["k"]) for s, v in r["alvo"].items()},
              r.get("pareado_top1"), r.get("especies_que_pioraram_top1"))


if __name__ == "__main__":
    main()
