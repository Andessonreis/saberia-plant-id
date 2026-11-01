import sys, glob, os, numpy as np, onnxruntime as ort
from PIL import Image
S, tag, onnx_name, splits = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4].split(",")
MEAN = np.array([0.48145466, 0.4578275, 0.40821073], np.float32); STD = np.array([0.26862954, 0.26130258, 0.27577711], np.float32)
def prep(f):
    im = Image.open(f).convert("RGB"); w, h = im.size; s = 224 / min(w, h)
    im = im.resize((max(224, round(w*s)), max(224, round(h*s))), Image.BILINEAR); w, h = im.size
    l, t = (w-224)//2, (h-224)//2; im = im.crop((l, t, l+224, t+224))
    return ((np.asarray(im, np.float32)/255 - MEAN)/STD).transpose(2,0,1)[None]
so = ort.SessionOptions(); so.intra_op_num_threads = 12
sess = ort.InferenceSession(f"{S}/models/{onnx_name}", so, providers=["CPUExecutionProvider"])
base = np.load(sorted(glob.glob(f"{S}/work/emb_{tag}_*.npz"))[0])
out = {"text": base["text"]}
for sp in splits:
    files = sorted(glob.glob(f"{S}/{sp}/*/*.jpg"))
    out[f"{sp}_X"] = np.concatenate([sess.run(None, {"pixel_values": prep(f)})[0] for f in files])
    out[f"{sp}_files"] = np.array(files); print(sp, len(files), flush=True)
np.savez(f"{S}/work/emb_{tag}bl-{onnx_name.split('_')[-1][:-5]}_{'+'.join(splits)}.npz", **out)
