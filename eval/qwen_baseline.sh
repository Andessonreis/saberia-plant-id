#!/bin/bash
# Baseline: a general-purpose vision-language model (Qwen3-VL-2B, Q4_K_M GGUF) run locally with
# llama.cpp, using the identification prompt of the earlier version of the app, over the first
# 8 test photos of 8 species (64 photos). Prints "species|file|answer" per photo.
#
# usage: LLAMA_MTMD_CLI=/path/to/llama-mtmd-cli QWEN_DIR=/path/to/gguf ./qwen_baseline.sh <workdir> > qwen_results.txt
set -euo pipefail
S=$1
CLI=${LLAMA_MTMD_CLI:-llama-mtmd-cli}
Q=${QWEN_DIR:?set QWEN_DIR to the folder with the Qwen3-VL-2B GGUF files}
P="GPT, sua tarefa é identificar plantas com precisão. Analise qualquer imagem de uma planta ou folha que eu fornecer e detecte. Responda estritamente com o nome cientifico da planta identificada, e nada mais, sem explicações, sem texto adicional. Se a condição for irreconhecível, responda com 'Não sei'. Se a imagem não estiver relacionada a plantas, diga 'Por favor, escolha outra imagem'."
for sp in Sarcomphalus_joazeiro Cereus_jamacaru Spondias_tuberosa Myracrodruon_urundeuva Aloe_vera Sideroxylon_obtusifolium Mimosa_tenuiflora Commiphora_leptophloeos; do
  for f in $(ls "$S"/photos_recent/$sp/*.jpg | head -8); do
    a=$("$CLI" -m "$Q"/Qwen3VL-2B-Instruct-Q4_K_M.gguf --mmproj "$Q"/mmproj-Qwen3VL-2B-Instruct-Q8_0.gguf \
      --image "$f" --image-max-tokens 128 -n 32 --temp 0 -t 8 -c 2048 \
      -sys "Você deve fornecer respostas curtas e concisas" -p "$P" 2>/dev/null | grep -v "^[[:space:]]*$" | tail -1)
    echo "$sp|$(basename "$f")|$a"
  done
done
