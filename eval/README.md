# Evaluation and index build

Scripts used to build `plant-index.bin` and to produce the numbers in the main README. All of them take a working directory `W` as the first argument and expect this layout:

```text
W/
  db/caatinga_species.json   copy of ../data/caatinga_species.json
  work/labels.json           copy of data/labels.json (or regenerate with build_labels.py)
  models/                    ONNX files written by export_onnx.py
  refs/<species_id>/*.jpg    reference photos (fetch_refs.py)
  photos_recent/<Species_name>/*.jpg   test photos, species of the base (+ Ficus benjamina, treated as out-of-base)
  photos_ood/<Species_name>/*.jpg      test photos, species outside the base
```

## Requirements

```bash
pip install torch open_clip_torch onnx onnxruntime pillow numpy requests
```

## Steps

```bash
W=/path/to/workdir
mkdir -p $W/db $W/work $W/models
cp ../data/caatinga_species.json $W/db/
cp data/labels.json $W/work/

# 1. Reference photos: up to 15 per species, research grade, observed up to 2024-12-31, Brazil first
python fetch_refs.py $W 15

# 2. Test photos: observed from 2025-01-01, 8 per species
D1=2025-01-01 python fetch_photos.py $W/photos_recent 8 "Aloe vera,Amburana cearensis,Anadenanthera colubrina,Cenostigma pyramidale,Cereus jamacaru,Coleus barbatus,Commiphora leptophloeos,Cymbopogon citratus,Erythrina velutina,Handroanthus impetiginosus,Hymenaea courbaril,Jatropha mollissima,Libidibia ferrea,Lippia alba,Melocactus zehntneri,Mentha spicata,Mimosa tenuiflora,Myracrodruon urundeuva,Opuntia ficus-indica,Sarcomphalus joazeiro,Schinopsis brasiliensis,Sideroxylon obtusifolium,Spondias tuberosa,Ximenia americana,Xiquexique gounellei,Ficus benjamina"
D1=2025-01-01 python fetch_photos.py $W/photos_ood 6 "Azadirachta indica,Bougainvillea glabra,Catharanthus roseus,Croton urucurana,Delonix regia,Dieffenbachia seguine,Ixora coccinea,Leucaena leucocephala,Nerium oleander,Pereskia aculeata,Senna siamea"

# 3. Export BioCLIP 2's image encoder to ONNX and quantize the MatMuls to int8
python export_onnx.py $W imageomics/bioclip-2          # -> models/bioclip-2_visual_int8.onnx

# 4. Text vectors (PyTorch), then image vectors with the int8 ONNX model and bilinear resize
python embed.py $W imageomics/bioclip-2 photos_recent  # -> work/emb_bioclip-2_photos_recent.npz (holds the text vectors)
python embed_onnx.py $W bioclip-2 bioclip-2_visual_int8.onnx refs
python embed_onnx.py $W bioclip-2 bioclip-2_visual_int8.onnx photos_recent,photos_ood

# 5. Metrics: top-1/top-3 and the confidence-threshold table; per-species table with a 4th argument
python evaluate.py $W bioclip-2bl-int8 1.0 0.75

# 6. Write plant-index.bin, copy the model and print the manifest (size + SHA-256)
mkdir -p $W/release
python build_index.py $W bioclip-2bl-int8 bioclip-2_visual_int8.onnx $W/release 1.0 0.75
```

`qwen_baseline.sh` runs the generative baseline (Qwen3-VL-2B through llama.cpp) on the first 8 test photos of 8 species. It needs `llama-mtmd-cli` and the GGUF files; see the header of the script.

## Data

| File | Content |
|---|---|
| `data/test_photos.csv` | The 268 test photos (194 in the base, 74 out of the base): iNaturalist observation, license, author |
| `data/reference_photos.csv` | The 2,320 reference photos behind the vectors in `plant-index.bin`, in index order |
| `data/labels.json` | The 1,212 labels (159 species of the base + 1,053 other plants) with GBIF taxonomy |
| `data/qwen_results.txt` | Raw answers of the Qwen3-VL-2B baseline |

The photos themselves are not in this repository. Most are CC BY-NC, and iNaturalist observations can change (photos get removed, identifications get revised), so a fresh download may not give exactly the same set or the same numbers.

## Notes

- `fetch_photos.py` and `fetch_refs.py` take the first photo of each observation. The license filter of the iNaturalist API applies to the observation, so three reference photos ended up being "all rights reserved"; they are flagged in `reference_photos.csv` (empty `license`) and will be dropped in the next index.
- `build_labels.py` needs the PlantNet-300K `species_id_2_name` JSON in `W/models/` and queries the GBIF API. The shipped `data/labels.json` makes this step optional.
- Image embeddings from ONNX Runtime's int8 CPU kernels vary slightly between runs (cosine 0.994 to 1.0), which can move top-1 by about one percentage point.
- These scripts were run during development. In this release pass only `evaluate.py` and `../examples/predict.py` were re-run, against the stored embeddings and the released files.
