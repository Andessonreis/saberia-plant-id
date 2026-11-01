import json, sys, os, glob, time, numpy as np, torch, open_clip
from PIL import Image
S, model_id = sys.argv[1], sys.argv[2]
tag = model_id.split("/")[-1]
torch.set_num_threads(8)
model, _, pre = open_clip.create_model_and_transforms(f"hf-hub:{model_id}")
tok = open_clip.get_tokenizer(f"hf-hub:{model_id}")
model.eval()
labels = json.load(open(f"{S}/work/labels.json"))
def taxstr(l, name):
    t = l["tax"]
    return " ".join(x for x in [t.get("kingdom"), t.get("phylum"), t.get("class"), t.get("order"), t.get("family")] if x) + " " + name
texts, owner = [], []
for i, l in enumerate(labels):
    for n in [l["name"]] + l["synonyms"]:
        n = n.replace("×", "x")
        for s in (f"a photo of {taxstr(l, n)}.", f"a photo of {n}."):
            texts.append(s); owner.append(i)
with torch.no_grad():
    embs = []
    for b in range(0, len(texts), 256):
        e = model.encode_text(tok(texts[b:b+256])); embs.append(torch.nn.functional.normalize(e, dim=-1))
    E = torch.cat(embs).numpy()
owner = np.array(owner)
T = np.stack([E[owner == i].mean(0) for i in range(len(labels))]); T /= np.linalg.norm(T, axis=1, keepdims=True)
out = {"text": T.astype(np.float32), "logit_scale": float(model.logit_scale.exp())}
for split in (sys.argv[3].split(",") if len(sys.argv) > 3 else ("photos", "photos_recent")):
    files = sorted(glob.glob(f"{S}/{split}/*/*.jpg"))
    X = []
    t0 = time.time()
    with torch.no_grad():
        for b in range(0, len(files), 32):
            ims = torch.stack([pre(Image.open(f).convert("RGB")) for f in files[b:b+32]])
            X.append(torch.nn.functional.normalize(model.encode_image(ims), dim=-1).numpy())
    print(split, len(files), f"{(time.time()-t0)/max(1,len(files))*1000:.0f} ms/img batch", flush=True)
    out[f"{split}_X"] = np.concatenate(X).astype(np.float32)
    out[f"{split}_files"] = np.array(files)
np.savez(f"{S}/work/emb_{tag}_" + "+".join(k[:-2] for k in out if k.endswith("_X")) + ".npz", **out)
