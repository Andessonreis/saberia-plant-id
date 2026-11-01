"""Junta as métricas em resultados.json e gera as tabelas em Markdown (tabelas.md).

Uso: python relatorio.py <metricas_app.json> <dir_dados> <saida_dir> <species.json> [log_do_aparelho]
"""
import json, os, re, statistics, sys


def pct(x):
    return "–" if x is None else f"{100 * x:.1f}".replace(".", ",") + "%"


def ci(d):
    lo, hi = d["ic95"]
    return f"{pct(d['p'])} ({pct(lo)}–{pct(hi)})" if d["n"] else "–"


def frac(d):
    return f"{d['k']}/{d['n']}"


def latency(log):
    t = open(log).read()
    m = sorted(int(x) for x in re.findall(r"modelo=(\d+)ms", t))
    r = sorted(int(x) for x in re.findall(r"leitura=(\d+)ms", t))
    c = sorted(int(x) for x in re.findall(r"carregado em (\d+) ms", t))
    th = sorted(set(re.findall(r"threads=(\d+)", t)))
    return {"fonte": "registro do próprio app no aparelho (files/plant-id.log), identificações reais feitas no Redmi 12 (MediaTek Helio G88, 8 GB)",
            "identificacoes": len(m), "threads": th,
            "inferencia_ms": {"mediana": statistics.median(m), "min": m[0], "max": m[-1]} if m else None,
            "leitura_foto_ms": {"mediana": statistics.median(r), "min": r[0], "max": r[-1]} if r else None,
            "carga_do_modelo_ms": {"n": len(c), "mediana": statistics.median(c), "min": c[0], "max": c[-1]} if c else None}


