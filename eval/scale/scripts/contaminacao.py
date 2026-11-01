"""Sensibilidade à contaminação: desempenho por data de envio da observação ao iNaturalist.

Uso: python contaminacao.py <dir_dados> <saida.json>
Lê <dir_dados>/metricas_app_predicoes.json (predições por foto) e <dir_dados>/test/datas_inat.json (datas_inat.py).

Datas de corte dos dados de treino do BioCLIP-2 (TreeOfLife-200M, revisão a8f38b4, a usada no paper):
- GBIF (de onde vêm as fotos do iNaturalist): instantâneo de ocorrências de 2024-05-01 (DOI 10.15468/dl.bfv433);
- EOL (que também espelha fotos do iNaturalist): acessado em agosto de 2024.
Uma observação criada depois de 2024-08-31 não pode estar no treino (a foto não existia).
"""
import json, os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from avaliar import wilson
from fetch_test import CHAVE

GBIF = "2024-05-01"
EOL_FIM = "2024-09-01"  # primeiro dia depois de agosto de 2024


def prop(k, n):
    return {"k": int(k), "n": int(n), "p": round(k / n, 4) if n else None, "ic95": wilson(int(k), int(n))}


def faixa(created):
    d = created[:10]
    if d >= EOL_FIM: return "a"
    if d >= GBIF: return "b"
    return "c"


def main():
    data, out = sys.argv[1:3]
    pred = json.load(open(os.path.join(data, "metricas_app_predicoes.json")))["test"]
    datas = json.load(open(os.path.join(data, "test", "datas_inat.json")))
    rows = []
    for p in pred:
        obs = os.path.basename(p["file"]).split("_")[0]
        c = datas[obs]["obs_created_at"]
        rows.append((faixa(c), c[:10] >= "2025-01-01", p["species"] in CHAVE,
                     p["top3"][0] == p["species"], p["species"] in p["top3"], c[:10]))
    F = np.array([r[0] for r in rows]); y25 = np.array([r[1] for r in rows]); ch = np.array([r[2] for r in rows])
    t1 = np.array([r[3] for r in rows]); t3 = np.array([r[4] for r in rows])

    def bloco(mask):
        n = int(mask.sum())
        return {"n": n, "top1": prop(t1[mask].sum(), n), "top3": prop(t3[mask].sum(), n)}

    def tudo(mask):
        return {"geral": bloco(mask), "especies_chave": bloco(mask & ch)}

    nomes = {
        "a": f"criadas no iNaturalist a partir de {EOL_FIM} (depois de todas as datas de corte; não podem estar no treino)",
        "b": f"criadas entre {GBIF} e 2024-08-31 (depois do instantâneo do GBIF, antes do acesso ao EOL)",
        "c": f"criadas antes de {GBIF} (podem estar no treino do BioCLIP-2)",
    }
    res = {"faixas_por_data_de_criacao_da_observacao": {k: {"descricao": nomes[k], **tudo(F == k)} for k in "abc"},
           "recorte_pedido_2025": {"criadas_em_2025_ou_depois": tudo(y25), "criadas_antes_de_2025": tudo(~y25)},
           "datas_de_criacao": {"min": min(r[5] for r in rows), "max": max(r[5] for r in rows)}}
    # Comparação dentro da mesma espécie: as fotos antigas só entraram em espécies com poucas fotos recentes
    # (espécies mais difíceis), então a comparação direta mistura data e espécie.
    sp = np.array([p["species"] for p in pred])
    ambas = sorted(s for s in set(sp) if ((sp == s) & (F == "a")).any() and ((sp == s) & (F != "a")).any())
    pa, pc, w = [], [], []
    for s in ambas:
        ma, mc = (sp == s) & (F == "a"), (sp == s) & (F != "a")
        pa.append(t1[ma].mean()); pc.append(t1[mc].mean()); w.append(int(mc.sum()))
    pa, pc, w = np.array(pa), np.array(pc), np.array(w)
    m_amb = np.isin(sp, ambas)
    res["mesma_especie"] = {
        "descricao": "espécies com fotos nos dois grupos; top-1 das fotos criadas depois do corte (a) padronizado para a composição de espécies das fotos criadas antes de 2024-09-01 (b+c)",
        "especies": len(ambas),
        "antes_do_corte_b_c": bloco(m_amb & (F != "a")),
        "depois_do_corte_a": bloco(m_amb & (F == "a")),
        "top1_a_padronizado_pela_composicao_de_b_c": round(float((pa * w).sum() / w.sum()), 4),
        "top1_b_c_mesma_ponderacao": round(float((pc * w).sum() / w.sum()), 4),
    }
    json.dump(res, open(out, "w"), ensure_ascii=False, indent=2)
    print(json.dumps(res["mesma_especie"], ensure_ascii=False))
    for k in "abc":
        g = res["faixas_por_data_de_criacao_da_observacao"][k]
        print(k, g["geral"]["n"], g["geral"]["top1"]["p"], g["geral"]["top1"]["ic95"], g["geral"]["top3"]["p"],
              "| chave", g["especies_chave"]["n"], g["especies_chave"]["top1"]["p"], g["especies_chave"]["top1"]["ic95"])
    for k, g in res["recorte_pedido_2025"].items():
        print(k, g["geral"]["n"], g["geral"]["top1"]["p"], g["geral"]["top1"]["ic95"], "| chave", g["especies_chave"]["n"], g["especies_chave"]["top1"]["p"])


if __name__ == "__main__":
    main()
