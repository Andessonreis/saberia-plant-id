"""Compara com IA na nuvem na MESMA subamostra usada para o classificador local.

Uso:
  python nuvem.py amostra <dir_dados> [n_base=400] [n_fora=50]
      sorteia (semente fixa SEED) a subamostra a partir de test/meta.jsonl e ood/meta.jsonl
      (fotos removidas depois como quase-duplicatas saem da comparação para todos os sistemas)
  python nuvem.py rodar <dir_dados> <keys.properties> <provedor> [workers=4]
      provedor: gemini (mesmo endpoint, modelo, prompt e parâmetros do app), gemini25 ou openai
      NUVEM_INTERVALO=<s> espaça as chamadas (cota gratuita do Gemini: 5 requisições/minuto).
      A chave é lida do arquivo e só vai no cabeçalho Authorization; nunca é impressa nem gravada.
  python nuvem.py pontuar <dir_dados> <species.json> <provedor>

Normalização dos nomes: nome aceito e sinônimos da base + o nome usado pelo iNaturalist para a
observação (primeiras duas palavras, minúsculas, "×" = "x"). Acerto de gênero: primeira palavra
igual ao gênero do nome aceito ou de algum sinônimo.
"""
import base64, json, os, random, re, sys, time, concurrent.futures as cf
import requests

SEED = 20251105
PROMPT_SYS = "Você deve fornecer respostas curtas e concisas"
PROMPT = ("GPT, sua tarefa é identificar plantas com precisão. Analise qualquer imagem de uma planta ou folha que eu fornecer e detecte. "
          "Responda estritamente com o nome cientifico da planta identificada, e nada mais, sem explicações, sem texto adicional. "
          "Se a condição for irreconhecível, responda com 'Não sei'. Se a imagem não estiver relacionada a plantas, diga 'Por favor, escolha outra imagem'.")
PROV = {
    # igual a RemotePlantAiEngine.kt (IDENTIFY): gemini-3.5-flash, max_tokens 1024, reasoning_effort low
    "gemini": {"url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions", "key": "API_KEY",
               "body": {"model": "gemini-3.5-flash", "max_tokens": 1024, "reasoning_effort": "low"}},
    # mesmo endpoint/prompt/parâmetros, outro modelo (usado quando a cota diária gratuita do 3.5 acaba: 20 req/dia)
    "gemini25": {"url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions", "key": "API_KEY",
                 "body": {"model": "gemini-2.5-flash", "max_tokens": 1024, "reasoning_effort": "low"}},
    "openai": {"url": "https://api.openai.com/v1/chat/completions", "key": "OPENAI_API_KEY",
               "body": {"model": os.environ.get("OPENAI_MODEL", "gpt-4o"), "max_tokens": 300}},
}


def amostra(data, n_base=400, n_fora=50):
    files = lambda split: sorted(json.loads(l)["file"] for l in open(os.path.join(data, split, "meta.jsonl")))
    rng = random.Random(SEED)
    base = rng.sample(files("test"), int(n_base))
    fora = rng.sample(files("ood"), int(n_fora))
    json.dump({"seed": SEED, "base": base, "fora": fora}, open(os.path.join(data, "amostra_nuvem.json"), "w"), indent=0)
    print(len(base), len(fora))


def read_key(path, name):
    for line in open(path):
        line = line.strip().lstrip("#").strip()
        if line.startswith(name + "="):
            return line.split("=", 1)[1].strip().strip('"')
    raise SystemExit(f"chave {name} não encontrada")


def rodar(data, keys, prov, workers=4):
    cfg = PROV[prov]
    key = read_key(keys, cfg["key"])
    am = json.load(open(os.path.join(data, "amostra_nuvem.json")))
    jobs = [("test", f) for f in am["base"]] + [("ood", f) for f in am["fora"]]
    out_path = os.path.join(data, f"nuvem_{prov}.jsonl")
    done = set()
    if os.path.exists(out_path):
        for l in open(out_path):
            r = json.loads(l)
            if r["status"] == "ok": done.add((r["split"], r["file"]))
    jobs = [j for j in jobs if j not in done]

    def call(job):
        split, f = job
        img = base64.b64encode(open(os.path.join(data, split, f), "rb").read()).decode()
        body = dict(cfg["body"], messages=[
            {"role": "system", "content": [{"type": "text", "text": PROMPT_SYS}]},
            {"role": "user", "content": [{"type": "text", "text": PROMPT},
                                         {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + img}}]}])
        tries, err = 0, None
        for attempt in range(7):
            tries += 1
            t0 = time.time()
            try:
                r = requests.post(cfg["url"], json=body, headers={"Authorization": "Bearer " + key}, timeout=120)
            except Exception as e:
                err = type(e).__name__; time.sleep(5 * 2 ** attempt); continue
            dt = time.time() - t0
            if r.status_code == 200:
                try:
                    js = r.json(); txt = js["choices"][0]["message"]["content"]; served = js.get("model")
                except Exception:
                    txt = served = None
                time.sleep(float(os.environ.get("NUVEM_INTERVALO", "0")))  # respeita o limite por minuto da cota
                return {"split": split, "file": f, "status": "ok", "answer": txt, "latency_s": round(dt, 2), "tries": tries,
                        "modelo_servido": served}
            err = r.status_code
            try: msg = (r.json()[0] if isinstance(r.json(), list) else r.json()).get("error", {}).get("message", "")[:160]
            except Exception: msg = r.text[:160]
            print(f"{split}/{f}: HTTP {r.status_code} {msg.replace(key, '<chave>')}", file=sys.stderr, flush=True)
            if r.status_code in (429, 500, 502, 503, 504):
                time.sleep(min(120, 5 * 2 ** attempt)); continue
            break
        return {"split": split, "file": f, "status": f"erro {err}", "answer": None, "tries": tries}

    with open(out_path, "a") as fo, cf.ThreadPoolExecutor(int(workers)) as ex:
        for i, r in enumerate(ex.map(call, jobs)):
            fo.write(json.dumps(r, ensure_ascii=False) + "\n"); fo.flush()
            if i % 25 == 0: print(prov, i, len(jobs), r["status"], flush=True)