def main():
    met_path, data, out, species_json = sys.argv[1:5]
    log = sys.argv[5] if len(sys.argv) > 5 else None
    met = json.load(open(met_path))
    nuvem = {}
    for p in ("gemini", "gemini25", "openai"):
        f = os.path.join(data, f"nuvem_{p}_resultado.json")
        if os.path.exists(f): nuvem[p] = json.load(open(f))
    tb = met["teste_na_base"]
    L = []
    L.append("### Geral (limiar do app = %s)\n" % str(met["limiar_app"]).replace(".", ","))
    L.append("| Recorte | n fotos | Top-1 (IC 95%) | Top-3 (IC 95%) | Gênero certo no top-1 | Aceitas no limiar | Acerto entre aceitas | Erro entre aceitas |")
    L.append("|---|---|---|---|---|---|---|---|")
    for nome, b in (("Todas as espécies", tb["geral_micro"]), ("Espécies-chave", tb["especies_chave"]), ("Demais espécies", tb["demais_especies"])):
        lim = b["no_limiar"]
        L.append(f"| {nome} | {b['n']} | {ci(b['top1'])} | {ci(b['top3'])} | {ci(b['top1_genero'])} | {ci(lim['aceitas'])} | {ci(lim['acerto_entre_aceitas'])} | {ci(lim['erro_entre_aceitas'])} |")
    m1, m3 = tb["geral_macro_top1"], tb["geral_macro_top3"]
    L.append(f"\nMédia por espécie (cada espécie pesa igual, {m1['especies']} espécies): top-1 {pct(m1['media'])} (IC 95% bootstrap {pct(m1['ic95'][0])}–{pct(m1['ic95'][1])}); "
             f"top-3 {pct(m3['media'])} ({pct(m3['ic95'][0])}–{pct(m3['ic95'][1])}). Espécies-chave: top-1 {pct(tb['especies_chave_macro_top1']['media'])} "
             f"({pct(tb['especies_chave_macro_top1']['ic95'][0])}–{pct(tb['especies_chave_macro_top1']['ic95'][1])}).\n")
    fb = met["fora_da_base"]
    L.append("### Plantas fora da base\n")
    L.append("| Recorte | Aceitas como espécie da base (falso positivo) |")
    L.append("|---|---|")
    L.append(f"| Todas ({fb['fotos']} fotos, {fb['especies']} espécies) | {frac(fb['falso_positivo_no_limiar'])} = {ci(fb['falso_positivo_no_limiar'])} |")
    L.append(f"| Espécie aparece na lista de nomes \"de fora\" do índice | {frac(fb['falso_positivo_especie_esta_na_lista_de_distratores'])} = {ci(fb['falso_positivo_especie_esta_na_lista_de_distratores'])} |")
    L.append(f"| Gênero tem espécie na base (ex.: outra *Erythrina*, outro *Melocactus*) | {frac(fb['falso_positivo_mesmo_genero_de_especie_da_base'])} = {ci(fb['falso_positivo_mesmo_genero_de_especie_da_base'])} |")
    L.append(f"| Gênero sem nenhuma espécie na base | {frac(fb['falso_positivo_genero_ausente_da_base'])} = {ci(fb['falso_positivo_genero_ausente_da_base'])} |")
    L.append(f"| Espécie não aparece nessa lista | {frac(fb['falso_positivo_especie_fora_da_lista_de_distratores'])} = {ci(fb['falso_positivo_especie_fora_da_lista_de_distratores'])} |\n")
    s = tb["sensibilidade_observador_tambem_nas_referencias"]
    L.append("### Sensibilidade: mesmo observador nas fotos de referência\n")
    L.append("| Recorte | n | Top-1 (IC 95%) |")
    L.append("|---|---|---|")
    L.append(f"| Observador também tem foto nas referências do índice | {s['observador_nas_referencias']['n']} | {ci(s['observador_nas_referencias']['top1'])} |")
    L.append(f"| Observador novo | {s['observador_novo']['n']} | {ci(s['observador_novo']['top1'])} |\n")
    if nuvem:
        L.append("### Comparação com IA na nuvem (mesmo prompt e endpoint do app)\n")
        any_r = next(iter(nuvem.values()))
        full = any_r["app_amostra_completa"]
        L.append(f"Subamostra sorteada com semente {any_r['seed']}: {any_r['n_amostra_base_sorteada']} fotos de espécies da base "
                 f"+ {any_r['n_amostra_fora_sorteada']} de fora da base. A cota gratuita da chave do app (20 requisições por dia "
                 f"por modelo) interrompeu as chamadas; entram só as fotos que cada modelo respondeu, comparadas com o "
                 f"classificador offline NAS MESMAS fotos.\n")
        L.append("| Sistema | Fotos respondidas | Espécie certa (IC 95%) | Gênero certo (IC 95%) | SaberIA offline nas mesmas fotos: top-1 (IC 95%) | Latência mediana da nuvem |")
        L.append("|---|---|---|---|---|---|")
        for p, r in nuvem.items():
            lat = r["latencia_s_mediana"]
            L.append(f"| {r['modelo']} | {r['n_respondidas_base']} | {frac(r['especie_correta'])} = {ci(r['especie_correta'])} | "
                     f"{frac(r['genero_correto'])} = {ci(r['genero_correto'])} | {frac(r['app_mesmas_fotos']['top1'])} = {ci(r['app_mesmas_fotos']['top1'])} | "
                     f"{('%.1f' % lat).replace('.', ',') + ' s' if lat else '–'} |")
        L.append(f"\nSaberIA offline na subamostra inteira ({full['n']} fotos): top-1 {ci(full['top1'])}, top-3 {ci(full['top3'])}; "
                 f"aceitas no limiar {ci(full['aceitas'])}, acerto entre aceitas {ci(full['acerto_entre_aceitas'])}; "
                 f"fora da base aceitas {frac(full['fora_da_base_aceitas_FP'])} = {ci(full['fora_da_base_aceitas_FP'])}.\n")
    L.append("### Por espécie\n")
    L.append("| Espécie | Chave | n | Top-1 (IC 95%) | Top-3 (IC 95%) | Aceitas | Acerto entre aceitas | Confusão mais comum |")
    L.append("|---|---|---|---|---|---|---|---|")
    per = sorted(tb["por_especie"].values(), key=lambda b: (not b["chave"], b["nome"]))
    for b in per:
        cf = b["confusoes_mais_comuns"][0] if b["confusoes_mais_comuns"] else None
        L.append(f"| *{b['nome']}* | {'sim' if b['chave'] else ''} | {b['n']} | {frac(b['top1'])} = {ci(b['top1'])} | {ci(b['top3'])} | "
                 f"{frac(b['no_limiar']['aceitas'])} | {frac(b['no_limiar']['acerto_entre_aceitas']) if b['no_limiar']['aceitas']['k'] else '–'} | "
                 f"{('*' + cf['especie'] + '* (' + str(cf['n']) + ')') if cf else ''} |")
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, "tabelas.md"), "w").write("\n".join(L) + "\n")
    meta_test = [json.loads(l) for l in open(os.path.join(data, "test", "meta.jsonl"))]
    meta_ood = [json.loads(l) for l in open(os.path.join(data, "ood", "meta.jsonl"))]
    res = {
        "versao": 1,
        "sistema_avaliado": {
            "modelo": "plant-classifier-int8.onnx (BioCLIP-2, codificador de imagem, int8)", "modelo_bytes": 308210728,
            "indice": "plant-index.bin (159 espécies, 2.320 fotos de referência, 1.212 rótulos de texto)", "indice_bytes": 5473795,
            "sha256_modelo": "6452d3304f38b1cb6e86d62172911c3082600e376dd57dd1659743171ca0dbdf",
            "sha256_indice": "b1c553fe4dc8a1426d6e46a028998bdc08ba5aab711c7ba2da81a9832ff21343",
            "limiar_de_confianca": met["limiar_app"]},
        "metodologia": {
            "fonte_das_fotos": "iNaturalist, API pública v1, observações 'research grade' com foto; tamanho 'medium' (lado maior 500 px)",
            "amostragem_teste": "por espécie da base: 1 foto por observação (a primeira), no máximo 1 observação por observador; "
                                 "preferência por observações de 2025-01-01 em diante e por licenças CC0/CC-BY/CC-BY-SA; alvo 100 fotos "
                                 "para 22 espécies-chave e 30 para as demais; quando não havia, ficou o n real",
            "amostragem_fora_da_base": "300 observações de plantas do Brasil (2025+), identificadas até espécie, sorteadas com semente 20251105 "
                                       "(IDs aleatórios), 1 por espécie e 1 por observador, excluídas as espécies da base e sinônimos",
            "prevencao_de_vazamento": ["exclusão por ID de observação de todas as 2.320 fotos de referência do índice e das fotos usadas antes "
                                       "para calibrar o limiar (2.647 observações)",
                                       "remoção de duplicatas reais (dHash 64 bits, Hamming <= 6, ou cosseno >= 0,99) contra as fotos de "
                                       "referência e entre as fotos de teste",
                                       "análise de sensibilidade separando fotos de observadores que também têm foto nas referências"],
            "preprocessamento": "idêntico ao app: orientação EXIF (rotações), inSampleSize em potência de 2, redimensionamento bilinear "
                                "sem suavização (como Bitmap.createScaledBitmap), recorte central 224x224, normalização CLIP",
            "pontuacao": "idêntica a PlantClassifier.score: texto + média das 3 referências mais parecidas; confiança = prob. da melhor "
                         "espécie x prob. de estar na base; aceita se confiança >= limiar",
            "intervalo_de_confianca": "IC 95% de Wilson para proporções; para a média por espécie, bootstrap estratificado (2.000 reamostragens, semente 20251105)",
            "seed": 20251105,
            "data_da_coleta": "2026-10-31",
        },
        "amostra": {"teste_fotos_baixadas": len(meta_test), "teste_fotos_avaliadas": met["teste_na_base"]["fotos"],
                    "teste_especies": met["teste_na_base"]["especies"], "fora_da_base_fotos": met["fora_da_base"]["fotos"],
                    "fora_da_base_especies": met["fora_da_base"]["especies"],
                    "especies_da_base_sem_nenhuma_foto_elegivel": sorted({x["id"] for x in json.load(open(species_json))["species"]}
                                                                         - {m["species"] for m in meta_test})},
        "resultados_classificador": met,
        "comparacoes": {
            "nuvem_mesma_subamostra": nuvem,
            "qwen3_vl_2b_local_medicao_anterior": {
                "acerto_especie": {"k": 6, "n": 64, "p": 0.0938, "ic95": [0.0437, 0.1898]},
                "observacao": "medido antes, com o mesmo prompt do app, em OUTRA amostra (64 fotos recentes do iNaturalist de 8 espécies-chave); não é a mesma amostra deste teste"}},
    }
    if log: res["latencia_aparelho"] = latency(log)
    json.dump(res, open(os.path.join(out, "resultados.json"), "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
