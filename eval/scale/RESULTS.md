# Scale evaluation of the offline plant classifier

[Português (Brasil)](RESULTS.pt-BR.md) · [Main README](../../README.md)

Collection and measurement: 2026-10-31. The numbers below are the ones that came out, with no sample selection and no rounding up. The complete data, including per-species results and per-photo cloud comparison, is in [`resultados.json`](resultados.json); per-species tables are in [`tabelas.md`](tabelas.md) (Portuguese); the scripts to redo everything are in [`scripts/`](scripts/).

## In one sentence

On **5,791 iNaturalist photos** of **157 of the 159 species** in the base, none of them used as a reference in the index, the app's offline classifier got the species right on the first option for **88.8%** of photos (95% CI: 88.0 to 89.6%) and within the top 3 for **96.2%** (95.7 to 96.7%). At the app's confidence threshold (0.75) it gives an answer for **76.1%** of photos and, when it does, it is right **97.2%** of the time (96.7 to 97.7%). On the **22 key species** (n = 1,986) the first option is right **84.3%** of the time (82.7 to 85.9%). On **300 plants outside the base**, the app wrongly accepted a species of the base for **12.3%** (9.1 to 16.5%). On the **5,155 photos** uploaded to iNaturalist after the BioCLIP 2 pretraining cutoff (August 2024), the first option is right **90.6%** of the time (89.8 to 91.4%): there is no sign that pretraining inflates the result (see "BioCLIP 2 pretraining contamination").

## Where the photos come from

- **Source:** iNaturalist (public API), research-grade observations only (identification confirmed by the community), "medium" size (500 px on the long side).
- **Test (species of the base):** for each species, 1 photo per observation (the main one) and **at most 1 observation per observer**, so the same plant or the same photographer is not counted many times. Target of 100 photos for the 22 key species and 30 for the others. Where there were not enough eligible photos, the real n was kept: catingueira has only 7, umburana-de-cheiro 53, umbu 65, aroeira 77, juazeiro 91, umburana-de-cambão 95. *Citrus aurantium* and *Pimpinella anisum* had no eligible photo. 146 species have n ≥ 20 and 11 have n < 20.
- **Period:** observations from 2025 onward came first (5,012 photos). Older ones (779) only entered where needed.
- **Licenses:** CC0/CC BY/CC BY-SA were preferred, but most iNaturalist photos are CC BY-NC. Final count: CC BY-NC 3,571, CC BY 1,162, CC0 311, CC BY-SA 176, CC BY-NC-SA 76, CC BY-NC-ND 21 and 474 without an open license. The photos are used only for measurement. They are not in the repository and are not redistributed. The list of observations and photos used, with species, license and credit, is in [`amostra_ids.csv`](amostra_ids.csv), and each photo can be seen at `inaturalist.org/photos/<id>`.
- **Outside the base:** 300 observations of plants from Brazil (2025+), identified to species, drawn with a fixed seed (20251105), 1 per species and 1 per observer, excluding the species of the base and their synonyms.

## How leakage was prevented (test photo too similar to a reference)

1. **By ID:** every observation behind the 2,320 reference photos of the published index was excluded from the test, and so were the photos used earlier to calibrate the 0.75 threshold (the development set). 2,647 observations in total.
2. **By content:** each test photo was compared with the 2,320 references and with the other test photos by perceptual hash (64-bit dHash, up to 6 bits apart) and by embedding similarity (cosine ≥ 0.99). Five photos were removed, all repeated within the test set itself. No test photo is a copy of a reference. The cosine cut started at 0.95, but visual inspection showed that pairs between 0.95 and 0.98 are different photos of the same species, not duplicates. So only the real-copy criterion was kept, to avoid discarding precisely the typical photos.
3. **Observer sensitivity:** when the observer also has a photo among the references (1,250 photos), the first option is right 87.0% of the time. For a new observer (4,541 photos), 89.3%. There is no sign that "knowing the photographer" inflates the result.

## BioCLIP 2 pretraining contamination

The app's base model (BioCLIP 2) was pretrained on TreeOfLife-200M, which includes iNaturalist photos. So some test photos may have gone through pretraining even though they are not in the index. The test photos **were not used as references in the index**, but it cannot be said that the model never saw them.

**Training-data cutoff**, according to the official dataset card (huggingface.co/datasets/imageomics/TreeOfLife-200M, revision a8f38b4, the one used for BioCLIP 2 and in Gu et al., NeurIPS 2025, arXiv 2505.23883):