def norm(s):
    s = s.replace("×", "x").replace("*", "").replace("_", " ").strip().lower()
    return " ".join(re.sub(r"[^a-zà-ü\- ]", " ", s).split()[:2])


def pontuar(data, species_json, prov):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from avaliar import prop
    db = json.load(open(species_json))["species"]
    name2id, gen = {}, {}
    for s in db:
        for n in [s["scientific_name"]] + s["synonyms"]: name2id.setdefault(norm(n), s["id"])
        gen[s["id"]] = {n.split()[0].lower() for n in [s["scientific_name"]] + s["synonyms"]}
    meta = {json.loads(l)["file"]: json.loads(l) for l in open(os.path.join(data, "test", "meta.jsonl"))}
    for m in meta.values():
        name2id.setdefault(norm(m["taxon"]), m["species"]); gen[m["species"]].add(m["taxon"].split()[0].lower())
    app = {x["file"]: x for x in json.load(open(os.path.join(data, "metricas_app_predicoes.json")))["test"]}
    app_o = {x["file"]: x for x in json.load(open(os.path.join(data, "metricas_app_predicoes.json")))["ood"]}
    rows = [json.loads(l) for l in open(os.path.join(data, f"nuvem_{prov}.jsonl"))]
    last = {}
    for r in rows: last[(r["split"], r["file"])] = r if r["status"] == "ok" or (r["split"], r["file"]) not in last else last[(r["split"], r["file"])]
    am = json.load(open(os.path.join(data, "amostra_nuvem.json")))
    am["base"] = [f for f in am["base"] if f in app]; am["fora"] = [f for f in am["fora"] if f in app_o]
    def app_block(files):
        n = len(files); A = [app[f] for f in files]
        return {"n": n, "top1": prop(sum(a["top3"][0] == a["species"] for a in A), n),
                "top3": prop(sum(a["species"] in a["top3"] for a in A), n),
                "aceitas": prop(sum(a["aceita"] for a in A), n),
                "acerto_entre_aceitas": prop(sum(a["aceita"] and a["top3"][0] == a["species"] for a in A), sum(a["aceita"] for a in A))}
    # só entram na comparação as fotos que este sistema respondeu; como a ordem das chamadas é a ordem
    # aleatória do sorteio e a interrupção foi por cota (não pelo conteúdo), o subconjunto também é aleatório
    answered = [f for f in am["base"] if last.get(("test", f), {}).get("status") == "ok"]
    attempted_fail = [f for f in am["base"] if ("test", f) in last and last[("test", f)]["status"] != "ok"]
    k_sp = k_gen = abst = 0
    lat = []
    for f in answered:
        r = last[("test", f)]; t = app[f]["species"]
        lat.append(r["latency_s"])
        ans = (r["answer"] or "").strip().split("\n")[0]
        if not ans or "não sei" in ans.lower() or "escolha outra" in ans.lower(): abst += 1; continue
        nn = norm(ans)
        k_sp += name2id.get(nn) == t
        k_gen += bool(nn.split()[:1]) and nn.split()[0] in gen[t]
    n = len(answered)
    fo = [last.get(("ood", f)) for f in am["fora"]]
    ood_ok = [r for r in fo if r and r["status"] == "ok"]
    ood_said_base = sum(1 for r in ood_ok if name2id.get(norm((r["answer"] or "").split("\n")[0])) is not None)
    lat.sort()
    res = {
        "provedor": prov, "modelo": PROV[prov]["body"]["model"],
        "modelo_servido": sorted({r.get("modelo_servido") for r in last.values() if r.get("modelo_servido")}),
        "seed": am["seed"], "n_amostra_base_sorteada": len(am["base"]), "n_amostra_fora_sorteada": len(am["fora"]),
        "n_respondidas_base": n, "tentativas_sem_resposta_429_ou_erro": len(attempted_fail),
        "nao_tentadas_por_falta_de_cota": len(am["base"]) - n - len(attempted_fail),
        "nao_sei_ou_recusa": abst,
        "especie_correta": prop(k_sp, n), "genero_correto": prop(k_gen, n),
        "latencia_s_mediana": lat[len(lat) // 2] if lat else None,
        "fora_da_base": {"respondidas": len(ood_ok), "disse_especie_da_base": prop(ood_said_base, len(ood_ok))},
        "app_mesmas_fotos": app_block(answered),
        "app_amostra_completa": dict(app_block(am["base"]),
                                     fora_da_base_aceitas_FP=prop(sum(app_o[f]["aceita"] for f in am["fora"]), len(am["fora"]))),
        "respostas": [{"file": f, "especie": app[f]["species"], "resposta": last[("test", f)]["answer"],
                       "app_top1": app[f]["top3"][0]} for f in answered],
    }
    json.dump(res, open(os.path.join(data, f"nuvem_{prov}_resultado.json"), "w"), ensure_ascii=False, indent=1)
    print(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "amostra": amostra(*sys.argv[2:])
    elif c == "rodar": rodar(*sys.argv[2:])
    elif c == "pontuar": pontuar(*sys.argv[2:])
