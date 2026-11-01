import json, sys, os, glob, struct, hashlib, numpy as np
S, tag, onnx_name, out_dir = sys.argv[1:5]
W, THR = float(sys.argv[5]), float(sys.argv[6])
d = {}
for f in glob.glob(f"{S}/work/emb_{tag}_*.npz") + glob.glob(f"{S}/work/emb_{tag.split('-int8')[0]}_photos.npz"):
    z = np.load(f); d.update({k: z[k] for k in z.files})
labels = json.load(open(f"{S}/work/labels.json"))
db = json.load(open(f"{S}/db/caatinga_species.json"))["species"]
id2idx = {s["id"]: i for i, s in enumerate(db)}
assert [l["id"] for l in labels[:len(db)]] == [s["id"] for s in db]
refs_owner = [id2idx[os.path.basename(os.path.dirname(f))] for f in d["refs_files"]]
header = {"version": 1, "dim": int(d["text"].shape[1]), "size": 224,
          "mean": [0.48145466, 0.4578275, 0.40821073], "std": [0.26862954, 0.26130258, 0.27577711],
          "scale": 100.0, "weight": W, "k": 3, "threshold": THR,
          "labels": [{"id": l["id"], "name": l["name"]} if l["in_db"] else {"name": l["name"]} for l in labels],
          "refs": refs_owner}
hb = json.dumps(header, ensure_ascii=False, separators=(",", ":")).encode()
idx_path = f"{out_dir}/plant-index.bin"
with open(idx_path, "wb") as f:
    f.write(struct.pack("<i", len(hb))); f.write(hb)
    f.write(d["text"].astype("<f2").tobytes()); f.write(d["refs_X"].astype("<f2").tobytes())
model_path = f"{out_dir}/plant-classifier-int8.onnx"
if not os.path.exists(model_path): os.link(f"{S}/models/{onnx_name}", model_path) if False else __import__("shutil").copy(f"{S}/models/{onnx_name}", model_path)
def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()
manifest = {"files": [{"id": "classifier", "name": os.path.basename(model_path), "url": "", "size": os.path.getsize(model_path), "sha256": sha(model_path)},
                      {"id": "classifier-index", "name": os.path.basename(idx_path), "url": "", "size": os.path.getsize(idx_path), "sha256": sha(idx_path)}]}
json.dump(manifest, open(f"{out_dir}/manifest.json", "w"), indent=2)
print(json.dumps(manifest, indent=2))
