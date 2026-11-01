"""Gera um índice candidato (NÃO publicado) com mais fotos de referência para espécies fracas.

Uso: python melhorar_refs.py <plant-index.bin> <refs_files.txt> <refs2_dir> <refs2_attr.json> <modelo.onnx>
                             <dir_dados> <saida_indice.bin> <especie1,especie2,...> [remover_obs=id1,id2,...]

- <refs_files.txt>: caminho de cada foto de referência do índice atual, na mesma ordem dos vetores do índice
  (o nome do arquivo é o ID da observação)
- <refs2_dir>/<especie>/<obs>_<foto>.jpg (licença com ou sem versão, ex.: cc-by-sa-4.0) e <refs2_attr.json>: fotos candidatas (até 3 por observação) com licença
- remover_obs: observações cujas fotos saem do índice (ex.: fotos "todos os direitos reservados")

Regras para a foto candidata entrar: licença CC0/CC-BY/CC-BY-SA; observação fora do conjunto de teste
(<dir_dados>/test/meta.jsonl e ood/meta.jsonl); não ser cópia de nenhuma foto de teste (dHash <= 6 bits ou cosseno >= 0,99);
não repetir uma referência que já está no índice (cosseno >= 0,98, ex.: a mesma foto em outro tamanho).
Os vetores novos usam o mesmo pré-processamento do app (avaliar.preprocess).
"""
import json, os, re, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from avaliar import read_index, preprocess, dhash

FREE = {"cc0", "cc-by", "cc-by-sa"}


def main():
    idx_path, refs_files, refs2_dir, attr_path, model, data, out, species = sys.argv[1:9]
    remove = {int(x) for x in sys.argv[9].split(",")} if len(sys.argv) > 9 and sys.argv[9] else set()
    species = species.split(",")
    raw = open(idx_path, "rb").read()
    n = int.from_bytes(raw[:4], "little")
    h = json.loads(raw[4:4 + n].decode())
    _, text, refs, _, _ = read_index(idx_path)
    files = [l.strip() for l in open(refs_files) if l.strip()]
    assert len(files) == len(refs)
    label_of = {l["id"]: i for i, l in enumerate(h["labels"]) if l.get("id")}

    keep = [i for i, f in enumerate(files) if int(os.path.basename(f).split("_")[0].split(".")[0]) not in remove]
    removed = [files[i] for i in range(len(files)) if i not in set(keep)]
    test_obs, test_hashes = set(), []
    for split in ("test", "ood", "campo"):
        if not os.path.exists(os.path.join(data, split, "meta.jsonl")): continue
        for l in open(os.path.join(data, split, "meta.jsonl")):
            m = json.loads(l); test_obs.add(m["obs"])
            if m.get("species") in species: test_hashes.append(dhash(os.path.join(data, split, m["file"])))
    attr = json.load(open(attr_path))
    import onnxruntime as ort
    so = ort.SessionOptions(); so.intra_op_num_threads = os.cpu_count()
    sess = ort.InferenceSession(model, so, providers=["CPUExecutionProvider"])
    new_vecs, new_labels, added, skipped = [], [], [], {"licenca": 0, "observacao_no_teste": 0, "copia_de_foto_de_teste": 0, "repetida_de_referencia": 0}
    z = np.load(os.path.join(data, "emb_test.npz")); Xt = z["X"].astype(np.float32)
    R0 = refs[keep]
    for sp in species:
        for key, a in sorted(attr.items()):
            if a["id"] != sp: continue
            f = os.path.join(refs2_dir, sp, key + ".jpg")
            if not os.path.exists(f): continue
            if re.sub(r"-[\d.]+$", "", a["license"] or "") not in FREE: skipped["licenca"] += 1; continue
            if a["obs"] in test_obs: skipped["observacao_no_teste"] += 1; continue
            hh = dhash(f)
            if any(bin(hh ^ t).count("1") <= 6 for t in test_hashes): skipped["copia_de_foto_de_teste"] += 1; continue
            v = sess.run(None, {"pixel_values": preprocess(f)})[0][0]
            if float((Xt @ v).max()) >= 0.99: skipped["copia_de_foto_de_teste"] += 1; continue
            prev = np.concatenate([R0] + [np.array(new_vecs, np.float32).reshape(-1, refs.shape[1])])
            if float((prev @ v).max()) >= 0.98: skipped["repetida_de_referencia"] += 1; continue
            new_vecs.append(v); new_labels.append(label_of[sp])
            added.append({"especie": sp, "obs": a["obs"], "foto": a["photo"], "licenca": a["license"], "credito": a["attribution"]})
    R = np.concatenate([refs[keep], np.array(new_vecs, np.float32).reshape(-1, refs.shape[1])])
    h["refs"] = [h["refs"][i] for i in keep] + new_labels
    hb = json.dumps(h, ensure_ascii=False, separators=(",", ":")).encode()
    with open(out, "wb") as fo:
        fo.write(len(hb).to_bytes(4, "little")); fo.write(hb)
        fo.write(text.astype("<f2").tobytes()); fo.write(R.astype("<f2").tobytes())
    rep = {"removidas": removed, "adicionadas": added, "descartadas": skipped, "refs_total": len(h["refs"])}
    json.dump(rep, open(out + ".json", "w"), ensure_ascii=False, indent=1)
    print(json.dumps({k: (len(v) if isinstance(v, list) else v) for k, v in rep.items()}, ensure_ascii=False))


if __name__ == "__main__":
    main()