- **GBIF**, through which iNaturalist photos enter: occurrence snapshot of **2024-05-01** (DOI 10.15468/dl.bfv433).
- **EOL**, which also mirrors iNaturalist photos: accessed in **August 2024**.

The later cutoff, **2024-08-31**, was used. For each test photo, the creation (upload) date of the observation was downloaded from the iNaturalist API. A photo cannot have been uploaded before its observation existed, so an observation created from 2024-09-01 was certainly not in pretraining. Since the cutoff is before 2025, there is no "January 2025 to cutoff" band.

| Band (observation creation date) | n | Top-1 (95% CI) | Top-3 (95% CI) | Key species: n | Key species: top-1 (95% CI) | Key species: top-3 (95% CI) |
|---|---:|---|---|---:|---|---|
| (a) from 2024-09-01: certainly outside pretraining | 5,155 | 90.6% (89.8–91.4%) | 96.9% (96.4–97.3%) | 1,559 | 88.1% (86.4–89.6%) | 95.5% (94.3–96.4%) |
| (b) 2024-05-01 to 2024-08-31: could only have entered through EOL | 56 | 71.4% (58.5–81.6%) | 92.9% (83.0–97.2%) | 39 | 61.5% (45.9–75.1%) | 89.7% (76.4–95.9%) |
| (c) before 2024-05-01: may be in pretraining | 580 | 74.3% (70.6–77.7%) | 90.9% (88.2–93.0%) | 388 | 71.7% (67.0–75.9%) | 89.7% (86.3–92.3%) |
| Created in 2025 or later | 5,060 | 90.8% (89.9–91.5%) | 96.9% (96.4–97.3%) | 1,486 | 88.3% (86.6–89.8%) | 95.4% (94.2–96.4%) |
| Created before 2025 | 731 | 75.4% (72.1–78.4%) | 91.5% (89.3–93.3%) | 500 | 72.6% (68.5–76.3%) | 90.6% (87.7–92.9%) |

**Reading:** no sign of inflation from contamination. Photos certainly outside pretraining score **higher**, not lower. The raw gap comes almost entirely from species: older photos only entered for species with few recent photos, which are precisely the hardest native trees (see "Period" above). Within the same 39 species that have photos from both periods, new photos (a), standardized to the same species mix, are right on the first option **77.8%** of the time and older ones (b + c) **74.1%** (n = 946 and 636). The 88.8% can be quoted. The subset with no chance of contamination gives **90.6%** (89.8 to 91.4%, n = 5,155).

## Mini test: lower-quality photos (separate label, small n)

**Do not add to the main test.** These are 99 observations of the key species graded "casual" or "needs ID" on iNaturalist, i.e. below research grade. Rules: created from 2024-09-01 (outside pretraining), community identification at species level with at least 2 different identifiers agreeing, no observation from the main test, the references or the calibration, 1 per observer and up to 7 per species. IDs are in [`amostra_ids.csv`](amostra_ids.csv) (set `mini_teste_qualidade_inferior`) and details in [`resultados.json`](resultados.json) (`mini_teste_fotos_qualidade_inferior`).

| Subset | n | Top-1 (95% CI) | Top-3 (95% CI) | Accepted at threshold | Correct among accepted |
|---|---:|---|---|---|---|
| Mini test, all | 99 | 88.9% (81.2–93.7%) | 96.0% (90.1–98.4%) | 70.7% | 97.1% (68/70) |
| "Casual" only | 93 | 88.2% (80.1–93.3%) | 95.7% (89.5–98.3%) | 72.0% | 97.0% |
| "Needs ID" only | 6 | 6/6 (61.0–100%) | 6/6 | 3/6 | 3/3 |

For comparison, the main test (research grade) on these same species, each weighted equally, gives 87.8% on the first option. **No drop appeared, but the test measures little.** 88 of the 99 photos are "casual" only because the plant is cultivated (yard, pot, square), not because the photo is poor. And exactly the hard native trees are missing: pinhão-bravo, jurema-preta and quixabeira had no eligible photo, and aroeira and umburana-de-cambão have 1 photo each. Errors were in mulungu (4/7), umbu (0/2), umburana-de-cambão (0/1), umburana-de-cheiro (2/3), angico (3/4), capim-santo, ipê-roxo and pau-ferro (6/7 each). This mini test **does not replace** a test with field photos taken by lay users.


## How the measurement mirrors the app

