import json, sys, os, glob, numpy as np, collections
S, tag = sys.argv[1], sys.argv[2]
W = float(sys.argv[3]) if len(sys.argv) > 3 else 1.5
d = {}
for f in glob.glob(f"{S}/work/emb_{tag}_*.npz"):
    z = np.load(f); d.update({k: z[k] for k in z.files})
labels = json.load(open(f"{S}/work/labels.json"))
db = json.load(open(f"{S}/db/caatinga_species.json"))["species"]; ndb = len(db)
id2idx = {s["id"]: i for i, s in enumerate(db)}
name2idx = {}
for i, l in enumerate(labels):
    for n in [l["name"]] + l["synonyms"]: name2idx.setdefault(n.replace("×","x"), i)
T, R = d["text"], d["refs_X"]
Rc = np.array([id2idx[os.path.basename(os.path.dirname(f))] for f in d["refs_files"]])
SCALE = 100.0
def sm(z): z = z - z.max(1, keepdims=True); e = np.exp(z); return e / e.sum(1, keepdims=True)
def classify(X, k=3):
    t = X @ T.T
    pt = sm(SCALE * t); p_db = pt[:, :ndb].sum(1)
    sims = X @ R.T
    p = np.full((len(X), ndb), -1.0)
    for c in range(ndb):
        m = Rc == c; p[:, c] = np.sort(sims[:, m], 1)[:, ::-1][:, :k].mean(1)
    s = t[:, :ndb] + W * p
    pc = sm(SCALE / (1 + W) * s)
    return pc, p_db, p.max(1)
truth = lambda f: name2idx.get(os.path.basename(os.path.dirname(f)).replace("_", " "), -1)
Xi, Fi = d["photos_recent_X"], d["photos_recent_files"]; yi = np.array([truth(f) for f in Fi])
ood = yi >= ndb
Xo = np.concatenate([d["photos_ood_X"], Xi[ood]]); Xi, Fi, yi = Xi[~ood], Fi[~ood], yi[~ood]
pci, pdbi, kni = classify(Xi); pco, pdbo, kno = classify(Xo)
oi = np.argsort(-pci, 1); top1 = oi[:, 0] == yi
print(f"[{tag} W={W}] no gate: top1 {top1.mean():.3f} top3 {np.mean([y in r[:3] for y, r in zip(yi, oi)]):.3f}  (n={len(yi)}, OOD n={len(Xo)})")
conf_i = pci.max(1) * pdbi; conf_o = pco.max(1) * pdbo
print(" thr  | in-DB answered | acc among answered | wrong answers (in-DB) | OOD falsely answered")
for thr in (0.0, 0.5, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85):
    a = conf_i >= thr; ao = conf_o >= thr
    print(f" {thr:.2f} | {a.mean():.2f} | {top1[a].mean() if a.any() else 0:.3f} | {(a & ~top1).sum()}/{len(yi)} | {ao.sum()}/{len(Xo)}")
np.save(f"{S}/work/conf_{tag}.npy", np.stack([conf_i, top1]))
if len(sys.argv) > 4:
    thr = float(sys.argv[4])
    per = collections.defaultdict(lambda: [0, 0, 0, 0])
    for y, r, c in zip(yi, oi, conf_i):
        k = labels[y]["name"]; per[k][0] += 1; per[k][1] += r[0] == y; per[k][2] += y in r[:3]; per[k][3] += (c >= thr) and r[0] == y
    print(f"species | n | top1 | top3 | correct&answered@{thr}")
    for k, v in sorted(per.items()): print(f"{k} | {v[0]} | {v[1]} | {v[2]} | {v[3]}")
low = conf_i < 0.75
top3c = np.array([y in r[:3] for y, r in zip(yi, oi)])
print(f"below 0.75: {low.sum()}/{len(yi)} ; top1 ok among them {top1[low].sum()} ; top3 ok among them {top3c[low].sum()}")
print(f"above 0.75: {(~low).sum()} ; top1 ok {top1[~low].sum()}")
