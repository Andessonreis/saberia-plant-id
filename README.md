<div align="center">

# SaberIA Plant ID

**Offline identification of medicinal plants of the Brazilian Caatinga, on a mid-range Android phone.**

**English** · [Português (Brasil)](README.pt-BR.md)

[![License: MIT](https://img.shields.io/badge/license-MIT-2f6f3e)](LICENSE)
[![Platform: Android](https://img.shields.io/badge/platform-Android-3ddc84?logo=android&logoColor=white)](#how-it-works)
[![ONNX Runtime](https://img.shields.io/badge/ONNX%20Runtime-int8-005ced?logo=onnx&logoColor=white)](https://onnxruntime.ai)
[![Python 3](https://img.shields.io/badge/python-3-3776ab?logo=python&logoColor=white)](examples/predict.py)
[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20model-andessonIF%2Fsaberia--plant--id-ffcc4d)](https://huggingface.co/andessonIF/saberia-plant-id)
[![Release](https://img.shields.io/github/v/release/Andessonreis/saberia-plant-id?color=2f6f3e)](https://github.com/Andessonreis/saberia-plant-id/releases/latest)

<img src="docs/img/screens.png" alt="SaberIA app identifying a juazeiro and an umbuzeiro offline, in airplane mode" width="520">

<sub>Real screens of the SaberIA app on an Android phone in airplane mode. Left: juazeiro (<i>Sarcomphalus joazeiro</i>), confidence 1.00. Right: umbuzeiro (<i>Spondias tuberosa</i>), confidence 0.97. About 3 s per photo. Photos from iNaturalist: <a href="https://www.inaturalist.org/observations/386235537">386235537</a> by marcello_ofiologia (CC BY) and <a href="https://www.inaturalist.org/observations/364868810">364868810</a> by taize (CC0).</sub>

</div>

---

SaberIA is an Android app, developed as an undergraduate research project (PIBITI) at IFBA Campus Irecê, that helps communities of the Brazilian semi-arid region record and check traditional knowledge about medicinal plants. This repository holds the **plant recognition part**: the on-device model, the comparison index, the curated species base, the evaluation, and a reference implementation in Python.

You take a photo. The phone computes an embedding with a quantized [BioCLIP 2](https://huggingface.co/imageomics/bioclip-2) image encoder, compares it with an index of 159 species, and shows a description that was **written in advance from cited sources**. No text is generated at inference time, nothing is sent to a server, and when the model is not confident, the app says so instead of guessing.

## Highlights

- **88.8% correct on the first option and 96.2% within the top 3**, on 5,791 iNaturalist photos of 157 species, none of them used as a reference in the index (95% CI: 88.0–89.6% and 95.7–96.7%).
- **97.2% correct when it answers.** At confidence ≥ 0.75, the app names the plant for 76.1% of photos; for the rest, it asks for another photo instead of guessing.
- **Works without internet.** A 308 MB model and a 5.5 MB index are downloaded once; after that everything runs on the phone, in airplane mode.
- **About 3 s per photo** on a mid-range phone (Redmi 12, median 3.3 s).
- **159 species with public sources.** Each entry cites Flora e Funga do Brasil, GBIF, Agra et al. (2008), RENISUS or the Brazilian Pharmacopoeia's herbal formulary.
- **No made-up text.** Descriptions were written in advance from those sources; the model only picks the species.
- **No sign of pretraining inflation.** On the 5,155 photos created on iNaturalist after BioCLIP 2's training-data cutoff, top-1 is 90.6%.
- **Open evaluation.** IDs, licenses and authors of every test photo, scripts and per-species results are in [`eval/scale/`](eval/scale/).

## Contents

- [Why](#why)
- [How it works](#how-it-works)
- [Results](#results)
- [Limitations and validity](#limitations-and-validity)
- [Quick start (Python)](#quick-start-python)
- [Methodology and reproducibility](#methodology-and-reproducibility)
- [Species in the base](#species-in-the-base)
- [Licenses and attribution](#licenses-and-attribution)
- [Citation](#citation)
- [Acknowledgements and contact](#acknowledgements-and-contact)

## Why

The Caatinga is a biome found only in Brazil, and its communities hold a large body of knowledge about medicinal plants: which part to use, how to prepare it, what it is used for. That knowledge is passed on mostly by word of mouth and is being lost with urbanization and the lack of written records.

The first version of the app identified plants with a general-purpose multimodal model in the cloud and asked it to write the description. That had three problems in the field:

| Problem | Consequence |
|---|---|
| Native Caatinga species are rare in the training data of general models | Wrong names for exactly the plants that matter most |
| Free-form generated text | Plausible but unverifiable health claims |
| Needs internet | Rural areas of the semi-arid often have weak or no signal |

This repository replaces that step with a closed-set classifier that runs on the phone and a species base where every statement has a source.

The project relates to the UN Sustainable Development Goals 3 (good health and well-being), 11.4 (safeguard cultural heritage) and 15 (life on land).

## How it works

```mermaid
flowchart LR
    A[Photo<br/>camera or gallery] --> B[Resize shorter side to 224 px<br/>center crop, normalize]
    B --> C[BioCLIP 2 image encoder<br/>ViT-L/14, ONNX, int8<br/>on the phone]
    C --> D[768-d embedding]
    D --> E{Compare with index}
    E -->|cosine similarity| F[Text vectors<br/>159 species + 1,053 other plants]
    E -->|cosine similarity| G[Reference photo vectors<br/>2,320 iNaturalist photos]
    F --> H[Combined score<br/>top-3 species + confidence]
    G --> H
    H -->|confidence >= 0.75| I[Show species and curated text<br/>with sources]
    H -->|confidence < 0.75| J[Ask for another photo]
```

1. **Encoder.** The image tower of BioCLIP 2 (ViT-L/14, trained on [TreeOfLife-200M](https://huggingface.co/datasets/imageomics/TreeOfLife-200M), about 200 million images of organisms), exported to ONNX with dynamic int8 quantization of the matrix multiplications. No fine-tuning: the weights are the original ones.
2. **Text vectors.** For each label, BioCLIP 2's text encoder embeds the scientific name and synonyms, with and without the GBIF taxonomic path (kingdom to family). Besides the 159 species of the base, the index has 1,053 other plants (PlantNet-300K species and common Brazilian ornamentals, crops and weeds). They are never shown as answers; they are there to estimate whether the photo belongs to the base at all.
3. **Reference vectors.** Up to 15 research-grade iNaturalist photos per species, observed up to 2024-12-31, embedded with the same int8 model. Only the vectors ship; the photos do not. [Index v1.0.1](#index-v101) adds 70 freely licensed photos for three species.
4. **Score.** For each species of the base: `text_similarity + 1.0 × mean(top-3 reference similarities)`, then a softmax. Confidence is `P(top-1) × P(photo is a species of the base)`. Below 0.75 the app does not name the plant.
5. **Text.** The result screen reads the entry from [`data/caatinga_species.json`](data/caatinga_species.json): popular names, family, origin, traditional uses, precautions, and links to Flora e Funga do Brasil, GBIF, Agra et al. (2008), RENISUS and the Brazilian Pharmacopoeia herbal formulary.

The model (308 MB) is downloaded once, its SHA-256 is checked, and from then on identification works in airplane mode.

## Results

The main evaluation was run on 2026-10-31 with **5,791 iNaturalist photos of 157 of the 159 species in the base**, none of them used as a reference in the index. It used the same files the app downloads (model and index checked by SHA-256), with the app's preprocessing and scoring reproduced in Python. Full report in [`eval/scale/RESULTS.md`](eval/scale/RESULTS.md) ([Português](eval/scale/RESULTS.pt-BR.md)), per-species tables in [`eval/scale/tabelas.md`](eval/scale/tabelas.md) (Portuguese), raw numbers in [`eval/scale/resultados.json`](eval/scale/resultados.json).

### Overview

App confidence threshold: 0.75. 95% Wilson confidence intervals (CI).

| Subset | Photos | Top-1 (95% CI) | Top-3 (95% CI) | Answered at threshold | Correct when answered |
|---|---:|---|---|---:|---|
| **All species** | 5,791 | **88.8%** (88.0–89.6%) | **96.2%** (95.7–96.7%) | 76.1% | **97.2%** (96.7–97.7%) |
| 22 key species | 1,986 | 84.3% (82.7–85.9%) | 94.2% (93.1–95.2%) | 67.9% | 96.1% (94.9–97.0%) |
| Other 135 species | 3,805 | 91.1% (90.2–92.0%) | 97.3% (96.7–97.7%) | 80.3% | 97.8% (97.2–98.2%) |

- **Top-1** means the right species is the first option; **top-3**, that it is among the first three. Neither column applies the threshold.
- **Answered at threshold** is the share of photos whose confidence reached 0.75, so the app named the plant. For the rest, it asks for another photo.
- **Per-species mean**, with each of the 157 species weighted equally: top-1 88.3% (bootstrap 95% CI: 87.5–89.2%) and top-3 96.0% (95.4–96.7%).

### On the phone

| Measure | Value |
|---|---|
| Model time per photo (Redmi 12, MediaTek Helio G88, 4 threads) | median **3.3 s** (3.0 to 4.8 s; 16 real identifications) |
| Photo decoding and preprocessing | median 55 ms |
| First model load, once per session | median 8.6 s (7.4 to 11.6 s; n = 6) |
| Model (`plant-classifier-int8.onnx`) | 308 MB, ONNX int8 |
| Index (`plant-index.bin`) | 5.5 MB: 159 species, 1,212 text labels, 2,320 reference vectors (v1.0.0); 5.6 MB and 2,387 vectors in [v1.0.1](#index-v101) |
| Internet | only for the first download; airplane mode after that |

Timings come from the app's own log on the device.

### How the evaluation was built

- **Photos.** Research-grade iNaturalist observations (identification confirmed by the community), "medium" size (500 px on the long side). Per species: 1 photo per observation and **at most 1 observation per observer**, so the same plant or photographer is not counted many times.
- **Size.** Target of 100 photos for the 22 key species and 30 for the others. Where there were not enough eligible photos, the real n was kept (catingueira has only 7). 146 species have n ≥ 20. *Citrus aurantium* and *Pimpinella anisum* had no eligible photo. Observations from 2025 onward came first (5,012 photos); older ones (779) only filled gaps.
- **Separated from the references, by ID.** Every observation behind the 2,320 reference photos of the index and behind the development set was excluded, 2,647 in total.
- **Separated from the references, by content.** Each test photo was compared with the references and with the other test photos by perceptual hash (64-bit dHash, up to 6 bits apart) and by embedding cosine (≥ 0.99). Five photos were removed, all repeated within the test set itself. None was a copy of a reference.
- **The same system as the app.** Preprocessing from `PlantClassifier.kt` (EXIF orientation, power-of-two downsampling, bilinear resize like `Bitmap.createScaledBitmap`, 224×224 center crop), same scoring, same threshold.
- **Statistics.** 95% Wilson CI for every rate. For the per-species mean, stratified bootstrap with 2,000 resamples (seed 20251105).
- **Observer sensitivity.** When the photographer also has a photo among the references (1,250 photos), top-1 is 87.0% (85.0–88.7%). For new observers (4,541 photos), 89.3% (88.4–90.2%). Knowing the photographer does not inflate the result.
- **Reproducible.** [`eval/scale/amostra_ids.csv`](eval/scale/amostra_ids.csv) lists every observation and photo used, with species, date, license and credit. The scripts are in [`eval/scale/scripts/`](eval/scale/scripts/). The photos are not redistributed.

### Backbone pretraining contamination

The encoder comes from BioCLIP 2, pretrained on TreeOfLife-200M, which includes iNaturalist photos. The test photos were not used as references in the index, but some of them may have gone through pretraining. According to the dataset card, the data comes from a GBIF snapshot of **2024-05-01** and from EOL accessed in **August 2024**. For every test photo, the creation date of the iNaturalist observation was downloaded:

| Observation creation date | Photos | Top-1 (95% CI) | Top-3 (95% CI) |
|---|---:|---|---|
| From 2024-09-01: certainly outside pretraining | 5,155 | **90.6%** (89.8–91.4%) | 96.9% (96.4–97.3%) |
| 2024-05-01 to 2024-08-31: could only have entered through EOL | 56 | 71.4% (58.5–81.6%) | 92.9% (83.0–97.2%) |
| Before 2024-05-01: may be in pretraining | 580 | 74.3% (70.6–77.7%) | 90.9% (88.2–93.0%) |

Photos that were certainly outside pretraining score **higher**, not lower. The raw gap comes from the species mix: older photos only entered for species with few recent photos, which are the hardest native trees. Within the same 39 species that have photos from both periods, with the same species mix, new photos score 77.8% and older ones 74.1% (n = 946 and 636). There is no sign that pretraining inflates the result.

### Photos below research grade (mini test)

A separate test with 99 observations of the key species graded "casual" or "needs ID" (created from 2024-09-01, with at least 2 agreeing identifiers) gave **88.9%** top-1 (95% CI: 81.2–93.7%) and 96.0% top-3. On the same species, the main test gives 87.8%. This measures little: 88 of the 99 photos are "casual" because the plant is cultivated, not because the photo is poor, and exactly the hard native trees were missing (pinhão-bravo, jurema-preta and quixabeira had no photo). It does not replace a test with field photos from lay users.

### Key species

Sorted by top-1. With 100 photos, the CI of one species is between ±5 and ±10 percentage points; with fewer photos it is wider.

| Species | Popular name | n | Top-1 (95% CI) | Top-3 | Answered at threshold | Correct when answered | Most common confusion |
|---|---|---:|---|---:|---:|---:|---|
| *Aloe vera* | babosa | 100 | **100.0%** (96.3–100.0%) | 100.0% | 97/100 | 97/97 | – |
| *Melocactus zehntneri* | coroa-de-frade | 99 | **100.0%** (96.3–100.0%) | 100.0% | 97/99 | 97/97 | – |
| *Cymbopogon citratus* | capim-santo | 100 | **99.0%** (94.5–99.8%) | 100.0% | 92/100 | 92/92 | *Zingiber officinale* (1) |
| *Opuntia ficus-indica* | palma | 100 | **99.0%** (94.5–99.8%) | 100.0% | 93/100 | 93/93 | *Xiquexique gounellei* (1) |
| *Schinus terebinthifolia* | aroeira-vermelha | 100 | **99.0%** (94.5–99.8%) | 99.0% | 94/100 | 94/94 | *Cnidoscolus quercifolius* (1) |
| *Lippia alba* | erva-cidreira | 99 | **97.0%** (91.5–99.0%) | 99.0% | 92/99 | 91/92 | *Lippia origanoides* (2) |
| *Xiquexique gounellei* | xique-xique | 100 | **95.0%** (88.8–97.9%) | 98.0% | 90/100 | 90/90 | *Cereus jamacaru* (3) |
| *Coleus barbatus* | boldo | 100 | **94.0%** (87.5–97.2%) | 99.0% | 77/100 | 76/77 | *Coleus amboinicus* (5) |
| *Sarcomphalus joazeiro* | juazeiro | 91 | **91.2%** (83.6–95.5%) | 97.8% | 61/91 | 60/61 | *Microdesmia rigida* (2) |
| *Cereus jamacaru* | mandacaru | 100 | **90.0%** (82.6–94.5%) | 99.0% | 23/100 | 23/23 | *Pilosocereus pachycladus* (6) |
| *Jatropha mollissima* | pinhão-bravo | 100 | **90.0%** (82.6–94.5%) | 94.0% | 83/100 | 79/83 | *Amburana cearensis* (3) |
| *Handroanthus impetiginosus* | ipê-roxo | 100 | **87.0%** (79.0–92.2%) | 94.0% | 64/100 | 64/64 | *Handroanthus serratifolius* (3) |
| *Libidibia ferrea* | jucá | 100 | **79.0%** (70.0–85.8%) | 97.0% | 58/100 | 52/58 | *Hymenaea courbaril* (6) |
| *Mimosa tenuiflora* | jurema-preta | 100 | **76.0%** (66.8–83.3%) | 95.0% | 35/100 | 33/35 | *Prosopis juliflora* (7) |
| *Sideroxylon obtusifolium* | quixabeira | 100 | **73.0%** (63.6–80.7%) | 86.0% | 53/100 | 51/53 | *Spondias mombin* (4) |
| *Spondias tuberosa* | umbuzeiro | 65 | **72.3%** (60.4–81.7%) | 90.8% | 36/65 | 33/36 | *Commiphora leptophloeos* (9) |
| *Commiphora leptophloeos* | umburana-de-cambão | 95 | **69.5%** (59.6–77.8%) | 97.9% | 52/95 | 40/52 | *Amburana cearensis* (20) |
| *Anadenanthera colubrina* | angico | 100 | **65.0%** (55.2–73.6%) | 96.0% | 40/100 | 35/40 | *Spondias mombin* (12) |
| *Amburana cearensis* | umburana-de-cheiro | 53 | **60.4%** (46.9–72.4%) | 81.1% | 25/53 | 23/25 | *Cenostigma pyramidale* (6) |
| *Erythrina velutina* | mulungu | 100 | **59.0%** (49.2–68.1%) | 76.0% | 48/100 | 36/48 | *Ceiba glaziovii* (9) |
| *Cenostigma pyramidale* | catingueira | 7 | **57.1%** (25.1–84.2%) | 85.7% | 4/7 | 4/4 | *Tabebuia aurea* (1) |
| *Astronium urundeuva* | aroeira-do-sertão | 77 | **55.8%** (44.7–66.4%) | 66.2% | 34/77 | 32/34 | *Amburana cearensis* (8) |

The other 135 species appear in the "Top-1 (n)" column of the [species table](#species-in-the-base) and, with CIs, in [`eval/scale/tabelas.md`](eval/scale/tabelas.md). 40 of them reached 100% top-1.

### Index v1.0.1

v1.0.1 reinforces the three weakest key species (aroeira-do-sertão, mulungu and umburana-de-cambão). It uses the same model, labels and threshold as v1.0.0, with a different index file (`plant-index-v1.0.1.bin`, sha256 `d8c97ff0419fcafb04201bf22ef1196c66de983e6210a0e1be89b2287cc9a5d2`). Changes:

- **+70 freely licensed references** (CC0, CC BY or CC BY-SA, none NC): 18 extra photos from iNaturalist observations already in the index and 52 field photos from Wikimedia Commons, checked one by one. Credits in [`eval/scale/index-v1.0.1/referencias_adicionadas.csv`](eval/scale/index-v1.0.1/referencias_adicionadas.csv).
- **−3 references** that were "all rights reserved" (*Genipa americana*, *Pityrocarpa moniliformis*, *Spondias mombin*). List in [`removidas_e_descartadas.json`](eval/scale/index-v1.0.1/removidas_e_descartadas.json).
- No new reference comes from a test observation, and none is a copy of a test photo.

| Top-1 | v1.0.0 | v1.0.1 |
|---|---:|---:|
| Overall, same 5,791 photos (optimistic) | 88.8% | 89.2% |
| Aroeira-do-sertão, same photos (n = 77, optimistic) | 55.8% | 76.6% |
| Mulungu, same photos (n = 100, optimistic) | 59.0% | 73.0% |
| Umburana-de-cambão, same photos (n = 95, optimistic) | 69.5% | 70.5% |
| **3 species, 117 new observations (unbiased)** | **51.3%** (42.3–60.2%) | **73.5%** (64.9–80.7%) |

The rows marked optimistic use the same test that showed which species to reinforce. The unbiased estimate is therefore the last row: 117 observations of the 3 species that had not been used for anything (test, reference or calibration), 1 per observer. On them, 26 wrong photos became right and no right photo became wrong. On the main test, 7 species lost 1 or 2 photos (the largest loss was *Erythrina mulungu*, from 24 to 22 of 30), and the out-of-base false positive rate stayed the same (37/300). Details in [`eval/scale/index-v1.0.1/`](eval/scale/index-v1.0.1/). **The headline result of this README is still v1.0.0's.**

### Plants outside the base

300 photos of 300 Brazilian plant species that are not in the base (observations from 2025 onward, drawn with a fixed seed, 1 per species and 1 per observer).

| Subset | Photos | Given the name of a species of the base (95% CI) |
|---|---:|---|
| All | 300 | 37 = 12.3% (9.1–16.5%) |
| Genus has a species in the base (another *Erythrina*, another *Melocactus*...) | 56 | 13 = 23.2% (14.1–35.8%) |
| Genus has no species in the base | 244 | 24 = 9.8% (6.7–14.2%) |

### Against other systems

Treat this as a **limited indication** only:

- **Cloud AI.** Same endpoint, prompt and parameters as the previous version of the app, on a randomly drawn subsample. The free API quota cut the calls short. Gemini 3.5 Flash answered 11 photos and got 6 right (95% CI: 28–79%). Gemini 2.5 Flash answered 20 and got 7 right (18–57%). On those same photos, SaberIA got 11/11 and 19/20. With n this small the intervals are huge: the result points in one direction but does not measure the cloud models. The OpenAI account had no credit and could not be measured.
- **Local multimodal model.** Qwen3-VL-2B got 6 of 64 photos right (9.4%; 95% CI: 4.4–19.0%), taking 2 to 3.5 min per photo on the phone. That sample is a different one, from the development set, so it does not compare side by side with the table above.

### Development set

Before the main evaluation, a smaller set was used to **choose the model and calibrate the 0.75 threshold**: 194 photos of 25 species (observations from 2025 onward) and 74 photos of 12 plants outside the base. Because it guided decisions, it is not a final measure, and its observations were excluded from the main evaluation. On it, the shipped model scored 75.8% top-1 (147/194; 95% CI: 69.3–81.3%) and 92.3% top-3. The rate is lower than in the main evaluation because 21 of the 25 species were key species, which are the hardest, and with 8 photos per species the interval is wide. Photos, licenses and authors are in [`eval/data/test_photos.csv`](eval/data/test_photos.csv).

<details>
<summary>Variants compared, local model and Python reproduction (development set)</summary>

Same 194 + 74 photos, same int8 quantization, threshold 0.75.

| Variant | Top-1 | Top-3 | Answered | Correct when answered | Out-of-base answered |
|---|---:|---:|---:|---:|---:|
| BioCLIP (v1), names only | 44.8% | 62.4% | 40% | 73.1% | 6/74 |
| BioCLIP (v1), names + reference photos | 59.8% | 76.8% | 41% | 88.6% | 5/74 |
| BioCLIP 2, names only | 68.0% | 88.1% | 55% | 85.8% | 3/74 |
| BioCLIP 2, names + reference photos, bicubic resize | 77.3% | 93.3% | 61% | 93.2% | 1/74 |
| **BioCLIP 2, names + reference photos, bilinear resize (shipped)** | **75.8%** | **92.3%** | **63%** | **91.8%** | **1/74** |

The shipped variant uses bilinear resizing because that is what Android's `Bitmap.createScaledBitmap` does. The bicubic row scores slightly higher on a PC, but bilinear is what the phone actually sees.

General-purpose local model, with the previous app prompt ("answer only with the scientific name"), on the first 64 photos (8 species × 8 photos):

| Model | Correct species | Time per photo on the phone |
|---|---:|---:|
| Qwen3-VL-2B (Q4_K_M, llama.cpp), generative | 6/64 (9.4%) | 2 to 3.5 min |
| SaberIA (BioCLIP 2 + index), same 64 photos | 45/64 (70.3%) top-1 | ~3.3 s |

Qwen often answered with real species from other regions (*Carnegiea gigantea*, the saguaro, for 6 of the 8 mandacaru photos) or with "Não sei" (I don't know). Raw answers: [`eval/data/qwen_results.txt`](eval/data/qwen_results.txt).

Running [`examples/predict.py`](examples/predict.py) with the [release](https://github.com/Andessonreis/saberia-plant-id/releases/tag/v1.0.0) files on the same photos gave 76.8% top-1, 92.3% top-3, 60% answered, 94.0% correct when answered and 1/74 false answer. Scoring the stored evaluation embeddings with the same script gives exactly 75.8%. The difference comes from run-to-run numerical variation in ONNX Runtime's int8 CPU kernels (cosine 0.994 to 1.0 between runs), which flips a few borderline photos. Expect similar small variations on other devices.

</details>

## Limitations and validity

The numbers above hold for iNaturalist photos of the species in the base. The points below mark what they do and do not say, and several of them point to the project's next step.

- **Hardest species.** Native Caatinga trees look very much alike, especially leafless in the dry season. The lowest top-1 with n ≥ 50 are aroeira-do-sertão (55.8%, n = 77), mulungu (59.0%), umburana-de-cheiro (60.4%), angico (65.0%) and umburana-de-cambão (69.5%). For several of them the right species is almost always in the top 3 (angico 96.0%, umburana-de-cambão 97.9%). Among species with few photos, errors stay within the genus: *Lippia grata* (0/4), *Hymenaea martiana* (1/11) and *Phyllanthus niruri*, taken for *P. amarus*. More reference photos are the most direct improvement: in [index v1.0.1](#index-v101), they took aroeira and mulungu, on new observations, from 30% to 85% and from 50% to 71%. Angico, umburana-de-cheiro and umburana-de-cambão still need more references, with trunk, bark and leafless plants.
- **Mandacaru.** Top-1 is 90%, but only 23 of 100 photos pass the threshold. Confidence is split with other columnar cacti, mainly facheiro (*Pilosocereus pachycladus*).
- **Backbone pretraining.** BioCLIP 2 was trained on TreeOfLife-200M, which includes iNaturalist images. Some test photos may have been seen while the encoder was pretrained, even though none was used as a reference in the index. The analysis by observation creation date ([above](#backbone-pretraining-contamination)) shows no inflation: on the 5,155 photos created after the cutoff, top-1 is 90.6%, above the overall 88.8%. The conservative number to quote is still 88.8%.
- **Research photos are easier than field photos.** On iNaturalist, photographers usually know the plant and frame flowers or fruit in good light. A hurried photo of a loose leaf or a dry trunk tends to score lower. The numbers are a realistic ceiling, not a field guarantee. The mini test with photos below research grade showed no drop, but almost all of them were cultivated plants. The next step is to measure with photos taken in the community workshops.
- **Plants outside the base get a guess.** The system is closed-set: it can only name the 159 species. For 12.3% of outside plants it accepted the name of a species in the base, and for 23.2% when the genus is in the base. The app tells the user to confirm the identification, and that warning is still needed.
- **Reference photo licenses.** Most reference and test photos are CC BY-NC. The index holds only numeric vectors derived from them, not the images, and the test photos are not redistributed. For commercial use, check whether this fits your case. Three reference photos that turned out to be "all rights reserved" were dropped in index v1.0.1, which only added CC0, CC BY and CC BY-SA photos, with credits listed.
- **Per-species sample size.** With 30 photos, a species at 90% has a CI of about 74 to 97%. Small differences between species are not significant.
- **iNaturalist labels.** Research grade requires 2/3 agreement among identifiers, but misidentifications still happen. That tends to pull the measured accuracy down, not up.
- **Human validation.** Identification and texts support, but do not replace, validation by a botanist and guidance from a health professional. The app keeps a human validation step for community records.

## Quick start (Python)

Download the model, the index and the species base from the [release](https://github.com/Andessonreis/saberia-plant-id/releases/tag/v1.0.0) (or from [Hugging Face](https://huggingface.co/andessonIF/saberia-plant-id)) and check the hashes:

```bash
pip install onnxruntime numpy pillow
BASE=https://github.com/Andessonreis/saberia-plant-id/releases/download/v1.0.0
for f in plant-classifier-int8.onnx plant-index.bin caatinga_species.json SHA256SUMS; do
  curl -LO "$BASE/$f"
done
sha256sum -c SHA256SUMS
```

Then run [`examples/predict.py`](examples/predict.py), which reproduces the app's scoring (`PlantClassifier.kt`):

```bash
python examples/predict.py my_photo.jpg
```

```text
my_photo.jpg: confidence 0.86
  -> Cereus jamacaru (mandacaru, cardeiro)
     source: https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/
```

The core of it, if you want to embed it in your own code:

```python
import json, struct
import numpy as np, onnxruntime as ort
from PIL import Image

# index: int32 header size, JSON header, float16 vectors (one per label, then one per reference photo)
with open("plant-index.bin", "rb") as f:
    h = json.loads(f.read(struct.unpack("<i", f.read(4))[0]))
    v = np.frombuffer(f.read(), "<f2").astype(np.float32).reshape(-1, h["dim"])
text, refs = v[: len(h["labels"])], v[len(h["labels"]):]

def preprocess(path):  # shorter side -> 224 (bilinear), center crop, CLIP normalization
    im = Image.open(path).convert("RGB"); s = 224 / min(im.size)
    im = im.resize((max(224, round(im.width * s)), max(224, round(im.height * s))), Image.BILINEAR)
    l, t = (im.width - 224) // 2, (im.height - 224) // 2
    x = (np.asarray(im.crop((l, t, l + 224, t + 224)), np.float32) / 255 - h["mean"]) / h["std"]
    return x.transpose(2, 0, 1)[None].astype(np.float32)

session = ort.InferenceSession("plant-classifier-int8.onnx")
x = session.run(None, {"pixel_values": preprocess("my_photo.jpg")})[0][0]  # 768-d, L2-normalized

def softmax(z, scale): e = np.exp((z - z.max()) * scale); return e / e.sum()
catalog = [i for i, label in enumerate(h["labels"]) if "id" in label]   # the 159 species of the base
owner = np.array(h["refs"])                                              # label index of each reference photo
t = text @ x
p_in_base = softmax(t, h["scale"])[catalog].sum()
visual = [np.sort(refs[owner == i] @ x)[-h["k"]:].mean() for i in catalog]
prob = softmax(t[catalog] + h["weight"] * np.array(visual), h["scale"] / (1 + h["weight"]))
best = int(prob.argmax())
confidence = prob[best] * p_in_base
print(h["labels"][catalog[best]]["name"], round(float(confidence), 2),
      "answer" if confidence >= h["threshold"] else "not sure")
```

Model input and output:

| | |
|---|---|
| Input `pixel_values` | `float32 [1, 3, 224, 224]`, RGB, mean `0.48145466, 0.4578275, 0.40821073`, std `0.26862954, 0.26130258, 0.27577711` |
| Output `embedding` | `float32 [1, 768]`, L2-normalized |
| Index parameters | `scale` 100, `weight` 1.0, `k` 3, `threshold` 0.75 (read from the index header) |

## Methodology and reproducibility

The main evaluation lives in [`eval/scale/`](eval/scale/): report, tables, photo list, and the scripts for collection, evaluation, cloud comparison and table generation. No script stores an API key; the cloud key is read from a file passed on the command line.

The [`eval/`](eval/) folder also has the scripts used to build the index and to evaluate on the development set, and [`eval/README.md`](eval/README.md) lists the order to run them. In short:

1. `build_labels.py`: label list (159 species + 1,053 other plants) with GBIF taxonomy.
2. `fetch_refs.py`: up to 15 reference photos per species from iNaturalist, observed up to 2024-12-31, Brazil first.
3. `fetch_photos.py`: development-set photos, research grade, observed from 2025-01-01.
4. `export_onnx.py`: export BioCLIP 2's image encoder to ONNX and quantize to int8.
5. `embed.py` and `embed_onnx.py`: text vectors (PyTorch/OpenCLIP) and image vectors (ONNX int8, bilinear resize).
6. `evaluate.py`: top-1/top-3 and the confidence-threshold table.
7. `build_index.py`: write `plant-index.bin`.

Photos are not redistributed: most are CC BY-NC. The CSV files in [`eval/data/`](eval/data/) list every observation ID, license and author, so the same photos can be downloaded again from iNaturalist.

## Species in the base

159 species: 99 native (24 endemic to Brazil) and 60 exotic species that are cultivated or naturalized and widely used in the region. 47 are on RENISUS, the Brazilian Ministry of Health list of medicinal plants of interest to the public health system. The "Top-1 (n)" column gives the first-option accuracy and the number of photos of each species in the [main evaluation](#results); "–" marks a species with no eligible photo.

Source keys: **Flora** = Flora e Funga do Brasil (JBRJ), **GBIF** = GBIF Backbone Taxonomy, **Agra 2008** = Agra et al., *Survey of medicinal plants used in the region Northeast of Brazil*, Rev. Bras. Farmacogn. 18(3), **RENISUS** = Ministry of Health, **FFFB** = ANVISA, *Formulário de Fitoterápicos da Farmacopeia Brasileira*, **art.** = specific scientific article.

<details>
<summary>Show all 159 species</summary>

| # | Scientific name | Popular names | Family | Origin | Ref. photos | Top-1 (n) | Sources |
|---:|---|---|---|---|---:|:---:|---|
| 1 | *Acanthospermum hispidum* | espinho-de-cigano, carrapicho, retirante | Asteraceae | native | 15 | 100.0% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB103232) · [GBIF](https://www.gbif.org/species/3100375) |
| 2 | *Ageratum conyzoides* | mentrasto, catinga-de-bode | Asteraceae | native | 15 | 100.0% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB15934) · [GBIF](https://www.gbif.org/species/5401673) |
| 3 | *Allium cepa* | cebola | Amaryllidaceae | exotic, cultivated | 15 | 93.3% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB611758) · [GBIF](https://www.gbif.org/species/2857697) |
| 4 | *Allium sativum* | alho | Amaryllidaceae | exotic, cultivated | 15 | 96.7% (30) | [FFFB](https://bibliotecadigital.anvisa.gov.br/jspui/handle/anvisa/21045) · [RENISUS](https://www.gov.br/saude/pt-br/composicao/sectics/plantas-medicinais-e-fitoterapicos/ppnpmf/arquivos/2014/renisus.pdf) · [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB611763) · [GBIF](https://www.gbif.org/species/2856681) |
| 5 | *Aloe vera* | babosa | Asphodelaceae | exotic, cultivated | 15 | 100.0% (100) | [FFFB](https://bibliotecadigital.anvisa.gov.br/jspui/handle/anvisa/21045) · [RENISUS](https://www.gov.br/saude/pt-br/composicao/sectics/plantas-medicinais-e-fitoterapicos/ppnpmf/arquivos/2014/renisus.pdf) · [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB609263) · [GBIF](https://www.gbif.org/species/2777724) |
| 6 | *Alpinia zerumbet* | colônia, gengibre-concha | Zingiberaceae | exotic, cultivated | 15 | 93.3% (30) | [FFFB](https://bibliotecadigital.anvisa.gov.br/jspui/handle/anvisa/21045) · [RENISUS](https://www.gov.br/saude/pt-br/composicao/sectics/plantas-medicinais-e-fitoterapicos/ppnpmf/arquivos/2014/renisus.pdf) · [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB110703) · [GBIF](https://www.gbif.org/species/5301979) |
| 7 | *Alternanthera brasiliana* | terramicina, perpétua-do-brasil, penicilina | Amaranthaceae | native | 15 | 96.7% (30) | [FFFB](https://bibliotecadigital.anvisa.gov.br/jspui/handle/anvisa/21045) · [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB4302) · [GBIF](https://www.gbif.org/species/3084934) |
| 8 | *Amburana cearensis* | umburana-de-cheiro, cumaru, amburana | Fabaceae | native | 15 | 60.4% (53) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB22781) · [GBIF](https://www.gbif.org/species/2945821) |
| 9 | *Anacardium occidentale* | cajueiro, caju | Anacardiaceae | native | 15 | 93.3% (30) | [FFFB](https://bibliotecadigital.anvisa.gov.br/jspui/handle/anvisa/21045) · [RENISUS](https://www.gov.br/saude/pt-br/composicao/sectics/plantas-medicinais-e-fitoterapicos/ppnpmf/arquivos/2014/renisus.pdf) · [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB4381) · [GBIF](https://www.gbif.org/species/5421368) |
| 10 | *Anadenanthera colubrina* | angico, angico-vermelho, angico-de-caroço | Fabaceae | native | 15 | 65.0% (100) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB18071) · [GBIF](https://www.gbif.org/species/2952823) |
| 11 | *Ananas comosus* | abacaxi, ananás | Bromeliaceae | native | 15 | 93.3% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [RENISUS](https://www.gov.br/saude/pt-br/composicao/sectics/plantas-medicinais-e-fitoterapicos/ppnpmf/arquivos/2014/renisus.pdf) · [Flora](https://floradobrasil.jbrj.gov.br/FB16574) · [GBIF](https://www.gbif.org/species/5288819) |
| 12 | *Annona squamosa* | pinha, ata, fruta-do-conde | Annonaceae | exotic, naturalized | 15 | 90.0% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB117273) · [GBIF](https://www.gbif.org/species/5407099) |
| 13 | *Artemisia absinthium* | losna, absinto, erva-dos-vermes | Asteraceae | exotic, cultivated | 15 | 100.0% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [RENISUS](https://www.gov.br/saude/pt-br/composicao/sectics/plantas-medicinais-e-fitoterapicos/ppnpmf/arquivos/2014/renisus.pdf) · [Flora](https://floradobrasil.jbrj.gov.br/FB612129) · [GBIF](https://www.gbif.org/species/3121319) |
| 14 | *Aspidosperma pyrifolium* | pereiro, pau-pereiro | Apocynaceae | native | 15 | 90.0% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB15551) · [GBIF](https://www.gbif.org/species/7316881) |
| 15 | *Astronium urundeuva* | aroeira-do-sertão, aroeira, urundeúva | Anacardiaceae | native | 14 | 55.8% (77) | [FFFB](https://bibliotecadigital.anvisa.gov.br/jspui/handle/anvisa/21045) · [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB115185) · [GBIF](https://www.gbif.org/species/3660652) |
| 16 | *Attalea speciosa* | babaçu, coco-palmeira | Arecaceae | native, endemic to Brazil | 15 | 86.7% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [RENISUS](https://www.gov.br/saude/pt-br/composicao/sectics/plantas-medicinais-e-fitoterapicos/ppnpmf/arquivos/2014/renisus.pdf) · [Flora](https://floradobrasil.jbrj.gov.br/FB15686) · [GBIF](https://www.gbif.org/species/2732877) |
| 17 | *Bauhinia cheilantha* | mororó, pata-de-vaca | Fabaceae | native | 15 | 72.0% (25) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB82659) · [GBIF](https://www.gbif.org/species/2952938) |
| 18 | *Bauhinia forficata* | pata-de-vaca, mororó | Fabaceae | native | 15 | 80.0% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [RENISUS](https://www.gov.br/saude/pt-br/composicao/sectics/plantas-medicinais-e-fitoterapicos/ppnpmf/arquivos/2014/renisus.pdf) · [Flora](https://floradobrasil.jbrj.gov.br/FB82666) · [GBIF](https://www.gbif.org/species/2953861) |
| 19 | *Bidens pilosa* | picão-preto, picão, carrapicho-de-agulha | Asteraceae | exotic, naturalized | 15 | 100.0% (30) | [FFFB](https://bibliotecadigital.anvisa.gov.br/jspui/handle/anvisa/21045) · [RENISUS](https://www.gov.br/saude/pt-br/composicao/sectics/plantas-medicinais-e-fitoterapicos/ppnpmf/arquivos/2014/renisus.pdf) · [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB103749) · [GBIF](https://www.gbif.org/species/5391845) |
| 20 | *Bixa orellana* | urucum, colorau, açafroa | Bixaceae | native | 15 | 96.7% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB5745) · [GBIF](https://www.gbif.org/species/2874863) |
| 21 | *Bowdichia virgilioides* | sucupira, sucupira-preta | Fabaceae | native | 15 | 86.7% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB29489) · [GBIF](https://www.gbif.org/species/2975476) |
| 22 | *Bromelia laciniosa* | macambira | Bromeliaceae | native, endemic to Brazil | 15 | 100.0% (11) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB16578) · [GBIF](https://www.gbif.org/species/5287936) |
| 23 | *Byrsonima crassifolia* | murici, murici-da-praia | Malpighiaceae | native | 15 | 80.0% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB19419) · [GBIF](https://www.gbif.org/species/3191361) |
| 24 | *Cajanus cajan* | feijão-guandu, guandu, andu | Fabaceae | exotic, naturalized | 15 | 96.7% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB82709) · [GBIF](https://www.gbif.org/species/7587087) |
| 25 | *Calotropis procera* | algodão-de-seda, flor-de-seda, ciúme | Apocynaceae | exotic, naturalized | 15 | 100.0% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB80340) · [GBIF](https://www.gbif.org/species/5414566) |
| 26 | *Capraria biflora* | chá-da-calçada, chá-preto, mate | Scrophulariaceae | native | 15 | 100.0% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB25821) · [GBIF](https://www.gbif.org/species/3171842) |
| 27 | *Carica papaya* | mamão, mamoeiro | Caricaceae | exotic, naturalized | 15 | 100.0% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB22405) · [GBIF](https://www.gbif.org/species/2874484) |
| 28 | *Casearia sylvestris* | guaçatonga, pau-de-lagarto, língua-de-tiú | Salicaceae | native | 15 | 93.3% (30) | [FFFB](https://bibliotecadigital.anvisa.gov.br/jspui/handle/anvisa/21045) · [RENISUS](https://www.gov.br/saude/pt-br/composicao/sectics/plantas-medicinais-e-fitoterapicos/ppnpmf/arquivos/2014/renisus.pdf) · [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB14384) · [GBIF](https://www.gbif.org/species/5331148) |
| 29 | *Ceiba glaziovii* | barriguda, barriguda-de-espinho | Malvaceae | native, endemic to Brazil | 15 | 100.0% (29) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB9035) · [GBIF](https://www.gbif.org/species/7813916) |
| 30 | *Cenostigma pyramidale* | catingueira, catingueira-verdadeira | Fabaceae | native, endemic to Brazil | 13 | 57.1% (7) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB606076) · [GBIF](https://www.gbif.org/species/9462202) |
| 31 | *Cereus jamacaru* | mandacaru, cardeiro, jamacaru | Cactaceae | native, endemic to Brazil | 15 | 90.0% (100) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB1447) · [GBIF](https://www.gbif.org/species/7282182) |
| 32 | *Cinnamomum verum* | canela, canela-do-ceilão, caneleira | Lauraceae | exotic, cultivated | 15 | 100.0% (30) | [FFFB](https://bibliotecadigital.anvisa.gov.br/jspui/handle/anvisa/21045) · [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB25614) · [GBIF](https://www.gbif.org/species/3033987) |
| 33 | *Cissus verticillata* | insulina, insulina-vegetal, cipó-pucá | Vitaceae | native | 15 | 96.7% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB15270) · [GBIF](https://www.gbif.org/species/3039173) |
| 34 | *Citrus aurantium* | laranja-da-terra, laranja-amarga, laranja-azeda | Rutaceae | exotic, cultivated | 15 | – | [FFFB](https://bibliotecadigital.anvisa.gov.br/jspui/handle/anvisa/21045) · [Flora](https://floradobrasil.jbrj.gov.br/FB611574) · [GBIF](https://www.gbif.org/species/8077391) |
| 35 | *Cnidoscolus quercifolius* | faveleira, favela, faveleiro | Euphorbiaceae | native, endemic to Brazil | 15 | 90.0% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB17494) · [GBIF](https://www.gbif.org/species/3073448) |
| 36 | *Cnidoscolus urens* | cansanção, urtiga-branca, urtiga | Euphorbiaceae | native | 15 | 90.0% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB17495) · [GBIF](https://www.gbif.org/species/3073653) |
| 37 | *Cocos nucifera* | coqueiro, coco, coco-da-baía | Arecaceae | exotic, naturalized | 15 | 100.0% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB80541) · [GBIF](https://www.gbif.org/species/2735117) |
| 38 | *Coleus amboinicus* | hortelã-graúda, malvarisco, malva | Lamiaceae | exotic, cultivated | 15 | 93.3% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB23336) · [GBIF](https://www.gbif.org/species/5341313) |
| 39 | *Coleus barbatus* | boldo, boldo-brasileiro, boldo-nacional | Lamiaceae | exotic, cultivated | 15 | 94.0% (100) | [FFFB](https://bibliotecadigital.anvisa.gov.br/jspui/handle/anvisa/21045) · [RENISUS](https://www.gov.br/saude/pt-br/composicao/sectics/plantas-medicinais-e-fitoterapicos/ppnpmf/arquivos/2014/renisus.pdf) · [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB84186) · [GBIF](https://www.gbif.org/species/8030165) |
| 40 | *Coleus comosus* | boldo-gambá, boldo-pequeno, novalgina | Lamiaceae | exotic, cultivated | 10 | 87.5% (8) | [art.](https://repositorio.ufc.br/ri/bitstream/riufc/23729/3/2015%20_dis%20_fnavila.pdf) · [Flora](https://floradobrasil.jbrj.gov.br/FB637468) · [GBIF](https://www.gbif.org/species/5605775) |
| 41 | *Combretum leprosum* | mofumbo, mufumbo, pente-de-macaco | Combretaceae | native | 15 | 93.3% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB6906) · [GBIF](https://www.gbif.org/species/3698829) |
| 42 | *Commiphora leptophloeos* | umburana-de-cambão, imburana, imburana-de-cambão | Burseraceae | native | 15 | 69.5% (95) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB16657) · [GBIF](https://www.gbif.org/species/3993388) |
| 43 | *Copaifera langsdorffii* | copaíba, pau-d'óleo | Fabaceae | native | 15 | 53.3% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [RENISUS](https://www.gov.br/saude/pt-br/composicao/sectics/plantas-medicinais-e-fitoterapicos/ppnpmf/arquivos/2014/renisus.pdf) · [Flora](https://floradobrasil.jbrj.gov.br/FB22896) · [GBIF](https://www.gbif.org/species/2978171) |
| 44 | *Copernicia prunifera* | carnaúba, carnaubeira | Arecaceae | native, endemic to Brazil | 15 | 100.0% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB15706) · [GBIF](https://www.gbif.org/species/2738262) |
| 45 | *Cordia oncocalyx* | pau-branco | Cordiaceae | native, endemic to Brazil | 10 | 71.4% (21) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB127463) · [GBIF](https://www.gbif.org/species/5661249) |
| 46 | *Coriandrum sativum* | coentro | Apiaceae | exotic, cultivated | 15 | 93.3% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB111826) · [GBIF](https://www.gbif.org/species/3034871) |
| 47 | *Croton blanchetianus* | marmeleiro, marmeleiro-da-caatinga | Euphorbiaceae | native, endemic to Brazil | 15 | 90.0% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB25478) · [GBIF](https://www.gbif.org/species/3059075) |
| 48 | *Croton grewioides* | canela-de-cunhã, canelinha, alecrim-de-cabocla | Euphorbiaceae | native | 4 | 20.0% (5) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [RENISUS](https://www.gov.br/saude/pt-br/composicao/sectics/plantas-medicinais-e-fitoterapicos/ppnpmf/arquivos/2014/renisus.pdf) · [Flora](https://floradobrasil.jbrj.gov.br/FB17516) · [GBIF](https://www.gbif.org/species/3058458) |
| 49 | *Croton heliotropiifolius* | velame, velaminho, velame-de-cheiro | Euphorbiaceae | native | 15 | 96.7% (30) | [art.](https://www.alice.cnptia.embrapa.br/alice/bitstream/doc/935899/1/AnaValeria14.pdf) · [Flora](https://floradobrasil.jbrj.gov.br/FB17517) · [GBIF](https://www.gbif.org/species/3060038) |
| 50 | *Curcuma longa* | açafrão-da-terra, cúrcuma, açafrão | Zingiberaceae | exotic, cultivated | 15 | 96.7% (30) | [FFFB](https://bibliotecadigital.anvisa.gov.br/jspui/handle/anvisa/21045) · [RENISUS](https://www.gov.br/saude/pt-br/composicao/sectics/plantas-medicinais-e-fitoterapicos/ppnpmf/arquivos/2014/renisus.pdf) · [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [GBIF](https://www.gbif.org/species/2757624) |
| 51 | *Cymbopogon citratus* | capim-santo, capim-limão, capim-cidreira | Poaceae | exotic, naturalized | 15 | 99.0% (100) | [FFFB](https://bibliotecadigital.anvisa.gov.br/jspui/handle/anvisa/21045) · [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB24285) · [GBIF](https://www.gbif.org/species/2705275) |
| 52 | *Dysphania ambrosioides* | mastruz, mastruço, erva-de-santa-maria | Amaranthaceae | exotic, naturalized | 15 | 100.0% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [RENISUS](https://www.gov.br/saude/pt-br/composicao/sectics/plantas-medicinais-e-fitoterapicos/ppnpmf/arquivos/2014/renisus.pdf) · [Flora](https://floradobrasil.jbrj.gov.br/FB139867) · [GBIF](https://www.gbif.org/species/5568446) |
| 53 | *Egletes viscosa* | macela, macela-da-terra, macela-do-campo | Asteraceae | native | 15 | 100.0% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB16094) · [GBIF](https://www.gbif.org/species/3118721) |
| 54 | *Erythrina mulungu* | mulungu | Fabaceae | native | 15 | 80.0% (30) | [FFFB](https://bibliotecadigital.anvisa.gov.br/jspui/handle/anvisa/21045) · [RENISUS](https://www.gov.br/saude/pt-br/composicao/sectics/plantas-medicinais-e-fitoterapicos/ppnpmf/arquivos/2014/renisus.pdf) · [Flora](https://floradobrasil.jbrj.gov.br/FB105155) · [GBIF](https://www.gbif.org/species/5349691) |
| 55 | *Erythrina velutina* | mulungu, mulungu-da-caatinga | Fabaceae | native | 15 | 59.0% (100) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB29679) · [GBIF](https://www.gbif.org/species/5349685) |
| 56 | *Eugenia uniflora* | pitangueira, pitanga | Myrtaceae | native | 15 | 86.7% (30) | [FFFB](https://bibliotecadigital.anvisa.gov.br/jspui/handle/anvisa/21045) · [RENISUS](https://www.gov.br/saude/pt-br/composicao/sectics/plantas-medicinais-e-fitoterapicos/ppnpmf/arquivos/2014/renisus.pdf) · [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB10560) · [GBIF](https://www.gbif.org/species/5416458) |
| 57 | *Euphorbia tirucalli* | avelós, aveloz, pau-pelado | Euphorbiaceae | exotic, cultivated | 15 | 100.0% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB609672) · [GBIF](https://www.gbif.org/species/3069353) |
| 58 | *Foeniculum vulgare* | funcho, erva-doce | Apiaceae | exotic, cultivated | 15 | 100.0% (30) | [FFFB](https://bibliotecadigital.anvisa.gov.br/jspui/handle/anvisa/21045) · [RENISUS](https://www.gov.br/saude/pt-br/composicao/sectics/plantas-medicinais-e-fitoterapicos/ppnpmf/arquivos/2014/renisus.pdf) · [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB21886) · [GBIF](https://www.gbif.org/species/3034922) |
| 59 | *Genipa americana* | jenipapo, jenipapeiro | Rubiaceae | native | 15 | 70.0% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB14045) · [GBIF](https://www.gbif.org/species/2895593) |
| 60 | *Gossypium barbadense* | algodoeiro, algodão | Malvaceae | exotic, naturalized | 15 | 93.3% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB19517) · [GBIF](https://www.gbif.org/species/3152666) |
| 61 | *Gymnanthemum amygdalinum* | boldo-baiano, alumã, boldo | Asteraceae | exotic, naturalized | 15 | 90.0% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [RENISUS](https://www.gov.br/saude/pt-br/composicao/sectics/plantas-medicinais-e-fitoterapicos/ppnpmf/arquivos/2014/renisus.pdf) · [Flora](https://floradobrasil.jbrj.gov.br/FB22218) · [GBIF](https://www.gbif.org/species/3130899) |
| 62 | *Hancornia speciosa* | mangabeira, mangaba | Apocynaceae | native | 15 | 83.3% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB15558) · [GBIF](https://www.gbif.org/species/3169679) |
| 63 | *Handroanthus impetiginosus* | ipê-roxo, pau-d'arco-roxo, pau-d'arco | Bignoniaceae | native | 15 | 87.0% (100) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [RENISUS](https://www.gov.br/saude/pt-br/composicao/sectics/plantas-medicinais-e-fitoterapicos/ppnpmf/arquivos/2014/renisus.pdf) · [Flora](https://floradobrasil.jbrj.gov.br/FB114086) · [GBIF](https://www.gbif.org/species/4092242) |
| 64 | *Handroanthus serratifolius* | pau-d'arco-amarelo, ipê-amarelo | Bignoniaceae | native | 15 | 60.0% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB117466) · [GBIF](https://www.gbif.org/species/4092017) |
| 65 | *Harrisia adscendens* | rabo-de-raposa, cacto-rabo-de-raposa | Cactaceae | native, endemic to Brazil | 15 | 96.7% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB1540) · [GBIF](https://www.gbif.org/species/5622072) |
| 66 | *Heliotropium indicum* | crista-de-galo, fedegoso, crista-de-peru | Heliotropiaceae | native | 15 | 100.0% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB16545) · [GBIF](https://www.gbif.org/species/2925788) |
| 67 | *Hymenaea courbaril* | jatobá | Fabaceae | native | 15 | 76.7% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB22972) · [GBIF](https://www.gbif.org/species/2950750) |
| 68 | *Hymenaea martiana* | jatobá | Fabaceae | native | 6 | 9.1% (11) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB83203) · [GBIF](https://www.gbif.org/species/2950768) |
| 69 | *Hymenaea stigonocarpa* | jatobá, jatobá-do-cerrado, jatobá-da-casca-fina | Fabaceae | native | 15 | 76.7% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB83206) · [GBIF](https://www.gbif.org/species/2950722) |
| 70 | *Ipomoea asarifolia* | salsa, salsa-brava, batata-brava | Convolvulaceae | native | 15 | 100.0% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB7026) · [GBIF](https://www.gbif.org/species/2928595) |
| 71 | *Jatropha curcas* | pinhão-manso, pinhão, pinhão-branco | Euphorbiaceae | exotic, naturalized | 15 | 96.7% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB22713) · [GBIF](https://www.gbif.org/species/3072953) |
| 72 | *Jatropha gossypiifolia* | pinhão-roxo | Euphorbiaceae | native | 15 | 96.7% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [RENISUS](https://www.gov.br/saude/pt-br/composicao/sectics/plantas-medicinais-e-fitoterapicos/ppnpmf/arquivos/2014/renisus.pdf) · [Flora](https://floradobrasil.jbrj.gov.br/FB17581) · [GBIF](https://www.gbif.org/species/3072900) |
| 73 | *Jatropha mollissima* | pinhão-bravo, pinhão-roxo, pinhão-vermelho | Euphorbiaceae | native | 15 | 90.0% (100) | [art.](https://ojs.uel.br/revistas/uel/index.php/semagrarias/article/view/33642) · [art.](https://www.uece.br/cecitecwp/wp-content/uploads/sites/42/2016/12/1516-0572-rbpm-18-2-s1-0582.pdf) · [Flora](https://floradobrasil.jbrj.gov.br/FB17582) · [GBIF](https://www.gbif.org/species/3073075) |
| 74 | *Justicia pectoralis* | chambá, anador | Acanthaceae | native | 15 | 93.3% (30) | [FFFB](https://bibliotecadigital.anvisa.gov.br/jspui/handle/anvisa/21045) · [RENISUS](https://www.gov.br/saude/pt-br/composicao/sectics/plantas-medicinais-e-fitoterapicos/ppnpmf/arquivos/2014/renisus.pdf) · [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB21673) · [GBIF](https://www.gbif.org/species/7624130) |
| 75 | *Kalanchoe crenata* | saião, coirama-branca, folha-grossa | Crassulaceae | exotic, naturalized | 14 | 61.5% (13) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB102470) · [GBIF](https://www.gbif.org/species/6441622) |
| 76 | *Kalanchoe pinnata* | folha-da-fortuna, saião, folha-da-costa | Crassulaceae | exotic, naturalized | 15 | 100.0% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [RENISUS](https://www.gov.br/saude/pt-br/composicao/sectics/plantas-medicinais-e-fitoterapicos/ppnpmf/arquivos/2014/renisus.pdf) · [Flora](https://floradobrasil.jbrj.gov.br/FB22581) · [GBIF](https://www.gbif.org/species/2985930) |
| 77 | *Lantana camara* | camará, chumbinho, cambará | Verbenaceae | exotic, naturalized | 15 | 100.0% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB15164) · [GBIF](https://www.gbif.org/species/2925303) |
| 78 | *Leonotis nepetifolia* | cordão-de-frade, cordão-de-são-francisco, rubim | Lamiaceae | exotic, naturalized | 15 | 100.0% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB17909) · [GBIF](https://www.gbif.org/species/4924659) |
| 79 | *Libidibia ferrea* | jucá, pau-ferro | Fabaceae | native, endemic to Brazil | 15 | 79.0% (100) | [FFFB](https://bibliotecadigital.anvisa.gov.br/jspui/handle/anvisa/21045) · [RENISUS](https://www.gov.br/saude/pt-br/composicao/sectics/plantas-medicinais-e-fitoterapicos/ppnpmf/arquivos/2014/renisus.pdf) · [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB109828) · [GBIF](https://www.gbif.org/species/5832783) |
| 80 | *Lippia alba* | erva-cidreira, cidreira, erva-cidreira-de-arbusto | Verbenaceae | native | 15 | 97.0% (99) | [FFFB](https://bibliotecadigital.anvisa.gov.br/jspui/handle/anvisa/21045) · [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB15171) · [GBIF](https://www.gbif.org/species/2925385) |
| 81 | *Lippia grata* | alecrim-pimenta, alecrim-de-serrote, alecrim-da-chapada | Verbenaceae | native | 4 | 0.0% (4) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB21441) · [GBIF](https://www.gbif.org/species/4084112) |
| 82 | *Lippia origanoides* | alecrim-pimenta, alecrim-do-mato, alecrim-de-tabuleiro | Verbenaceae | native | 15 | 100.0% (30) | [FFFB](https://bibliotecadigital.anvisa.gov.br/jspui/handle/anvisa/21045) · [RENISUS](https://www.gov.br/saude/pt-br/composicao/sectics/plantas-medicinais-e-fitoterapicos/ppnpmf/arquivos/2014/renisus.pdf) · [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB21449) · [GBIF](https://www.gbif.org/species/7297353) |
| 83 | *Luffa operculata* | cabacinha, buchinha, buchinha-do-norte | Cucurbitaceae | native | 13 | 87.0% (23) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB17091) · [GBIF](https://www.gbif.org/species/2874603) |
| 84 | *Malpighia emarginata* | acerola, aceroleira | Malpighiaceae | exotic, cultivated | 15 | 93.3% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB617494) · [GBIF](https://www.gbif.org/species/5421427) |
| 85 | *Mangifera indica* | mangueira, manga | Anacardiaceae | exotic, cultivated | 15 | 86.7% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB80029) · [GBIF](https://www.gbif.org/species/3190638) |
| 86 | *Manihot glaziovii* | maniçoba | Euphorbiaceae | native, endemic to Brazil | 15 | 100.0% (2) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB17601) · [GBIF](https://www.gbif.org/species/6709094) |
| 87 | *Marsypianthes chamaedrys* | hortelã-do-mato, betônica-brava | Lamiaceae | native | 15 | 96.7% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB8272) · [GBIF](https://www.gbif.org/species/2926970) |
| 88 | *Matricaria chamomilla* | camomila, camomila-vulgar, maçanilha | Asteraceae | exotic, cultivated | 15 | 100.0% (30) | [FFFB](https://bibliotecadigital.anvisa.gov.br/jspui/handle/anvisa/21045) · [RENISUS](https://www.gov.br/saude/pt-br/composicao/sectics/plantas-medicinais-e-fitoterapicos/ppnpmf/arquivos/2014/renisus.pdf) · [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB80681) · [GBIF](https://www.gbif.org/species/8370958) |
| 89 | *Melissa officinalis* | melissa, erva-cidreira, cidreira-verdadeira | Lamiaceae | exotic, cultivated | 15 | 96.7% (30) | [FFFB](https://bibliotecadigital.anvisa.gov.br/jspui/handle/anvisa/21045) · [Flora](https://floradobrasil.jbrj.gov.br/FB84196) · [GBIF](https://www.gbif.org/species/5341501) |
| 90 | *Melocactus zehntneri* | coroa-de-frade, cabeça-de-frade | Cactaceae | native, endemic to Brazil | 15 | 100.0% (99) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB1595) · [GBIF](https://www.gbif.org/species/8127764) |
| 91 | *Mentha pulegium* | poejo | Lamiaceae | exotic, cultivated | 15 | 96.7% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [RENISUS](https://www.gov.br/saude/pt-br/composicao/sectics/plantas-medicinais-e-fitoterapicos/ppnpmf/arquivos/2014/renisus.pdf) · [Flora](https://floradobrasil.jbrj.gov.br/FB23330) · [GBIF](https://www.gbif.org/species/2927189) |
| 92 | *Mentha spicata* | hortelã, hortelã-rasteira, hortelã-verde | Lamiaceae | exotic, naturalized | 15 | 80.0% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [RENISUS](https://www.gov.br/saude/pt-br/composicao/sectics/plantas-medicinais-e-fitoterapicos/ppnpmf/arquivos/2014/renisus.pdf) · [Flora](https://floradobrasil.jbrj.gov.br/FB36582) · [GBIF](https://www.gbif.org/species/2927175) |
| 93 | *Mentha × piperita* | hortelã-pimenta, menta | Lamiaceae | exotic, cultivated | 15 | 83.3% (30) | [FFFB](https://bibliotecadigital.anvisa.gov.br/jspui/handle/anvisa/21045) · [RENISUS](https://www.gov.br/saude/pt-br/composicao/sectics/plantas-medicinais-e-fitoterapicos/ppnpmf/arquivos/2014/renisus.pdf) · [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB59167) · [GBIF](https://www.gbif.org/species/8707933) |
| 94 | *Mentha × villosa* | hortelã-da-folha-miúda, hortelã-rasteira, hortelã | Lamiaceae | exotic, cultivated | 15 | 80.0% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [RENISUS](https://www.gov.br/saude/pt-br/composicao/sectics/plantas-medicinais-e-fitoterapicos/ppnpmf/arquivos/2014/renisus.pdf) · [GBIF](https://www.gbif.org/species/8004895) |
| 95 | *Mesosphaerum pectinatum* | sambacaitá, alfazema-brava, betônica | Lamiaceae | native | 15 | 76.7% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB59379) · [GBIF](https://www.gbif.org/species/3889976) |
| 96 | *Mesosphaerum suaveolens* | alfazema-de-caboclo, bamburral, alfavaca-brava | Lamiaceae | native | 15 | 93.3% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB59418) · [GBIF](https://www.gbif.org/species/3889017) |
| 97 | *Microdesmia rigida* | oiticica | Chrysobalanaceae | native, endemic to Brazil | 15 | 95.0% (20) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB605408) · [GBIF](https://www.gbif.org/species/10039120) |
| 98 | *Mikania glomerata* | guaco | Asteraceae | native | 11 | 63.6% (11) | [FFFB](https://bibliotecadigital.anvisa.gov.br/jspui/handle/anvisa/21045) · [RENISUS](https://www.gov.br/saude/pt-br/composicao/sectics/plantas-medicinais-e-fitoterapicos/ppnpmf/arquivos/2014/renisus.pdf) · [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB5378) · [GBIF](https://www.gbif.org/species/7337157) |
| 99 | *Mimosa caesalpiniifolia* | sabiá, unha-de-gato | Fabaceae | native, endemic to Brazil | 15 | 96.7% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB18776) · [GBIF](https://www.gbif.org/species/2970230) |
| 100 | *Mimosa tenuiflora* | jurema-preta, jurema | Fabaceae | native | 15 | 76.0% (100) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB18874) · [GBIF](https://www.gbif.org/species/2969531) |
| 101 | *Momordica charantia* | melão-de-são-caetano, melão-de-sabiá, erva-de-são-caetano | Cucurbitaceae | exotic, naturalized | 15 | 100.0% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [RENISUS](https://www.gov.br/saude/pt-br/composicao/sectics/plantas-medicinais-e-fitoterapicos/ppnpmf/arquivos/2014/renisus.pdf) · [Flora](https://floradobrasil.jbrj.gov.br/FB17098) · [GBIF](https://www.gbif.org/species/2874581) |
| 102 | *Moringa oleifera* | moringa, lírio-branco, acácia-branca | Moringaceae | exotic, cultivated | 15 | 96.7% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB598022) · [GBIF](https://www.gbif.org/species/3054181) |
| 103 | *Neoglaziovia variegata* | caroá, caruá, gravatá | Bromeliaceae | native, endemic to Brazil | 15 | 93.3% (30) | [art.](https://www.alice.cnptia.embrapa.br/handle/doc/1171858) · [art.](https://pesquisa.bvsalud.org/bvsvs/resource/pt/mdl-34425057) · [Flora](https://floradobrasil.jbrj.gov.br/FB16612) · [GBIF](https://www.gbif.org/species/2699414) |
| 104 | *Ocimum basilicum* | manjericão, alfavaca, manjericão-de-molho | Lamiaceae | exotic, cultivated | 15 | 90.0% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB117019) · [GBIF](https://www.gbif.org/species/2927096) |
| 105 | *Ocimum gratissimum* | alfavaca, alfavacão, alfavaca-de-cheiro | Lamiaceae | exotic, naturalized | 15 | 93.3% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [RENISUS](https://www.gov.br/saude/pt-br/composicao/sectics/plantas-medicinais-e-fitoterapicos/ppnpmf/arquivos/2014/renisus.pdf) · [Flora](https://floradobrasil.jbrj.gov.br/FB23332) · [GBIF](https://www.gbif.org/species/2927094) |
| 106 | *Operculina hamiltonii* | batata-de-purga, batatão | Convolvulaceae | native | 15 | 93.3% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB28445) · [GBIF](https://www.gbif.org/species/7323899) |
| 107 | *Operculina macrocarpa* | batata-de-purga, jalapa, batatão | Convolvulaceae | native | 15 | 88.9% (18) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB7108) · [GBIF](https://www.gbif.org/species/5548777) |
| 108 | *Opuntia ficus-indica* | palma, palma-gigante, figo-da-índia | Cactaceae | exotic, naturalized | 15 | 99.0% (100) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB1614) · [GBIF](https://www.gbif.org/species/5384064) |
| 109 | *Parkinsonia aculeata* | turco, cina-cina, espinho-de-jerusalém | Fabaceae | native | 15 | 100.0% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB83555) · [GBIF](https://www.gbif.org/species/5357217) |
| 110 | *Passiflora cincinnata* | maracujá-do-mato, maracujá-mochila | Passifloraceae | native | 15 | 90.0% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB12518) · [GBIF](https://www.gbif.org/species/2874200) |
| 111 | *Passiflora edulis* | maracujá, maracujazeiro | Passifloraceae | native | 15 | 96.7% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [RENISUS](https://www.gov.br/saude/pt-br/composicao/sectics/plantas-medicinais-e-fitoterapicos/ppnpmf/arquivos/2014/renisus.pdf) · [Flora](https://floradobrasil.jbrj.gov.br/FB12523) · [GBIF](https://www.gbif.org/species/2874190) |
| 112 | *Persea americana* | abacateiro, abacate | Lauraceae | exotic, cultivated | 15 | 93.3% (30) | [FFFB](https://bibliotecadigital.anvisa.gov.br/jspui/handle/anvisa/21045) · [RENISUS](https://www.gov.br/saude/pt-br/composicao/sectics/plantas-medicinais-e-fitoterapicos/ppnpmf/arquivos/2014/renisus.pdf) · [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB25622) · [GBIF](https://www.gbif.org/species/3034046) |
| 113 | *Petiveria alliacea* | tipi, guiné, erva-guiné | Phytolaccaceae | exotic, naturalized | 15 | 96.7% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB24174) · [GBIF](https://www.gbif.org/species/3084012) |
| 114 | *Petroselinum crispum* | salsa, salsinha, cheiro-verde | Apiaceae | exotic, cultivated | 15 | 100.0% (30) | [RENISUS](https://www.gov.br/saude/pt-br/composicao/sectics/plantas-medicinais-e-fitoterapicos/ppnpmf/arquivos/2014/renisus.pdf) · [art.](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3637085/) · [Flora](https://floradobrasil.jbrj.gov.br/FB597718) · [GBIF](https://www.gbif.org/species/7828157) |
| 115 | *Phyllanthus amarus* | quebra-pedra, erva-pombinha | Phyllanthaceae | native | 15 | 100.0% (30) | [RENISUS](https://www.gov.br/saude/pt-br/composicao/sectics/plantas-medicinais-e-fitoterapicos/ppnpmf/arquivos/2014/renisus.pdf) · [art.](https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/1177844/1/BDP-387-roberto.pdf) · [Flora](https://floradobrasil.jbrj.gov.br/FB632874) · [GBIF](https://www.gbif.org/species/5382589) |
| 116 | *Phyllanthus niruri* | quebra-pedra | Phyllanthaceae | native | 15 | 43.3% (30) | [FFFB](https://bibliotecadigital.anvisa.gov.br/jspui/handle/anvisa/21045) · [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB24168) · [GBIF](https://www.gbif.org/species/5381945) |
| 117 | *Pilosocereus pachycladus* | facheiro, facheiro-azul, mandacaru-de-facho | Cactaceae | native, endemic to Brazil | 15 | 70.0% (30) | [art.](https://scielo.br/j/rbfar/a/m4bzmgQgH6fZVmYNWHwMBrN/?lang=en) · [Flora](https://floradobrasil.jbrj.gov.br/FB1668) · [GBIF](https://www.gbif.org/species/7284328) |
| 118 | *Pimpinella anisum* | erva-doce, anis | Apiaceae | exotic, cultivated | 1 | – | [FFFB](https://bibliotecadigital.anvisa.gov.br/jspui/handle/anvisa/21045) · [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB599054) · [GBIF](https://www.gbif.org/species/8080300) |
| 119 | *Pityrocarpa moniliformis* | catanduva, angico-de-bezerro, quipé | Fabaceae | native, endemic to Brazil | 15 | 80.0% (30) | [art.](https://periodicos.uem.br/ojs/index.php/ActaSciBiolSci/article/view/75753) · [Flora](https://floradobrasil.jbrj.gov.br/FB116640) · [GBIF](https://www.gbif.org/species/3795607) |
| 120 | *Plantago major* | tanchagem, transagem, tansagem | Plantaginaceae | exotic, naturalized | 15 | 100.0% (30) | [FFFB](https://bibliotecadigital.anvisa.gov.br/jspui/handle/anvisa/21045) · [RENISUS](https://www.gov.br/saude/pt-br/composicao/sectics/plantas-medicinais-e-fitoterapicos/ppnpmf/arquivos/2014/renisus.pdf) · [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB128310) · [GBIF](https://www.gbif.org/species/3189767) |
| 121 | *Plumbago scandens* | louco, erva-do-diabo, caataia | Plumbaginaceae | native | 15 | 90.0% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB12940) · [GBIF](https://www.gbif.org/species/3082282) |
| 122 | *Portulaca oleracea* | beldroega, bredo | Portulacaceae | exotic, naturalized | 15 | 100.0% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB20624) · [GBIF](https://www.gbif.org/species/3084719) |
| 123 | *Prosopis juliflora* | algaroba, algarobeira | Fabaceae | exotic, naturalized | 15 | 86.7% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB18991) · [GBIF](https://www.gbif.org/species/5358460) |
| 124 | *Psidium guajava* | goiabeira, goiaba | Myrtaceae | exotic, naturalized | 15 | 100.0% (30) | [FFFB](https://bibliotecadigital.anvisa.gov.br/jspui/handle/anvisa/21045) · [RENISUS](https://www.gov.br/saude/pt-br/composicao/sectics/plantas-medicinais-e-fitoterapicos/ppnpmf/arquivos/2014/renisus.pdf) · [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB24034) · [GBIF](https://www.gbif.org/species/5420380) |
| 125 | *Punica granatum* | romã, romãzeira | Lythraceae | exotic, cultivated | 15 | 96.7% (30) | [FFFB](https://bibliotecadigital.anvisa.gov.br/jspui/handle/anvisa/21045) · [RENISUS](https://www.gov.br/saude/pt-br/composicao/sectics/plantas-medicinais-e-fitoterapicos/ppnpmf/arquivos/2014/renisus.pdf) · [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB594110) · [GBIF](https://www.gbif.org/species/5420901) |
| 126 | *Ricinus communis* | mamona, carrapateira, rícino | Euphorbiaceae | exotic, naturalized | 15 | 100.0% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB17659) · [GBIF](https://www.gbif.org/species/5380041) |
| 127 | *Ruta graveolens* | arruda | Rutaceae | exotic, cultivated | 15 | 100.0% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [RENISUS](https://www.gov.br/saude/pt-br/composicao/sectics/plantas-medicinais-e-fitoterapicos/ppnpmf/arquivos/2014/renisus.pdf) · [Flora](https://floradobrasil.jbrj.gov.br/FB991) · [GBIF](https://www.gbif.org/species/3190382) |
| 128 | *Salvia rosmarinus* | alecrim, alecrim-verdadeiro | Lamiaceae | exotic, cultivated | 15 | 100.0% (30) | [FFFB](https://bibliotecadigital.anvisa.gov.br/jspui/handle/anvisa/21045) · [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB633987) · [GBIF](https://www.gbif.org/species/10902460) |
| 129 | *Sarcomphalus joazeiro* | juazeiro, juá, joá | Rhamnaceae | native | 15 | 91.2% (91) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB622196) · [GBIF](https://www.gbif.org/species/8910944) |
| 130 | *Schinopsis brasiliensis* | baraúna, braúna | Anacardiaceae | native | 15 | 46.7% (15) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB4396) · [GBIF](https://www.gbif.org/species/7321861) |
| 131 | *Schinus terebinthifolia* | aroeira-vermelha, aroeira-da-praia, aroeira-mansa | Anacardiaceae | native | 15 | 99.0% (100) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [RENISUS](https://www.gov.br/saude/pt-br/composicao/sectics/plantas-medicinais-e-fitoterapicos/ppnpmf/arquivos/2014/renisus.pdf) · [Flora](https://floradobrasil.jbrj.gov.br/FB4401) · [GBIF](https://www.gbif.org/species/3660419) |
| 132 | *Scoparia dulcis* | vassourinha, vassoura-de-botão | Plantaginaceae | native | 15 | 100.0% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB12920) · [GBIF](https://www.gbif.org/species/3171787) |
| 133 | *Selaginella convoluta* | jericó, mão-fechada, mão-de-papagaio | Selaginellaceae | native | 15 | 100.0% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB92067) · [GBIF](https://www.gbif.org/species/7723170) |
| 134 | *Senna obtusifolia* | mata-pasto, fedegoso | Fabaceae | native | 15 | 93.3% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB23161) · [GBIF](https://www.gbif.org/species/2957408) |
| 135 | *Senna occidentalis* | fedegoso, mata-pasto, manjerioba | Fabaceae | native | 15 | 100.0% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB23162) · [GBIF](https://www.gbif.org/species/2957966) |
| 136 | *Senna spectabilis* | canafístula, cássia-do-nordeste | Fabaceae | native | 15 | 80.0% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB23172) · [GBIF](https://www.gbif.org/species/2957438) |
| 137 | *Sida cordifolia* | malva-branca, malva, malva-veludo | Malvaceae | native | 15 | 96.7% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB9212) · [GBIF](https://www.gbif.org/species/5406755) |
| 138 | *Sideroxylon obtusifolium* | quixabeira, quixaba, rompe-gibão | Sapotaceae | native | 15 | 73.0% (100) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB21028) · [GBIF](https://www.gbif.org/species/2887108) |
| 139 | *Solanum paniculatum* | jurubeba, jurubeba-roxa | Solanaceae | native | 15 | 100.0% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [RENISUS](https://www.gov.br/saude/pt-br/composicao/sectics/plantas-medicinais-e-fitoterapicos/ppnpmf/arquivos/2014/renisus.pdf) · [Flora](https://floradobrasil.jbrj.gov.br/FB14821) · [GBIF](https://www.gbif.org/species/2932547) |
| 140 | *Spondias mombin* | cajá, cajazeira, taperebá | Anacardiaceae | native | 15 | 90.0% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB4404) · [GBIF](https://www.gbif.org/species/8185571) |
| 141 | *Spondias purpurea* | siriguela, seriguela, ciriguela | Anacardiaceae | exotic, cultivated | 15 | 70.0% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB21762) · [GBIF](https://www.gbif.org/species/3190598) |
| 142 | *Spondias tuberosa* | umbuzeiro, umbu, imbuzeiro | Anacardiaceae | native, endemic to Brazil | 15 | 72.3% (65) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB4405) · [GBIF](https://www.gbif.org/species/8230360) |
| 143 | *Stachytarpheta cayennensis* | gervão, rinchão | Verbenaceae | native | 15 | 96.7% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB21466) · [GBIF](https://www.gbif.org/species/2925454) |
| 144 | *Stryphnodendron adstringens* | barbatimão, casca-da-virgindade | Fabaceae | native, endemic to Brazil | 15 | 96.7% (30) | [FFFB](https://bibliotecadigital.anvisa.gov.br/jspui/handle/anvisa/21045) · [RENISUS](https://www.gov.br/saude/pt-br/composicao/sectics/plantas-medicinais-e-fitoterapicos/ppnpmf/arquivos/2014/renisus.pdf) · [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB19133) · [GBIF](https://www.gbif.org/species/2951737) |
| 145 | *Syagrus coronata* | licuri, ouricuri | Arecaceae | native, endemic to Brazil | 15 | 93.1% (29) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB15736) · [GBIF](https://www.gbif.org/species/5293875) |
| 146 | *Syzygium cumini* | jambolão, azeitona-roxa, jamelão | Myrtaceae | exotic, naturalized | 15 | 76.7% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [RENISUS](https://www.gov.br/saude/pt-br/composicao/sectics/plantas-medicinais-e-fitoterapicos/ppnpmf/arquivos/2014/renisus.pdf) · [Flora](https://floradobrasil.jbrj.gov.br/FB86017) · [GBIF](https://www.gbif.org/species/3183840) |
| 147 | *Tabebuia aurea* | craibeira, caraibeira, ipê-amarelo | Bignoniaceae | native | 15 | 83.3% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB114257) · [GBIF](https://www.gbif.org/species/4091191) |
| 148 | *Tacinga inamoena* | quipá, palmatória, palmatória-miúda | Cactaceae | native, endemic to Brazil | 15 | 96.7% (30) | [art.](https://scielo.br/j/bjps/a/K5LsHZwSqgy6KGFKHQYCKKj/?lang=en) · [Flora](https://floradobrasil.jbrj.gov.br/FB1753) · [GBIF](https://www.gbif.org/species/7284042) |
| 149 | *Tagetes erecta* | cravo-de-defunto, cravo-africano | Asteraceae | exotic, naturalized | 15 | 100.0% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB22240) · [GBIF](https://www.gbif.org/species/3088488) |
| 150 | *Talisia esculenta* | pitombeira, pitomba | Sapindaceae | native | 15 | 90.0% (20) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB20984) · [GBIF](https://www.gbif.org/species/3788345) |
| 151 | *Tamarindus indica* | tamarindo, tamarindeiro | Fabaceae | exotic, cultivated | 15 | 93.3% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB23201) · [GBIF](https://www.gbif.org/species/2975768) |
| 152 | *Terminalia catappa* | castanhola, amendoeira, chapéu-de-sol | Combretaceae | exotic, naturalized | 15 | 90.0% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB22511) · [GBIF](https://www.gbif.org/species/3189394) |
| 153 | *Turnera subulata* | chanana, boa-noite, onze-horas | Turneraceae | native | 15 | 100.0% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB21354) · [GBIF](https://www.gbif.org/species/4161154) |
| 154 | *Varronia curassavica* | erva-baleeira, maria-milagrosa | Cordiaceae | native | 15 | 93.3% (30) | [FFFB](https://bibliotecadigital.anvisa.gov.br/jspui/handle/anvisa/21045) · [RENISUS](https://www.gov.br/saude/pt-br/composicao/sectics/plantas-medicinais-e-fitoterapicos/ppnpmf/arquivos/2014/renisus.pdf) · [Flora](https://floradobrasil.jbrj.gov.br/FB105435) · [GBIF](https://www.gbif.org/species/4060951) |
| 155 | *Varronia leucocephala* | moleque-duro, negro-duro | Cordiaceae | native, endemic to Brazil | 15 | 96.7% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB105425) · [GBIF](https://www.gbif.org/species/4060181) |
| 156 | *Waltheria indica* | malva, malva-branca, douradinha | Malvaceae | native | 15 | 96.7% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB136634) · [GBIF](https://www.gbif.org/species/5406665) |
| 157 | *Ximenia americana* | ameixa-do-mato, ameixa, ameixa-brava | Ximeniaceae | native | 15 | 93.3% (30) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB10971) · [GBIF](https://www.gbif.org/species/2889811) |
| 158 | *Xiquexique gounellei* | xique-xique | Cactaceae | native, endemic to Brazil | 15 | 95.0% (100) | [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB617411) · [GBIF](https://www.gbif.org/species/10965911) |
| 159 | *Zingiber officinale* | gengibre | Zingiberaceae | exotic, cultivated | 15 | 80.0% (30) | [FFFB](https://bibliotecadigital.anvisa.gov.br/jspui/handle/anvisa/21045) · [RENISUS](https://www.gov.br/saude/pt-br/composicao/sectics/plantas-medicinais-e-fitoterapicos/ppnpmf/arquivos/2014/renisus.pdf) · [Agra 2008](https://www.scielo.br/j/rbfar/a/fC7snvLkwzzFsMv3mfVRGNc/) · [Flora](https://floradobrasil.jbrj.gov.br/FB110731) · [GBIF](https://www.gbif.org/species/2757280) |

</details>

The texts are in Portuguese and are for traditional and educational use. They do not replace a physician, pharmacist or other health professional.

## Licenses and attribution

| Item | License |
|---|---|
| Code, model files (`plant-classifier-int8.onnx`, `plant-index.bin`) | [MIT](LICENSE) |
| BioCLIP 2 weights the model is derived from | MIT, Copyright (c) 2023-2026 Imageomics Institute and others ([full text](LICENSE-BIOCLIP2)) |
| Reference vectors in `plant-index.bin` | Computed from iNaturalist photos under CC0, CC BY, CC BY-SA, CC BY-NC and CC BY-NC-SA; authors listed in [`eval/data/reference_photos.csv`](eval/data/reference_photos.csv) |
| Vectors added in `plant-index-v1.0.1.bin` | 70 CC0, CC BY and CC BY-SA photos from iNaturalist and Wikimedia Commons; authors in [`eval/scale/index-v1.0.1/referencias_adicionadas.csv`](eval/scale/index-v1.0.1/referencias_adicionadas.csv) |
| Test photos | Not redistributed; IDs, licenses and authors in [`eval/scale/amostra_ids.csv`](eval/scale/amostra_ids.csv) (main evaluation) and [`eval/data/test_photos.csv`](eval/data/test_photos.csv) (development set) |
| Species texts | Written for this project from the sources linked in each entry |

Most reference and test photos are CC BY-NC. The index contains only numeric vectors derived from them, not the images. If you plan commercial use, review whether that is compatible with your use case. Three reference photos (*Genipa americana*, *Pityrocarpa moniliformis*, *Spondias mombin*, one each) turned out to be "all rights reserved" on their first image and were removed in [index v1.0.1](#index-v101). The 70 references added in v1.0.1 are CC0, CC BY or CC BY-SA, with authors in [`eval/scale/index-v1.0.1/referencias_adicionadas.csv`](eval/scale/index-v1.0.1/referencias_adicionadas.csv).

## Citation

```bibtex
@software{reis_2026_saberia_plant_id,
  author  = {Reis, Andesson and Souza, Leandro Oliveira de},
  title   = {{SaberIA Plant ID}: offline identification of medicinal plants of the Caatinga},
  year    = {2026},
  version = {1.0.0},
  url     = {https://github.com/Andessonreis/saberia-plant-id},
  note    = {Instituto Federal da Bahia (IFBA), Campus Irecê}
}
```

Please also cite BioCLIP 2:

```bibtex
@inproceedings{gu2025bioclip2,
  author    = {Gu, Jianyang and Stevens, Sam and Campolongo, Elizabeth and Thompson, Matthew and Zhang, Net and Wu, Jiaman and Kopanev, Andrei and Mai, Zheda and White, Alexander and Balhoff, James and Dahdul, Wasila and Rubenstein, Daniel and Lapp, Hilmar and Berger-Wolf, Tanya and Chao, Wei-Lun and Su, Yu},
  title     = {{BioCLIP 2}: Emergent Properties from Scaling Hierarchical Contrastive Learning},
  booktitle = {Advances in Neural Information Processing Systems},
  volume    = {38},
  pages     = {102778--102811},
  year      = {2025}
}

@software{Gu_BioCLIP_2_model,
  author    = {Gu, Jianyang and Stevens, Samuel and Campolongo, Elizabeth G. and Thompson, Matthew J. and Zhang, Net and Wu, Jiaman and Kopanev, Andrei and Mai, Zheda and White, Alexander E. and Balhoff, James and Dahdul, Wasila M. and Rubenstein, Daniel and Lapp, Hilmar and Berger-Wolf, Tanya and Chao, Wei-Lun and Su, Yu},
  title     = {{BioCLIP 2}},
  version   = {1.0.0},
  doi       = {10.57967/hf/5765},
  publisher = {Hugging Face},
  year      = {2025}
}
```

## Acknowledgements and contact

- **Author:** Andesson Reis, Instituto Federal da Bahia (IFBA), Campus Irecê. andesson.reis@ifba.edu.br · [GitHub](https://github.com/Andessonreis) · [Hugging Face](https://huggingface.co/andessonIF)
- **Advisor:** Dr. Leandro Oliveira de Souza (IFBA)
- Undergraduate research project (PIBITI/IFBA 2025-2026), presented at the XXIII SICTI / VII CPPGI.
- Thanks to the [Imageomics Institute](https://imageomics.osu.edu) for releasing BioCLIP 2 under an open license, to the iNaturalist observers whose photos made the reference index and the test set possible, and to the community members who tested the app in the workshops.