- Same model (`plant-classifier-int8.onnx`, sha256 `6452d330…`) and same index (`plant-index.bin`, sha256 `b1c553fe…`) as published and downloaded by the app.
- Same preprocessing as `PlantClassifier.kt`: EXIF orientation, power-of-two downsampling at decode time, bilinear resize without extra smoothing (like `Bitmap.createScaledBitmap`), 224×224 center crop and normalization.
- Same scoring as the app: similarity to the scientific name plus the mean of the 3 most similar reference photos. Confidence is the probability of the best species times the probability that the plant is in the base. The answer is shown only if confidence is ≥ 0.75.

## How the confidence intervals were computed

Every rate has a **95% Wilson interval**, which behaves well with small n and with rates close to 0% or 100%. For the "per-species mean", where each species weighs the same, the CI comes from a **stratified bootstrap**: 2,000 resamples of the photos within each species, seed 20251105. Photos from the same observer never repeat within a species, so the observations of each species are independent with respect to the photographer.

## Tables

### Overall (app threshold = 0.75)

| Subset | Photos | Top-1 (95% CI) | Top-3 (95% CI) | Genus right at top-1 | Accepted at threshold | Correct among accepted | Wrong among accepted |
|---|---:|---|---|---|---|---|---|
| All species | 5,791 | 88.8% (88.0–89.6%) | 96.2% (95.7–96.7%) | 91.1% (90.3–91.8%) | 76.1% (75.0–77.1%) | 97.2% (96.7–97.7%) | 2.8% (2.3–3.3%) |
| Key species | 1,986 | 84.3% (82.7–85.9%) | 94.2% (93.1–95.2%) | 85.5% (83.9–87.0%) | 67.9% (65.8–69.9%) | 96.1% (94.9–97.0%) | 3.9% (3.0–5.1%) |
| Other species | 3,805 | 91.1% (90.2–92.0%) | 97.3% (96.7–97.7%) | 94.0% (93.2–94.7%) | 80.3% (79.0–81.6%) | 97.8% (97.2–98.2%) | 2.2% (1.8–2.8%) |

Per-species mean (each species weighs the same, 157 species): top-1 88.3% (bootstrap 95% CI 87.5–89.2%); top-3 96.0% (95.4–96.7%). Key species: top-1 82.2% (80.0–84.4%).

### Plants outside the base

| Subset | Accepted as a species of the base (false positive) |
|---|---|
| All (300 photos, 300 species) | 37/300 = 12.3% (9.1–16.5%) |
| Species is in the index's list of "other plant" names | 0/22 = 0.0% (0.0–14.9%) |
| Genus has a species in the base (e.g. another *Erythrina*, another *Melocactus*) | 13/56 = 23.2% (14.1–35.8%) |
| Genus has no species in the base | 24/244 = 9.8% (6.7–14.2%) |
| Species is not in that list | 37/278 = 13.3% (9.8–17.8%) |

### Sensitivity: same observer among the reference photos

| Subset | n | Top-1 (95% CI) |
|---|---:|---|
| Observer also has a photo among the index references | 1,250 | 87.0% (85.0–88.7%) |
| New observer | 4,541 | 89.3% (88.4–90.2%) |

### Cloud AI comparison (same prompt and endpoint as the app)

Subsample drawn with seed 20251105: 399 photos of species in the base + 50 from outside. The free quota of the API key (20 requests per day per model) stopped the calls; only the photos each model answered are counted, compared with the offline classifier ON THE SAME photos.

| System | Photos answered | Right species (95% CI) | Right genus (95% CI) | SaberIA offline on the same photos: top-1 (95% CI) | Cloud median latency |
|---|---:|---|---|---|---|
| gemini-3.5-flash | 11 | 6/11 = 54.5% (28.0–78.7%) | 8/11 = 72.7% (43.4–90.2%) | 11/11 = 100.0% (74.1–100.0%) | 4.2 s |
| gemini-2.5-flash | 20 | 7/20 = 35.0% (18.1–56.7%) | 12/20 = 60.0% (38.7–78.1%) | 19/20 = 95.0% (76.4–99.1%) | 3.5 s |

SaberIA offline on the whole subsample (399 photos): top-1 87.2% (83.6–90.1%), top-3 96.7% (94.5–98.1%); accepted at threshold 71.9% (67.3–76.1%), correct among accepted 97.2% (94.6–98.6%); outside the base accepted 10/50 = 20.0% (11.2–33.0%).

### Per species

