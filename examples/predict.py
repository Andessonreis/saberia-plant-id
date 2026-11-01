"""Identify a Caatinga plant from a photo with the SaberIA model, fully offline.

Usage:
    python predict.py photo.jpg [more.jpg ...] \
        --model plant-classifier-int8.onnx --index plant-index.bin \
        --species caatinga_species.json

Reproduces the scoring used by the Android app (PlantClassifier.kt):
text similarity + mean similarity to the k closest reference photos of each species,
plus a confidence gate that refuses to answer below the index threshold.
"""
import argparse
import json
import struct

import numpy as np
import onnxruntime as ort
from PIL import Image


def load_index(path):
    with open(path, "rb") as f:
        size = struct.unpack("<i", f.read(4))[0]
        header = json.loads(f.read(size))
        vectors = np.frombuffer(f.read(), dtype="<f2").astype(np.float32)
    vectors = vectors.reshape(-1, header["dim"])
    n_labels = len(header["labels"])
    return header, vectors[:n_labels], vectors[n_labels:]


def preprocess(path, h):
    # Shorter side to 224 (bilinear, as Android's createScaledBitmap), then center crop.
    size = h["size"]
    im = Image.open(path).convert("RGB")
    w, ht = im.size
    s = size / min(w, ht)
    im = im.resize((max(size, round(w * s)), max(size, round(ht * s))), Image.BILINEAR)
    w, ht = im.size
    left, top = (w - size) // 2, (ht - size) // 2
    im = im.crop((left, top, left + size, top + size))
    x = (np.asarray(im, np.float32) / 255 - h["mean"]) / h["std"]
    return x.transpose(2, 0, 1)[None].astype(np.float32)


def softmax(z, scale):
    z = (z - z.max()) * scale
    e = np.exp(z)
    return e / e.sum()


def score(x, h, text, refs):
    catalog = [i for i, label in enumerate(h["labels"]) if "id" in label]
    owner = np.array(h["refs"])
    t = text @ x
    in_catalog = softmax(t, h["scale"])[catalog].sum()  # P(photo is a species of the base)
    sims = refs @ x
    visual = np.array([np.sort(sims[owner == i])[::-1][: h["k"]].mean() for i in catalog])
    combined = t[catalog] + h["weight"] * visual
    prob = softmax(combined, h["scale"] / (1 + h["weight"]))
    order = np.argsort(-prob)[:3]
    top3 = [(h["labels"][catalog[i]]["id"], float(prob[i])) for i in order]
    confidence = top3[0][1] * in_catalog
    return top3, float(confidence), bool(confidence >= h["threshold"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("photos", nargs="+")
    ap.add_argument("--model", default="plant-classifier-int8.onnx")
    ap.add_argument("--index", default="plant-index.bin")
    ap.add_argument("--species", default="caatinga_species.json")
    a = ap.parse_args()

    header, text, refs = load_index(a.index)
    species = {s["id"]: s for s in json.load(open(a.species, encoding="utf-8"))["species"]}
    session = ort.InferenceSession(a.model, providers=["CPUExecutionProvider"])

    for photo in a.photos:
        emb = session.run(None, {"pixel_values": preprocess(photo, header)})[0][0]
        top3, confidence, answered = score(emb, header, text, refs)
        best = species[top3[0][0]]
        print(f"{photo}: confidence {confidence:.2f}")
        if answered:
            print(f"  -> {best['scientific_name']} ({', '.join(best['popular_names'][:2])})")
            print(f"     source: {best['sources'][0]['url']}")
        else:
            print("  -> not sure; candidates:")
            for sid, p in top3:
                print(f"     {species[sid]['scientific_name']}  {p:.2f}")


if __name__ == "__main__":
    main()