The full per-species table (n, top-1 and top-3 with CI, accepted, correct among accepted, most common confusion) is in [`tabelas.md`](tabelas.md#por-espécie) and in the "Por espécie" section of [`RESULTS.pt-BR.md`](RESULTS.pt-BR.md). The 22 key species are also in the [main README](../../README.md#key-species).

## Index v1.0.1 (reinforcing aroeira, mulungu and umburana-de-cambão)

**The headline result of this document is still that of the v1.0.0 index: 88.8% on the first option, with no adjustment.** v1.0.1 is a separate index file (`plant-index-v1.0.1.bin`, sha256 `d8c97ff0419fcafb04201bf22ef1196c66de983e6210a0e1be89b2287cc9a5d2`) with the same format, labels, texts, threshold and model. Details in [`index-v1.0.1/README.md`](index-v1.0.1/README.md) (Portuguese).

What changed: the 3 "all rights reserved" references (*Genipa americana*, *Pityrocarpa moniliformis* and *Spondias mombin*) were removed. 70 CC0/CC BY/CC BY-SA references were added: 18 extra photos from observations already in the index and 52 field photos from Wikimedia Commons, checked by category and description. Review dropped 3 photos: one of *Schinus molle*, one of *Erythrina mulungu* and one that could not be verified.

**Methodological caveat:** the extra references were chosen after seeing where v1.0.0 failed **on the test**. So gains measured on that same test are optimistic.

| On the same 5,791 test photos (optimistic) | v1.0.0 | v1.0.1 |
|---|---|---|
| Top-1 overall | 88.8% (88.0–89.6) | 89.2% (88.3–90.0) |
| Top-1 key species | 84.3% (82.7–85.9) | 85.8% (84.1–87.2) |
| Top-1 other species | 91.1% (90.2–92.0) | 91.0% (90.0–91.8) |
| Aroeira-do-sertão (n = 77) | 55.8% | 76.6% |
| Mulungu (n = 100) | 59.0% | 73.0% |
| Umburana-de-cambão (n = 95) | 69.5% | 70.5% |
| Outside the base: false positive | 12.3% (37/300) | 12.3% (37/300) |

Photo by photo, 32 wrong became right and 11 right became wrong (McNemar p = 0.0019). Seven species lost 1 or 2 photos. The largest loss was *Erythrina mulungu*, from 24 to 22 of 30.

**New test, without that bias:** 117 observations of the 3 species that had not been used for anything (test, reference or calibration), 1 per observer. On them, the first option goes from **51.3% (42.3–60.2) to 73.5% (64.9–80.7)**, with 26 wrong becoming right and none right becoming wrong (McNemar p < 0.0001). Per species: aroeira from 6/20 to 17/20, mulungu from 34/68 to 48/68 and umburana-de-cambão from 20/29 to 21/29. Among the 47 observers with no photo in the main test, accuracy goes from 51.1% to 76.6%. This test only measures the 3 reinforced species.

## Other systems

- **Cloud AI (Gemini), same endpoint, prompt and parameters as the app:** the API key is on the free plan, which allows only 20 requests per day per model. So the planned 400-photo comparison did not fit. `gemini-3.5-flash`, the app's model, answered 11 photos of the drawn subsample and got the species right for 6 (54.5%; 95% CI 28.0 to 78.7%). `gemini-2.5-flash` answered 20 and got 7 right (35.0%; 18.1 to 56.7%). On the same photos, the offline classifier got 11/11 and 19/20. With n this small the intervals are wide. What can be said is that the difference points the same way in both samples. A precise cloud percentage cannot be stated. To reach n = 400, a key with billing is enough: `nuvem.py rodar` resumes where it stopped.
- **OpenAI (GPT-4o):** the available key is valid but has no credit ("insufficient_quota" error). It could not be measured.
- **Local Qwen3-VL-2B (earlier measurement, different sample):** got 6 of 64 photos right (9.4%; 95% CI 4.4 to 19.0%), with the app's prompt, on 64 recent iNaturalist photos of 8 key species. That sample is **not the same** as this test, and the number should not be compared side by side as if it were.

## On the device (Redmi 12, MediaTek Helio G88, 8 GB)

Source: the app's own log on the device (`files/plant-id.log`), with 16 real identifications made on 2026-10-31 using 4 threads.

- Model time per photo: median **3.3 s** (min 3.0 s, max 4.8 s).
- Photo decoding and preprocessing: median 55 ms.
- First model load, once per session: median 8.6 s (7.4 to 11.6 s; n = 6).
- Size: 308 MB model (int8) and 5.5 MB index. Downloaded once; after that everything works without internet.

## Limitations (read before quoting the numbers)

- **iNaturalist photos are easier than field photos.** They are usually framed by someone who already knows the plant, with flowers or fruit visible and good light. A hurried photo by a lay user, of a loose leaf or a leafless trunk in the dry season, tends to score lower. This number is a realistic ceiling, not a field guarantee.
- **Species bias:** common and cultivated species (babosa, capim-santo, coroa-de-frade, palma, aroeira-vermelha) reach 99 to 100%. Native Caatinga trees, which look very much alike when leafless, are well below. The weakest with n ≥ 50 are aroeira-do-sertão (55.8%), mulungu (59.0%), umburana-de-cheiro (60.4%), angico (65.0%) and umburana-de-cambão (69.5%). Among those with small n, confusions happen within the genus: *Lippia grata* (0/4), *Hymenaea martiana* (1/11), *Croton grewioides* (1/5) and *Phyllanthus niruri*, which becomes *P. amarus*.
- **Mandacaru:** the first option is right 90% of the time, but only 23 of 100 photos pass the threshold. Confidence is split with similar columnar cacti, and the most common confusion is facheiro (*Pilosocereus pachycladus*).
- **Plants outside the base:** the false positive rate rises to 23.2% (14.1 to 35.8%) when the plant belongs to a genus that has a species in the base, e.g. another *Erythrina*, *Melocactus*, *Sarcomphalus* or *Solanum*. When the genus is not in the base, it is 9.8% (6.7 to 14.2%). The app warns that the identification must be confirmed, and that warning is still needed.
- **Per-species sample size:** with 30 photos, the CI of a species at 90% goes from about 74% to 97%. Small differences between species are not significant.
- **Cloud comparison:** limited by the free quota (n = 11 and n = 20); it cannot pin down a cloud percentage.
- **iNaturalist labels:** research grade requires 2/3 agreement among identifiers, but misidentifications still happen. That tends to pull the measured accuracy down, not up.
- **Pretraining:** the test photos were not used as references in the index, but BioCLIP 2 was pretrained on iNaturalist photos up to 2024. The 636 test photos created before 2024-09-01 may have gone through pretraining. The subset without that possibility (n = 5,155) does not score lower.

## Reproducing

| File | Content |
|---|---|
| [`scripts/fetch_test.py`](scripts/fetch_test.py) | Downloads the test set (species of the base) from iNaturalist, with the sampling rules above |
| [`scripts/fetch_ood.py`](scripts/fetch_ood.py) | Downloads the out-of-base sample (300 species, fixed seed) |
| [`scripts/avaliar.py`](scripts/avaliar.py) | `embed`: computes the photo vectors with the app's preprocessing; `metrics`: app scoring, Wilson CIs, bootstrap, near-duplicate removal, observer sensitivity |
| [`scripts/nuvem.py`](scripts/nuvem.py) | Draws the cloud subsample, calls the cloud model (key read from a file given on the command line, sent only in the `Authorization` header, never printed or stored) and scores the answers |
| [`scripts/relatorio.py`](scripts/relatorio.py) | Merges everything into `resultados.json` and writes `tabelas.md` |
| [`scripts/datas_inat.py`](scripts/datas_inat.py), [`scripts/contaminacao.py`](scripts/contaminacao.py) | Observation creation dates and the pretraining-contamination analysis |
| [`scripts/campo_inferior.py`](scripts/campo_inferior.py) | Mini test with "casual"/"needs ID" photos |
| [`scripts/fetch_refs_novas.py`](scripts/fetch_refs_novas.py), [`scripts/fetch_commons.py`](scripts/fetch_commons.py), [`scripts/melhorar_refs.py`](scripts/melhorar_refs.py) | Candidate references (iNaturalist, Wikimedia Commons) and the v1.0.1 index build |
| [`scripts/comparar_indices.py`](scripts/comparar_indices.py), [`scripts/teste_novo_alvo.py`](scripts/teste_novo_alvo.py) | Paired comparison of indexes (McNemar) and the new unbiased test for the 3 species |

Requirements: `pip install numpy onnxruntime opencv-python requests`. The model and index are the [v1.0.0 release](https://github.com/Andessonreis/saberia-plant-id/releases/tag/v1.0.0) files; the species base is [`data/caatinga_species.json`](../../data/caatinga_species.json). The exclusion list given to `fetch_test.py` had 2,647 observation IDs: those behind the index's reference photos ([`../data/reference_photos.csv`](../data/reference_photos.csv)) and those used earlier during development, including the development set ([`../data/test_photos.csv`](../data/test_photos.csv)). iNaturalist observations change over time (photos removed, identifications revised), so a fresh download may not return exactly the same set; [`amostra_ids.csv`](amostra_ids.csv) pins the exact photos used.
