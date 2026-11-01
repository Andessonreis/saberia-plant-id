# Avaliação em escala do reconhecimento offline de plantas (SaberIA)

[English](RESULTS.md) · [README principal](../../README.pt-BR.md)

Coleta e medição: 31/10/2026. Os números abaixo são os que saíram, sem seleção de amostra e sem arredondar para cima. Os dados completos (inclusive por espécie e por foto da comparação com a nuvem) estão em `resultados.json`; os scripts para refazer tudo estão em `scripts/`.

## Resultado em uma frase

Em **5.791 fotos** do iNaturalist de **157 das 159 espécies** da base, nenhuma delas usada para montar o índice, o classificador offline do app acertou a espécie na 1ª opção em **88,8 %** das fotos (IC 95 %: 88,0 a 89,6 %) e entre as 3 primeiras em **96,2 %** (95,7 a 96,7 %). No limiar de confiança do app (0,75), ele mostra resposta em **76,1 %** das fotos e, quando mostra, acerta **97,2 %** (96,7 a 97,7 %). Nas **22 espécies-chave** da Caatinga (n = 1.986) a 1ª opção acerta **84,3 %** (82,7 a 85,9 %). Em **300 plantas fora da base**, o app aceitou erradamente uma espécie da base em **12,3 %** dos casos (9,1 a 16,5 %). Nas **5.155 fotos** enviadas ao iNaturalist depois da data de corte do pré-treino do BioCLIP-2 (agosto de 2024), a 1ª opção acerta **90,6 %** (89,8 a 91,4 %): não há sinal de que o pré-treino infle o resultado (seção "Contaminação do pré-treino").

## De onde vêm as fotos

- **Fonte:** iNaturalist (API pública), só observações com grau "pesquisa" (identificação confirmada pela comunidade), no tamanho "medium" (lado maior de 500 px).
- **Teste (espécies da base):** para cada espécie, 1 foto por observação (a principal) e **no máximo 1 observação por observador**, para não contar o mesmo pé de planta ou o mesmo fotógrafo várias vezes. Alvo de 100 fotos para 22 espécies-chave e 30 para as outras. Quando não havia fotos elegíveis suficientes, ficou o n real: catingueira só tem 7, umburana-de-cheiro 53, umbu 65, aroeira 77, juazeiro 91, umburana-de-cambão 95. *Citrus aurantium* e *Pimpinella anisum* ficaram sem nenhuma foto elegível. 146 espécies têm n ≥ 20 e 11 têm n < 20.
- **Período:** foram priorizadas observações de 2025 em diante (5.012 fotos). Só quando faltavam é que entraram as mais antigas (779).
- **Licenças:** a preferência foi CC0/CC-BY/CC-BY-SA, mas a maioria das fotos do iNaturalist é CC-BY-NC. Ficou assim: CC-BY-NC 3.571, CC-BY 1.162, CC0 311, CC-BY-SA 176, CC-BY-NC-SA 76, CC-BY-NC-ND 21 e 474 sem licença aberta. As fotos servem só para medir. Não estão no repositório e não são redistribuídas. A lista de observações e fotos usadas, com espécie, licença e crédito, está em `amostra_ids.csv`, e cada foto pode ser vista em inaturalist.org/photos/&lt;id&gt;.
- **Fora da base:** 300 observações de plantas do Brasil (2025+), identificadas até espécie, sorteadas com semente fixa (20251105), com 1 por espécie e 1 por observador, excluídas as espécies da base e os seus sinônimos.

## Como evitamos vazamento (foto de teste parecida demais com a de referência)

1. **Por ID:** ficaram de fora do teste todas as observações que geraram as 2.320 fotos de referência do índice publicado, e também as fotos usadas antes para calibrar o limiar de 0,75. Ao todo são 2.647 observações excluídas.
2. **Por conteúdo:** cada foto de teste foi comparada com as 2.320 referências e com as outras fotos de teste por hash perceptual (dHash de 64 bits, até 6 bits de diferença) e por semelhança de vetor (cosseno ≥ 0,99). Saíram 5 fotos, todas repetidas dentro do próprio teste. Nenhuma foto de teste é cópia de uma referência. O corte de cosseno começou em 0,95, mas a inspeção visual mostrou que pares entre 0,95 e 0,98 são fotos diferentes da mesma espécie e não duplicatas. Por isso ficou só o critério de cópia real, para não descartar justamente as fotos típicas.
3. **Sensibilidade por observador:** quando o observador também tem foto nas referências (1.250 fotos), a 1ª opção acerta 87,0 %. Quando é um observador novo (4.541 fotos), acerta 89,3 %. Não há sinal de que "conhecer o fotógrafo" infle o resultado.

## Contaminação do pré-treino do BioCLIP-2

O modelo de base do app (BioCLIP-2) foi pré-treinado no TreeOfLife-200M, que inclui fotos do iNaturalist. Então parte das fotos de teste pode ter passado pelo pré-treino, mesmo não estando no índice. As fotos de teste **não foram usadas como referência do índice**, mas não dá para dizer que o modelo nunca as viu.

**Data de corte dos dados de treino**, segundo o cartão oficial do dataset (huggingface.co/datasets/imageomics/TreeOfLife-200M, revisão a8f38b4, a usada no BioCLIP-2 e no paper de Gu et al., NeurIPS 2025, arXiv 2505.23883):

- **GBIF**, por onde entram as fotos do iNaturalist: instantâneo de ocorrências de **1º/05/2024** (DOI 10.15468/dl.bfv433).
- **EOL**, que também espelha fotos do iNaturalist: acessado em **agosto de 2024**.

Usamos o corte mais tardio, **31/08/2024**. Para cada foto de teste baixamos pela API do iNaturalist a data de criação (envio) da observação. A foto não pode ter sido enviada antes da observação existir, então uma observação criada a partir de 1º/09/2024 com certeza não estava no pré-treino. Como o corte é anterior a 2025, a faixa "entre jan/2025 e o corte" não existe. As faixas ficaram assim:

| Faixa (data de criação da observação) | n | Top-1 (IC 95%) | Top-3 (IC 95%) | Espécies-chave: n | Espécies-chave: top-1 (IC 95%) | Espécies-chave: top-3 (IC 95%) |
|---|---|---|---|---|---|---|
| (a) a partir de 1º/09/2024: fora do pré-treino com certeza | 5155 | 90,6% (89,8%–91,4%) | 96,9% (96,4%–97,3%) | 1559 | 88,1% (86,4%–89,6%) | 95,5% (94,3%–96,4%) |
| (b) 1º/05/2024 a 31/08/2024: só poderia ter entrado pelo EOL | 56 | 71,4% (58,5%–81,6%) | 92,9% (83,0%–97,2%) | 39 | 61,5% (45,9%–75,1%) | 89,7% (76,4%–95,9%) |
| (c) antes de 1º/05/2024: pode estar no pré-treino | 580 | 74,3% (70,6%–77,7%) | 90,9% (88,2%–93,0%) | 388 | 71,7% (67,0%–75,9%) | 89,7% (86,3%–92,3%) |
| Criadas em 2025 ou depois | 5060 | 90,8% (89,9%–91,5%) | 96,9% (96,4%–97,3%) | 1486 | 88,3% (86,6%–89,8%) | 95,4% (94,2%–96,4%) |
| Criadas antes de 2025 | 731 | 75,4% (72,1%–78,4%) | 91,5% (89,3%–93,3%) | 500 | 72,6% (68,5%–76,3%) | 90,6% (87,7%–92,9%) |

**Leitura:** não há sinal de inflação por contaminação. As fotos que com certeza ficaram fora do pré-treino acertam **mais**, e não menos. A diferença bruta vem quase toda da espécie: as fotos antigas só entraram nas espécies com poucas fotos recentes, que são justamente as árvores nativas mais difíceis (veja "Período" acima). Comparando dentro das mesmas 39 espécies que têm fotos dos dois períodos, as fotos novas (a), padronizadas para a mesma mistura de espécies, acertam **77,8 %** na 1ª opção e as antigas (b + c) **74,1 %** (n = 946 e 636). Os 88,8 % podem ser citados. O recorte sem nenhuma chance de contaminação dá **90,6 %** (89,8 a 91,4 %, n = 5.155).

**Frase sugerida:** "Em 5.791 fotos do iNaturalist de 157 espécies da base, não usadas como referência do índice, o classificador offline acertou a espécie na 1ª opção em 88,8 % (IC 95 % 88,0–89,6 %) e entre as 3 primeiras em 96,2 %. Nas 5.155 fotos enviadas ao iNaturalist depois da data de corte dos dados de pré-treino do BioCLIP-2 (agosto de 2024), o acerto na 1ª opção foi de 90,6 % (89,8–91,4 %), sem sinal de inflação por contaminação."

## Mini teste: fotos de qualidade inferior (rótulo à parte, n pequeno)

**Não somar com o teste principal.** São 99 observações das espécies-chave com grau "casual" ou "precisa de ID" no iNaturalist, ou seja, fora do grau "pesquisa". Regras: criadas a partir de 1º/09/2024 (fora do pré-treino), identificação da comunidade na espécie com pelo menos 2 identificadores diferentes concordando, nenhuma observação do teste principal, das referências ou da calibração, 1 por observador e até 7 por espécie. Os IDs estão em `amostra_ids.csv` (conjunto `mini_teste_qualidade_inferior`) e os detalhes em `resultados.json` (`mini_teste_fotos_qualidade_inferior`).

| Recorte | n | Top-1 (IC 95%) | Top-3 (IC 95%) | Aceitas no limiar | Acerto entre aceitas |
|---|---|---|---|---|---|
| Mini teste, todas | 99 | 88,9% (81,2%–93,7%) | 96,0% (90,1%–98,4%) | 70,7% | 97,1% (68/70) |
| Só "casual" | 93 | 88,2% (80,1%–93,3%) | 95,7% (89,5%–98,3%) | 72,0% | 97,0% |
| Só "precisa de ID" | 6 | 6/6 (61,0%–100%) | 6/6 | 3/6 | 3/3 |

Para comparar, o teste principal (grau pesquisa) dessas mesmas espécies, com o mesmo peso de cada uma, dá 87,8 % na 1ª opção. **Não apareceu queda, mas o teste mede pouco.** 88 das 99 fotos são "casual" só porque a planta é cultivada (quintal, vaso, praça), não porque a foto é ruim. Além disso, faltam justamente as árvores nativas difíceis: pinhão-bravo, jurema-preta e quixabeira ficaram sem nenhuma foto elegível, e aroeira e umburana-de-cambão têm 1 foto cada. Os erros foram em mulungu (4/7), umbu (0/2), umburana-de-cambão (0/1), umburana-de-cheiro (2/3), angico (3/4), capim-santo, ipê-roxo e pau-ferro (6/7 cada). Este mini teste **não substitui** um teste com fotos tiradas no campo por usuários leigos.

## Como a medição imita o app

- Usamos o mesmo modelo (`plant-classifier-int8.onnx`, sha256 6452d330…) e o mesmo índice (`plant-index.bin`, sha256 b1c553fe…) publicados e baixados pelo app.
- O pré-processamento é igual ao do `PlantClassifier.kt`: orientação EXIF, redução por potência de 2 na leitura, redimensionamento bilinear sem suavização (como o `Bitmap.createScaledBitmap`), recorte central de 224×224 e normalização.
- A pontuação também é a do app: semelhança com o nome científico mais a média das 3 fotos de referência mais parecidas. A confiança é a probabilidade da melhor espécie multiplicada pela probabilidade de a planta estar na base. A resposta só aparece se a confiança for ≥ 0,75.

## Como o intervalo de confiança foi calculado

Cada taxa vem com o **IC de 95 % de Wilson**, que funciona bem com n pequeno e com taxas perto de 0 % ou 100 %. Na "média por espécie", em que cada espécie pesa igual, o IC vem de **bootstrap estratificado**: 2.000 reamostragens das fotos dentro de cada espécie, com semente 20251105. As fotos de um mesmo observador nunca se repetem dentro de uma espécie, então as observações de cada espécie são independentes quanto ao fotógrafo.

## Tabelas

### Geral (limiar do app = 0,75)

| Recorte | n fotos | Top-1 (IC 95%) | Top-3 (IC 95%) | Gênero certo no top-1 | Aceitas no limiar | Acerto entre aceitas | Erro entre aceitas |
|---|---|---|---|---|---|---|---|
| Todas as espécies | 5791 | 88,8% (88,0%–89,6%) | 96,2% (95,7%–96,7%) | 91,1% (90,3%–91,8%) | 76,1% (75,0%–77,1%) | 97,2% (96,7%–97,7%) | 2,8% (2,3%–3,3%) |
| Espécies-chave | 1986 | 84,3% (82,7%–85,9%) | 94,2% (93,1%–95,2%) | 85,5% (83,9%–87,0%) | 67,9% (65,8%–69,9%) | 96,1% (94,9%–97,0%) | 3,9% (3,0%–5,1%) |
| Demais espécies | 3805 | 91,1% (90,2%–92,0%) | 97,3% (96,7%–97,7%) | 94,0% (93,2%–94,7%) | 80,3% (79,0%–81,6%) | 97,8% (97,2%–98,2%) | 2,2% (1,8%–2,8%) |

Média por espécie (cada espécie pesa igual, 157 espécies): top-1 88,3% (IC 95% bootstrap 87,5%–89,2%); top-3 96,0% (95,4%–96,7%). Espécies-chave: top-1 82,2% (80,0%–84,4%).

### Plantas fora da base

| Recorte | Aceitas como espécie da base (falso positivo) |
|---|---|
| Todas (300 fotos, 300 espécies) | 37/300 = 12,3% (9,1%–16,5%) |
| Espécie aparece na lista de nomes "de fora" do índice | 0/22 = 0,0% (0,0%–14,9%) |
| Gênero tem espécie na base (ex.: outra *Erythrina*, outro *Melocactus*) | 13/56 = 23,2% (14,1%–35,8%) |
| Gênero sem nenhuma espécie na base | 24/244 = 9,8% (6,7%–14,2%) |
| Espécie não aparece nessa lista | 37/278 = 13,3% (9,8%–17,8%) |

### Sensibilidade: mesmo observador nas fotos de referência

| Recorte | n | Top-1 (IC 95%) |
|---|---|---|
| Observador também tem foto nas referências do índice | 1250 | 87,0% (85,0%–88,7%) |
| Observador novo | 4541 | 89,3% (88,4%–90,2%) |

### Comparação com IA na nuvem (mesmo prompt e endpoint do app)

Subamostra sorteada com semente 20251105: 399 fotos de espécies da base + 50 de fora da base. A cota gratuita da chave do app (20 requisições por dia por modelo) interrompeu as chamadas; entram só as fotos que cada modelo respondeu, comparadas com o classificador offline NAS MESMAS fotos.

| Sistema | Fotos respondidas | Espécie certa (IC 95%) | Gênero certo (IC 95%) | SaberIA offline nas mesmas fotos: top-1 (IC 95%) | Latência mediana da nuvem |
|---|---|---|---|---|---|
| gemini-3.5-flash | 11 | 6/11 = 54,5% (28,0%–78,7%) | 8/11 = 72,7% (43,4%–90,2%) | 11/11 = 100,0% (74,1%–100,0%) | 4,2 s |
| gemini-2.5-flash | 20 | 7/20 = 35,0% (18,1%–56,7%) | 12/20 = 60,0% (38,7%–78,1%) | 19/20 = 95,0% (76,4%–99,1%) | 3,5 s |

SaberIA offline na subamostra inteira (399 fotos): top-1 87,2% (83,6%–90,1%), top-3 96,7% (94,5%–98,1%); aceitas no limiar 71,9% (67,3%–76,1%), acerto entre aceitas 97,2% (94,6%–98,6%); fora da base aceitas 10/50 = 20,0% (11,2%–33,0%).

### Por espécie

| Espécie | Chave | n | Top-1 (IC 95%) | Top-3 (IC 95%) | Aceitas | Acerto entre aceitas | Confusão mais comum |
|---|---|---|---|---|---|---|---|
| *Aloe vera* | sim | 100 | 100/100 = 100,0% (96,3%–100,0%) | 100,0% (96,3%–100,0%) | 97/100 | 97/97 |  |
| *Amburana cearensis* | sim | 53 | 32/53 = 60,4% (46,9%–72,4%) | 81,1% (68,6%–89,4%) | 25/53 | 23/25 | *Cenostigma pyramidale* (6) |
| *Anadenanthera colubrina* | sim | 100 | 65/100 = 65,0% (55,2%–73,6%) | 96,0% (90,2%–98,4%) | 40/100 | 35/40 | *Spondias mombin* (12) |
| *Astronium urundeuva* | sim | 77 | 43/77 = 55,8% (44,7%–66,4%) | 66,2% (55,1%–75,8%) | 34/77 | 32/34 | *Amburana cearensis* (8) |
| *Cenostigma pyramidale* | sim | 7 | 4/7 = 57,1% (25,1%–84,2%) | 85,7% (48,7%–97,4%) | 4/7 | 4/4 | *Tabebuia aurea* (1) |
| *Cereus jamacaru* | sim | 100 | 90/100 = 90,0% (82,6%–94,5%) | 99,0% (94,5%–99,8%) | 23/100 | 23/23 | *Pilosocereus pachycladus* (6) |
| *Coleus barbatus* | sim | 100 | 94/100 = 94,0% (87,5%–97,2%) | 99,0% (94,5%–99,8%) | 77/100 | 76/77 | *Coleus amboinicus* (5) |
| *Commiphora leptophloeos* | sim | 95 | 66/95 = 69,5% (59,6%–77,8%) | 97,9% (92,7%–99,4%) | 52/95 | 40/52 | *Amburana cearensis* (20) |
| *Cymbopogon citratus* | sim | 100 | 99/100 = 99,0% (94,5%–99,8%) | 100,0% (96,3%–100,0%) | 92/100 | 92/92 | *Zingiber officinale* (1) |
| *Erythrina velutina* | sim | 100 | 59/100 = 59,0% (49,2%–68,1%) | 76,0% (66,8%–83,3%) | 48/100 | 36/48 | *Ceiba glaziovii* (9) |
| *Handroanthus impetiginosus* | sim | 100 | 87/100 = 87,0% (79,0%–92,2%) | 94,0% (87,5%–97,2%) | 64/100 | 64/64 | *Handroanthus serratifolius* (3) |
| *Jatropha mollissima* | sim | 100 | 90/100 = 90,0% (82,6%–94,5%) | 94,0% (87,5%–97,2%) | 83/100 | 79/83 | *Amburana cearensis* (3) |
| *Libidibia ferrea* | sim | 100 | 79/100 = 79,0% (70,0%–85,8%) | 97,0% (91,5%–99,0%) | 58/100 | 52/58 | *Hymenaea courbaril* (6) |
| *Lippia alba* | sim | 99 | 96/99 = 97,0% (91,5%–99,0%) | 99,0% (94,5%–99,8%) | 92/99 | 91/92 | *Lippia origanoides* (2) |
| *Melocactus zehntneri* | sim | 99 | 99/99 = 100,0% (96,3%–100,0%) | 100,0% (96,3%–100,0%) | 97/99 | 97/97 |  |
| *Mimosa tenuiflora* | sim | 100 | 76/100 = 76,0% (66,8%–83,3%) | 95,0% (88,8%–97,9%) | 35/100 | 33/35 | *Prosopis juliflora* (7) |
| *Opuntia ficus-indica* | sim | 100 | 99/100 = 99,0% (94,5%–99,8%) | 100,0% (96,3%–100,0%) | 93/100 | 93/93 | *Xiquexique gounellei* (1) |
| *Sarcomphalus joazeiro* | sim | 91 | 83/91 = 91,2% (83,6%–95,5%) | 97,8% (92,3%–99,4%) | 61/91 | 60/61 | *Microdesmia rigida* (2) |
| *Schinus terebinthifolia* | sim | 100 | 99/100 = 99,0% (94,5%–99,8%) | 99,0% (94,5%–99,8%) | 94/100 | 94/94 | *Cnidoscolus quercifolius* (1) |
| *Sideroxylon obtusifolium* | sim | 100 | 73/100 = 73,0% (63,6%–80,7%) | 86,0% (77,9%–91,5%) | 53/100 | 51/53 | *Spondias mombin* (4) |
| *Spondias tuberosa* | sim | 65 | 47/65 = 72,3% (60,4%–81,7%) | 90,8% (81,3%–95,7%) | 36/65 | 33/36 | *Commiphora leptophloeos* (9) |
| *Xiquexique gounellei* | sim | 100 | 95/100 = 95,0% (88,8%–97,9%) | 98,0% (93,0%–99,5%) | 90/100 | 90/90 | *Cereus jamacaru* (3) |
| *Acanthospermum hispidum* |  | 30 | 30/30 = 100,0% (88,6%–100,0%) | 100,0% (88,6%–100,0%) | 28/30 | 28/28 |  |
| *Ageratum conyzoides* |  | 30 | 30/30 = 100,0% (88,6%–100,0%) | 100,0% (88,6%–100,0%) | 29/30 | 29/29 |  |
| *Allium cepa* |  | 30 | 28/30 = 93,3% (78,7%–98,2%) | 100,0% (88,6%–100,0%) | 27/30 | 26/27 | *Allium sativum* (2) |
| *Allium sativum* |  | 30 | 29/30 = 96,7% (83,3%–99,4%) | 100,0% (88,6%–100,0%) | 27/30 | 27/27 | *Operculina macrocarpa* (1) |
| *Alpinia zerumbet* |  | 30 | 28/30 = 93,3% (78,7%–98,2%) | 100,0% (88,6%–100,0%) | 28/30 | 28/28 | *Zingiber officinale* (2) |
| *Alternanthera brasiliana* |  | 30 | 29/30 = 96,7% (83,3%–99,4%) | 96,7% (83,3%–99,4%) | 27/30 | 27/27 | *Microdesmia rigida* (1) |
| *Anacardium occidentale* |  | 30 | 28/30 = 93,3% (78,7%–98,2%) | 96,7% (83,3%–99,4%) | 27/30 | 27/27 | *Terminalia catappa* (2) |
| *Ananas comosus* |  | 30 | 28/30 = 93,3% (78,7%–98,2%) | 100,0% (88,6%–100,0%) | 27/30 | 26/27 | *Aloe vera* (1) |
| *Annona squamosa* |  | 30 | 27/30 = 90,0% (74,4%–96,5%) | 100,0% (88,6%–100,0%) | 25/30 | 24/25 | *Persea americana* (2) |
| *Artemisia absinthium* |  | 30 | 30/30 = 100,0% (88,6%–100,0%) | 100,0% (88,6%–100,0%) | 29/30 | 29/29 |  |
| *Aspidosperma pyrifolium* |  | 30 | 27/30 = 90,0% (74,4%–96,5%) | 96,7% (83,3%–99,4%) | 18/30 | 18/18 | *Cordia oncocalyx* (1) |
| *Attalea speciosa* |  | 30 | 26/30 = 86,7% (70,3%–94,7%) | 100,0% (88,6%–100,0%) | 17/30 | 17/17 | *Cocos nucifera* (3) |
| *Bauhinia cheilantha* |  | 25 | 18/25 = 72,0% (52,4%–85,7%) | 100,0% (86,7%–100,0%) | 18/25 | 16/18 | *Bauhinia forficata* (4) |
| *Bauhinia forficata* |  | 30 | 24/30 = 80,0% (62,7%–90,5%) | 93,3% (78,7%–98,2%) | 17/30 | 16/17 | *Bauhinia cheilantha* (4) |
| *Bidens pilosa* |  | 30 | 30/30 = 100,0% (88,6%–100,0%) | 100,0% (88,6%–100,0%) | 28/30 | 28/28 |  |
| *Bixa orellana* |  | 30 | 29/30 = 96,7% (83,3%–99,4%) | 100,0% (88,6%–100,0%) | 27/30 | 27/27 | *Lantana camara* (1) |
| *Bowdichia virgilioides* |  | 30 | 26/30 = 86,7% (70,3%–94,7%) | 96,7% (83,3%–99,4%) | 19/30 | 19/19 | *Libidibia ferrea* (1) |
| *Bromelia laciniosa* |  | 11 | 11/11 = 100,0% (74,1%–100,0%) | 100,0% (74,1%–100,0%) | 10/11 | 10/10 |  |
| *Byrsonima crassifolia* |  | 30 | 24/30 = 80,0% (62,7%–90,5%) | 86,7% (70,3%–94,7%) | 21/30 | 20/21 | *Spondias mombin* (2) |
| *Cajanus cajan* |  | 30 | 29/30 = 96,7% (83,3%–99,4%) | 96,7% (83,3%–99,4%) | 26/30 | 26/26 | *Cenostigma pyramidale* (1) |
| *Calotropis procera* |  | 30 | 30/30 = 100,0% (88,6%–100,0%) | 100,0% (88,6%–100,0%) | 29/30 | 29/29 |  |
| *Capraria biflora* |  | 30 | 30/30 = 100,0% (88,6%–100,0%) | 100,0% (88,6%–100,0%) | 29/30 | 29/29 |  |
| *Carica papaya* |  | 30 | 30/30 = 100,0% (88,6%–100,0%) | 100,0% (88,6%–100,0%) | 29/30 | 29/29 |  |
| *Casearia sylvestris* |  | 30 | 28/30 = 93,3% (78,7%–98,2%) | 100,0% (88,6%–100,0%) | 22/30 | 22/22 | *Annona squamosa* (1) |
| *Ceiba glaziovii* |  | 29 | 29/29 = 100,0% (88,3%–100,0%) | 100,0% (88,3%–100,0%) | 20/29 | 20/20 |  |
| *Cinnamomum verum* |  | 30 | 30/30 = 100,0% (88,6%–100,0%) | 100,0% (88,6%–100,0%) | 28/30 | 28/28 |  |
| *Cissus verticillata* |  | 30 | 29/30 = 96,7% (83,3%–99,4%) | 100,0% (88,6%–100,0%) | 26/30 | 26/26 | *Sarcomphalus joazeiro* (1) |
| *Cnidoscolus quercifolius* |  | 30 | 27/30 = 90,0% (74,4%–96,5%) | 100,0% (88,6%–100,0%) | 23/30 | 23/23 | *Sideroxylon obtusifolium* (2) |
| *Cnidoscolus urens* |  | 30 | 27/30 = 90,0% (74,4%–96,5%) | 100,0% (88,6%–100,0%) | 27/30 | 26/27 | *Jatropha gossypiifolia* (1) |
| *Cocos nucifera* |  | 30 | 30/30 = 100,0% (88,6%–100,0%) | 100,0% (88,6%–100,0%) | 30/30 | 30/30 |  |
| *Coleus amboinicus* |  | 30 | 28/30 = 93,3% (78,7%–98,2%) | 96,7% (83,3%–99,4%) | 25/30 | 24/25 | *Coleus barbatus* (1) |
| *Coleus comosus* |  | 8 | 7/8 = 87,5% (52,9%–97,8%) | 100,0% (67,6%–100,0%) | 5/8 | 5/5 | *Coleus barbatus* (1) |
| *Combretum leprosum* |  | 30 | 28/30 = 93,3% (78,7%–98,2%) | 96,7% (83,3%–99,4%) | 24/30 | 24/24 | *Croton blanchetianus* (1) |
| *Copaifera langsdorffii* |  | 30 | 16/30 = 53,3% (36,1%–69,8%) | 83,3% (66,4%–92,7%) | 11/30 | 11/11 | *Sarcomphalus joazeiro* (2) |
| *Copernicia prunifera* |  | 30 | 30/30 = 100,0% (88,6%–100,0%) | 100,0% (88,6%–100,0%) | 24/30 | 24/24 |  |
| *Cordia oncocalyx* |  | 21 | 15/21 = 71,4% (50,0%–86,2%) | 85,7% (65,4%–95,0%) | 12/21 | 10/12 | *Persea americana* (3) |
| *Coriandrum sativum* |  | 30 | 28/30 = 93,3% (78,7%–98,2%) | 100,0% (88,6%–100,0%) | 28/30 | 27/28 | *Petroselinum crispum* (1) |
| *Croton blanchetianus* |  | 30 | 27/30 = 90,0% (74,4%–96,5%) | 96,7% (83,3%–99,4%) | 22/30 | 22/22 | *Croton heliotropiifolius* (2) |
| *Croton grewioides* |  | 5 | 1/5 = 20,0% (3,6%–62,5%) | 80,0% (37,5%–96,4%) | 3/5 | 1/3 | *Croton heliotropiifolius* (3) |
| *Croton heliotropiifolius* |  | 30 | 29/30 = 96,7% (83,3%–99,4%) | 100,0% (88,6%–100,0%) | 28/30 | 27/28 | *Croton blanchetianus* (1) |
| *Curcuma longa* |  | 30 | 29/30 = 96,7% (83,3%–99,4%) | 100,0% (88,6%–100,0%) | 28/30 | 28/28 | *Neoglaziovia variegata* (1) |
| *Dysphania ambrosioides* |  | 30 | 30/30 = 100,0% (88,6%–100,0%) | 100,0% (88,6%–100,0%) | 29/30 | 29/29 |  |
| *Egletes viscosa* |  | 30 | 30/30 = 100,0% (88,6%–100,0%) | 100,0% (88,6%–100,0%) | 30/30 | 30/30 |  |
| *Erythrina mulungu* |  | 30 | 24/30 = 80,0% (62,7%–90,5%) | 90,0% (74,4%–96,5%) | 20/30 | 19/20 | *Tabebuia aurea* (2) |
| *Eugenia uniflora* |  | 30 | 26/30 = 86,7% (70,3%–94,7%) | 96,7% (83,3%–99,4%) | 24/30 | 23/24 | *Malpighia emarginata* (2) |
| *Euphorbia tirucalli* |  | 30 | 30/30 = 100,0% (88,6%–100,0%) | 100,0% (88,6%–100,0%) | 29/30 | 29/29 |  |
| *Foeniculum vulgare* |  | 30 | 30/30 = 100,0% (88,6%–100,0%) | 100,0% (88,6%–100,0%) | 30/30 | 30/30 |  |
| *Genipa americana* |  | 30 | 21/30 = 70,0% (52,1%–83,3%) | 90,0% (74,4%–96,5%) | 14/30 | 14/14 | *Ceiba glaziovii* (2) |
| *Gossypium barbadense* |  | 30 | 28/30 = 93,3% (78,7%–98,2%) | 100,0% (88,6%–100,0%) | 24/30 | 24/24 | *Psidium guajava* (1) |
| *Gymnanthemum amygdalinum* |  | 30 | 27/30 = 90,0% (74,4%–96,5%) | 100,0% (88,6%–100,0%) | 22/30 | 22/22 | *Persea americana* (2) |
| *Hancornia speciosa* |  | 30 | 25/30 = 83,3% (66,4%–92,7%) | 90,0% (74,4%–96,5%) | 23/30 | 23/23 | *Spondias tuberosa* (2) |
| *Handroanthus serratifolius* |  | 30 | 18/30 = 60,0% (42,3%–75,4%) | 90,0% (74,4%–96,5%) | 13/30 | 11/13 | *Tabebuia aurea* (9) |
| *Harrisia adscendens* |  | 30 | 29/30 = 96,7% (83,3%–99,4%) | 100,0% (88,6%–100,0%) | 28/30 | 27/28 | *Xiquexique gounellei* (1) |
| *Heliotropium indicum* |  | 30 | 30/30 = 100,0% (88,6%–100,0%) | 100,0% (88,6%–100,0%) | 30/30 | 30/30 |  |
| *Hymenaea courbaril* |  | 30 | 23/30 = 76,7% (59,1%–88,2%) | 90,0% (74,4%–96,5%) | 21/30 | 21/21 | *Ceiba glaziovii* (2) |
| *Hymenaea martiana* |  | 11 | 1/11 = 9,1% (1,6%–37,7%) | 45,5% (21,3%–72,0%) | 4/11 | 0/4 | *Hymenaea stigonocarpa* (4) |
| *Hymenaea stigonocarpa* |  | 30 | 23/30 = 76,7% (59,1%–88,2%) | 86,7% (70,3%–94,7%) | 16/30 | 15/16 | *Amburana cearensis* (1) |
| *Ipomoea asarifolia* |  | 30 | 30/30 = 100,0% (88,6%–100,0%) | 100,0% (88,6%–100,0%) | 30/30 | 30/30 |  |
| *Jatropha curcas* |  | 30 | 29/30 = 96,7% (83,3%–99,4%) | 100,0% (88,6%–100,0%) | 28/30 | 27/28 | *Ricinus communis* (1) |
| *Jatropha gossypiifolia* |  | 30 | 29/30 = 96,7% (83,3%–99,4%) | 100,0% (88,6%–100,0%) | 26/30 | 26/26 | *Ricinus communis* (1) |
| *Justicia pectoralis* |  | 30 | 28/30 = 93,3% (78,7%–98,2%) | 100,0% (88,6%–100,0%) | 28/30 | 28/28 | *Alternanthera brasiliana* (1) |
| *Kalanchoe crenata* |  | 13 | 8/13 = 61,5% (35,5%–82,3%) | 61,5% (35,5%–82,3%) | 12/13 | 8/12 | *Kalanchoe pinnata* (5) |
| *Kalanchoe pinnata* |  | 30 | 30/30 = 100,0% (88,6%–100,0%) | 100,0% (88,6%–100,0%) | 30/30 | 30/30 |  |
| *Lantana camara* |  | 30 | 30/30 = 100,0% (88,6%–100,0%) | 100,0% (88,6%–100,0%) | 28/30 | 28/28 |  |
| *Leonotis nepetifolia* |  | 30 | 30/30 = 100,0% (88,6%–100,0%) | 100,0% (88,6%–100,0%) | 30/30 | 30/30 |  |
| *Lippia grata* |  | 4 | 0/4 = 0,0% (0,0%–49,0%) | 75,0% (30,1%–95,4%) | 3/4 | 0/3 | *Lippia origanoides* (3) |
| *Lippia origanoides* |  | 30 | 30/30 = 100,0% (88,6%–100,0%) | 100,0% (88,6%–100,0%) | 29/30 | 29/29 |  |
| *Luffa operculata* |  | 23 | 20/23 = 87,0% (67,9%–95,5%) | 95,7% (79,0%–99,2%) | 12/23 | 12/12 | *Bixa orellana* (1) |
| *Malpighia emarginata* |  | 30 | 28/30 = 93,3% (78,7%–98,2%) | 96,7% (83,3%–99,4%) | 26/30 | 25/26 | *Tabebuia aurea* (1) |
| *Mangifera indica* |  | 30 | 26/30 = 86,7% (70,3%–94,7%) | 93,3% (78,7%–98,2%) | 24/30 | 24/24 | *Cinnamomum verum* (2) |
| *Manihot glaziovii* |  | 2 | 2/2 = 100,0% (34,2%–100,0%) | 100,0% (34,2%–100,0%) | 0/2 | – |  |
| *Marsypianthes chamaedrys* |  | 30 | 29/30 = 96,7% (83,3%–99,4%) | 100,0% (88,6%–100,0%) | 27/30 | 27/27 | *Mesosphaerum suaveolens* (1) |
| *Matricaria chamomilla* |  | 30 | 30/30 = 100,0% (88,6%–100,0%) | 100,0% (88,6%–100,0%) | 29/30 | 29/29 |  |
| *Melissa officinalis* |  | 30 | 29/30 = 96,7% (83,3%–99,4%) | 96,7% (83,3%–99,4%) | 26/30 | 26/26 | *Lippia origanoides* (1) |
| *Mentha pulegium* |  | 30 | 29/30 = 96,7% (83,3%–99,4%) | 100,0% (88,6%–100,0%) | 28/30 | 28/28 | *Mentha × piperita* (1) |
| *Mentha spicata* |  | 30 | 24/30 = 80,0% (62,7%–90,5%) | 100,0% (88,6%–100,0%) | 10/30 | 9/10 | *Mentha × villosa* (5) |
| *Mentha × piperita* |  | 30 | 25/30 = 83,3% (66,4%–92,7%) | 100,0% (88,6%–100,0%) | 19/30 | 17/19 | *Mentha spicata* (5) |
| *Mentha × villosa* |  | 30 | 24/30 = 80,0% (62,7%–90,5%) | 96,7% (83,3%–99,4%) | 22/30 | 20/22 | *Mentha spicata* (6) |
| *Mesosphaerum pectinatum* |  | 30 | 23/30 = 76,7% (59,1%–88,2%) | 96,7% (83,3%–99,4%) | 14/30 | 13/14 | *Mesosphaerum suaveolens* (6) |
| *Mesosphaerum suaveolens* |  | 30 | 28/30 = 93,3% (78,7%–98,2%) | 100,0% (88,6%–100,0%) | 27/30 | 26/27 | *Melissa officinalis* (2) |
| *Microdesmia rigida* |  | 20 | 19/20 = 95,0% (76,4%–99,1%) | 95,0% (76,4%–99,1%) | 8/20 | 8/8 | *Combretum leprosum* (1) |
| *Mikania glomerata* |  | 11 | 7/11 = 63,6% (35,4%–84,8%) | 100,0% (74,1%–100,0%) | 4/11 | 3/4 | *Cinnamomum verum* (2) |
| *Mimosa caesalpiniifolia* |  | 30 | 29/30 = 96,7% (83,3%–99,4%) | 96,7% (83,3%–99,4%) | 21/30 | 21/21 | *Sarcomphalus joazeiro* (1) |
| *Momordica charantia* |  | 30 | 30/30 = 100,0% (88,6%–100,0%) | 100,0% (88,6%–100,0%) | 30/30 | 30/30 |  |
| *Moringa oleifera* |  | 30 | 29/30 = 96,7% (83,3%–99,4%) | 96,7% (83,3%–99,4%) | 25/30 | 25/25 | *Cocos nucifera* (1) |
| *Neoglaziovia variegata* |  | 30 | 28/30 = 93,3% (78,7%–98,2%) | 100,0% (88,6%–100,0%) | 22/30 | 22/22 | *Amburana cearensis* (1) |
| *Ocimum basilicum* |  | 30 | 27/30 = 90,0% (74,4%–96,5%) | 100,0% (88,6%–100,0%) | 29/30 | 27/29 | *Alternanthera brasiliana* (1) |
| *Ocimum gratissimum* |  | 30 | 28/30 = 93,3% (78,7%–98,2%) | 96,7% (83,3%–99,4%) | 23/30 | 23/23 | *Coleus barbatus* (1) |
| *Operculina hamiltonii* |  | 30 | 28/30 = 93,3% (78,7%–98,2%) | 96,7% (83,3%–99,4%) | 28/30 | 27/28 | *Carica papaya* (1) |
| *Operculina macrocarpa* |  | 18 | 16/18 = 88,9% (67,2%–96,9%) | 100,0% (82,4%–100,0%) | 16/18 | 15/16 | *Operculina hamiltonii* (2) |
| *Parkinsonia aculeata* |  | 30 | 30/30 = 100,0% (88,6%–100,0%) | 100,0% (88,6%–100,0%) | 30/30 | 30/30 |  |
| *Passiflora cincinnata* |  | 30 | 27/30 = 90,0% (74,4%–96,5%) | 100,0% (88,6%–100,0%) | 27/30 | 26/27 | *Passiflora edulis* (2) |
| *Passiflora edulis* |  | 30 | 29/30 = 96,7% (83,3%–99,4%) | 96,7% (83,3%–99,4%) | 23/30 | 23/23 | *Amburana cearensis* (1) |
| *Persea americana* |  | 30 | 28/30 = 93,3% (78,7%–98,2%) | 96,7% (83,3%–99,4%) | 22/30 | 21/22 | *Handroanthus serratifolius* (1) |
| *Petiveria alliacea* |  | 30 | 29/30 = 96,7% (83,3%–99,4%) | 96,7% (83,3%–99,4%) | 29/30 | 29/29 | *Cymbopogon citratus* (1) |
| *Petroselinum crispum* |  | 30 | 30/30 = 100,0% (88,6%–100,0%) | 100,0% (88,6%–100,0%) | 27/30 | 27/27 |  |
| *Phyllanthus amarus* |  | 30 | 30/30 = 100,0% (88,6%–100,0%) | 100,0% (88,6%–100,0%) | 7/30 | 7/7 |  |
| *Phyllanthus niruri* |  | 30 | 13/30 = 43,3% (27,4%–60,8%) | 93,3% (78,7%–98,2%) | 5/30 | 2/5 | *Phyllanthus amarus* (16) |
| *Pilosocereus pachycladus* |  | 30 | 21/30 = 70,0% (52,1%–83,3%) | 100,0% (88,6%–100,0%) | 12/30 | 8/12 | *Xiquexique gounellei* (6) |
| *Pityrocarpa moniliformis* |  | 30 | 24/30 = 80,0% (62,7%–90,5%) | 86,7% (70,3%–94,7%) | 18/30 | 18/18 | *Amburana cearensis* (2) |
| *Plantago major* |  | 30 | 30/30 = 100,0% (88,6%–100,0%) | 100,0% (88,6%–100,0%) | 30/30 | 30/30 |  |
| *Plumbago scandens* |  | 30 | 27/30 = 90,0% (74,4%–96,5%) | 93,3% (78,7%–98,2%) | 26/30 | 25/26 | *Alternanthera brasiliana* (1) |
| *Portulaca oleracea* |  | 30 | 30/30 = 100,0% (88,6%–100,0%) | 100,0% (88,6%–100,0%) | 30/30 | 30/30 |  |
| *Prosopis juliflora* |  | 30 | 26/30 = 86,7% (70,3%–94,7%) | 96,7% (83,3%–99,4%) | 1/30 | 0/1 | *Mimosa tenuiflora* (2) |
| *Psidium guajava* |  | 30 | 30/30 = 100,0% (88,6%–100,0%) | 100,0% (88,6%–100,0%) | 29/30 | 29/29 |  |
| *Punica granatum* |  | 30 | 29/30 = 96,7% (83,3%–99,4%) | 96,7% (83,3%–99,4%) | 27/30 | 27/27 | *Cinnamomum verum* (1) |
| *Ricinus communis* |  | 30 | 30/30 = 100,0% (88,6%–100,0%) | 100,0% (88,6%–100,0%) | 29/30 | 29/29 |  |
| *Ruta graveolens* |  | 30 | 30/30 = 100,0% (88,6%–100,0%) | 100,0% (88,6%–100,0%) | 27/30 | 27/27 |  |
| *Salvia rosmarinus* |  | 30 | 30/30 = 100,0% (88,6%–100,0%) | 100,0% (88,6%–100,0%) | 30/30 | 30/30 |  |
| *Schinopsis brasiliensis* |  | 15 | 7/15 = 46,7% (24,8%–69,9%) | 60,0% (35,8%–80,2%) | 5/15 | 3/5 | *Amburana cearensis* (2) |
| *Scoparia dulcis* |  | 30 | 30/30 = 100,0% (88,6%–100,0%) | 100,0% (88,6%–100,0%) | 30/30 | 30/30 |  |
| *Selaginella convoluta* |  | 30 | 30/30 = 100,0% (88,6%–100,0%) | 100,0% (88,6%–100,0%) | 27/30 | 27/27 |  |
| *Senna obtusifolia* |  | 30 | 28/30 = 93,3% (78,7%–98,2%) | 100,0% (88,6%–100,0%) | 29/30 | 27/29 | *Senna occidentalis* (2) |
| *Senna occidentalis* |  | 30 | 30/30 = 100,0% (88,6%–100,0%) | 100,0% (88,6%–100,0%) | 28/30 | 28/28 |  |
| *Senna spectabilis* |  | 30 | 24/30 = 80,0% (62,7%–90,5%) | 96,7% (83,3%–99,4%) | 18/30 | 17/18 | *Senna occidentalis* (2) |
| *Sida cordifolia* |  | 30 | 29/30 = 96,7% (83,3%–99,4%) | 100,0% (88,6%–100,0%) | 29/30 | 28/29 | *Waltheria indica* (1) |
| *Solanum paniculatum* |  | 30 | 30/30 = 100,0% (88,6%–100,0%) | 100,0% (88,6%–100,0%) | 30/30 | 30/30 |  |
| *Spondias mombin* |  | 30 | 27/30 = 90,0% (74,4%–96,5%) | 100,0% (88,6%–100,0%) | 11/30 | 10/11 | *Tabebuia aurea* (1) |
| *Spondias purpurea* |  | 30 | 21/30 = 70,0% (52,1%–83,3%) | 86,7% (70,3%–94,7%) | 14/30 | 14/14 | *Amburana cearensis* (2) |
| *Stachytarpheta cayennensis* |  | 30 | 29/30 = 96,7% (83,3%–99,4%) | 96,7% (83,3%–99,4%) | 28/30 | 28/28 | *Coleus amboinicus* (1) |
| *Stryphnodendron adstringens* |  | 30 | 29/30 = 96,7% (83,3%–99,4%) | 100,0% (88,6%–100,0%) | 25/30 | 25/25 | *Anadenanthera colubrina* (1) |
| *Syagrus coronata* |  | 29 | 27/29 = 93,1% (78,0%–98,1%) | 100,0% (88,3%–100,0%) | 22/29 | 22/22 | *Attalea speciosa* (1) |
| *Syzygium cumini* |  | 30 | 23/30 = 76,7% (59,1%–88,2%) | 90,0% (74,4%–96,5%) | 21/30 | 21/21 | *Libidibia ferrea* (2) |
| *Tabebuia aurea* |  | 30 | 25/30 = 83,3% (66,4%–92,7%) | 93,3% (78,7%–98,2%) | 17/30 | 17/17 | *Handroanthus serratifolius* (3) |
| *Tacinga inamoena* |  | 30 | 29/30 = 96,7% (83,3%–99,4%) | 100,0% (88,6%–100,0%) | 27/30 | 27/27 | *Opuntia ficus-indica* (1) |
| *Tagetes erecta* |  | 30 | 30/30 = 100,0% (88,6%–100,0%) | 100,0% (88,6%–100,0%) | 25/30 | 25/25 |  |
| *Talisia esculenta* |  | 20 | 18/20 = 90,0% (69,9%–97,2%) | 90,0% (69,9%–97,2%) | 14/20 | 14/14 | *Mangifera indica* (1) |
| *Tamarindus indica* |  | 30 | 28/30 = 93,3% (78,7%–98,2%) | 100,0% (88,6%–100,0%) | 24/30 | 23/24 | *Anadenanthera colubrina* (1) |
| *Terminalia catappa* |  | 30 | 27/30 = 90,0% (74,4%–96,5%) | 93,3% (78,7%–98,2%) | 20/30 | 20/20 | *Genipa americana* (1) |
| *Turnera subulata* |  | 30 | 30/30 = 100,0% (88,6%–100,0%) | 100,0% (88,6%–100,0%) | 30/30 | 30/30 |  |
| *Varronia curassavica* |  | 30 | 28/30 = 93,3% (78,7%–98,2%) | 100,0% (88,6%–100,0%) | 26/30 | 26/26 | *Lippia origanoides* (1) |
| *Varronia leucocephala* |  | 30 | 29/30 = 96,7% (83,3%–99,4%) | 96,7% (83,3%–99,4%) | 29/30 | 28/29 | *Varronia curassavica* (1) |
| *Waltheria indica* |  | 30 | 29/30 = 96,7% (83,3%–99,4%) | 100,0% (88,6%–100,0%) | 29/30 | 28/29 | *Mesosphaerum pectinatum* (1) |
| *Ximenia americana* |  | 30 | 28/30 = 93,3% (78,7%–98,2%) | 100,0% (88,6%–100,0%) | 26/30 | 26/26 | *Spondias mombin* (1) |
| *Zingiber officinale* |  | 30 | 24/30 = 80,0% (62,7%–90,5%) | 93,3% (78,7%–98,2%) | 25/30 | 24/25 | *Curcuma longa* (4) |

## Índice v1.0.1 (reforço de aroeira, mulungu e umburana-de-cambão)

**O resultado principal deste documento continua sendo o do índice publicado (v1.0): 88,8 % na 1ª opção, sem ajuste.** O v1.0.1 é um arquivo de índice à parte (`plant-index-v1.0.1.bin`, sha256 d8c97ff0…); o v1.0.0 continua disponível. Os detalhes estão em [`index-v1.0.1/README.md`](index-v1.0.1/README.md).

O que mudou: saíram as 3 referências "todos os direitos reservados" (*Genipa americana*, *Pityrocarpa moniliformis* e *Spondias mombin*). Entraram 70 referências CC0/CC BY/CC BY-SA: 18 fotos extras de observações que já estavam no índice e 52 fotos de campo do Wikimedia Commons, conferidas pela categoria e pela descrição. Na revisão caíram 3 fotos: uma de *Schinus molle*, uma de *Erythrina mulungu* e uma não verificável.

**Ressalva metodológica:** as referências extras foram escolhidas depois de ver em que espécies o v1.0 errava **no teste**. Por isso, os ganhos medidos nesse mesmo teste são otimistas.

| Nas mesmas 5.791 fotos do teste (otimista) | v1.0 publicado | v1.0.1 |
|---|---|---|
| Top-1 geral | 88,8% (88,0–89,6) | 89,2% (88,3–90,0) |
| Top-1 espécies-chave | 84,3% (82,7–85,9) | 85,8% (84,1–87,2) |
| Top-1 demais espécies | 91,1% (90,2–92,0) | 91,0% (90,0–91,8) |
| Aroeira-do-sertão (n = 77) | 55,8% | 76,6% |
| Mulungu (n = 100) | 59,0% | 73,0% |
| Umburana-de-cambão (n = 95) | 69,5% | 70,5% |
| Fora da base: falso positivo | 12,3% (37/300) | 12,3% (37/300) |

Foto a foto, 32 erradas viraram certas e 11 certas viraram erradas (McNemar p = 0,0019). Sete espécies perderam 1 ou 2 fotos. A maior perda foi *Erythrina mulungu*, de 24 para 22 de 30.

**Teste novo, sem esse viés:** usamos 117 observações das 3 espécies que não tinham sido usadas em nada (nem teste, nem referência, nem calibração), com 1 por observador. Nelas, a 1ª opção passa de **51,3 % (42,3–60,2) para 73,5 % (64,9–80,7)**, com 26 erradas que viraram certas e nenhuma certa que virou errada (McNemar p < 0,0001). Por espécie: aroeira de 6/20 para 17/20, mulungu de 34/68 para 48/68 e umburana-de-cambão de 20/29 para 21/29. Entre os 47 observadores sem nenhuma foto no teste principal, o acerto vai de 51,1 % para 76,6 %. Este teste só mede as 3 espécies reforçadas.

## Outros sistemas

- **IA na nuvem (Gemini), mesmo endpoint, prompt e parâmetros do app:** a chave do app está no plano gratuito, que libera só 20 requisições por dia para cada modelo. Por isso a comparação planejada com 400 fotos não coube. O `gemini-3.5-flash`, modelo do app, respondeu 11 fotos da subamostra sorteada e acertou a espécie em 6 (54,5 %; IC 95 % de 28,0 a 78,7 %). O `gemini-2.5-flash` respondeu 20 e acertou 7 (35,0 %; 18,1 a 56,7 %). Nas mesmas fotos, o classificador offline acertou 11/11 e 19/20. Com n tão pequeno, os intervalos são largos. O que dá para afirmar é que a diferença aponta para o mesmo lado nas duas amostras. Não dá para afirmar um percentual preciso da nuvem. Para fechar n = 400, basta uma chave com faturamento: o script `nuvem.py rodar` retoma de onde parou.
- **OpenAI (GPT-4o):** a chave disponível é válida, mas está sem crédito (erro "insufficient_quota"). Não foi possível medir.
- **Qwen3-VL-2B local (medição anterior, outra amostra):** acertou 6 de 64 fotos (9,4 %; IC 95 % de 4,4 a 19,0 %), com o mesmo prompt do app, em 64 fotos recentes do iNaturalist de 8 espécies-chave. Essa amostra **não é a mesma** deste teste e o número não deve ser comparado lado a lado como se fosse.

## Desempenho no aparelho (Redmi 12, MediaTek Helio G88, 8 GB)

Fonte: registro do próprio app no aparelho (`files/plant-id.log`), com 16 identificações reais feitas em 31/10/2026 usando 4 threads.

- Tempo do modelo por foto: mediana de **3,3 s** (mínimo 3,0 s, máximo 4,8 s).
- Leitura e preparo da foto: mediana de 55 ms.
- Primeira carga do modelo, uma vez por sessão: mediana de 8,6 s (7,4 a 11,6 s; n = 6).
- Tamanho: modelo de 308 MB (int8) e índice de 5,5 MB. O download é feito uma vez e depois tudo funciona sem internet.

## Limitações (leia antes de citar os números)

- **Fotos do iNaturalist são mais fáceis que fotos de campo.** Em geral são enquadradas por quem já conhece a planta, com flor ou fruto à vista e boa luz. Uma foto tirada às pressas por um usuário leigo, de uma folha solta ou de um tronco sem folhas na seca, tende a ter acerto menor. Este número é um teto realista, não a garantia de uso no campo.
- **Viés de espécie:** espécies comuns e cultivadas (babosa, capim-santo, coroa-de-frade, palma, aroeira-vermelha) chegam a 99 a 100 %. As árvores nativas da Caatinga, que se parecem muito entre si quando estão sem folhas, ficam bem abaixo. Os piores casos com n ≥ 50 são aroeira-do-sertão (55,8 %), mulungu (59,0 %), umburana-de-cheiro (60,4 %), angico (65,0 %) e umburana-de-cambão (69,5 %). Entre as de n pequeno, as confusões acontecem dentro do mesmo gênero: *Lippia grata* (0/4), *Hymenaea martiana* (1/11), *Croton grewioides* (1/5) e *Phyllanthus niruri*, que vira *P. amarus*.
- **Mandacaru:** a 1ª opção acerta 90 %, mas só 23 de 100 fotos passam do limiar. A confiança fica dividida com cactos colunares parecidos, e a confusão mais comum é com o facheiro (*Pilosocereus pachycladus*).
- **Plantas fora da base:** o falso positivo sobe para 23,2 % (14,1 a 35,8 %) quando a planta é de um gênero que tem espécie na base, por exemplo outra *Erythrina*, outro *Melocactus*, outro *Sarcomphalus* ou outro *Solanum*. Quando o gênero não está na base, fica em 9,8 % (6,7 a 14,2 %). O app avisa que a identificação deve ser confirmada, e esse aviso continua necessário.
- **Tamanho da amostra por espécie:** com 30 fotos, o IC de uma espécie com 90 % de acerto vai de cerca de 74 % a 97 %. Diferenças pequenas entre espécies não são significativas.
- **Comparação com a nuvem:** ficou limitada pela cota gratuita (n = 11 e n = 20) e não serve para cravar um percentual da nuvem.
- **Pré-treino:** as fotos de teste não foram usadas como referência do índice, mas o BioCLIP-2 foi pré-treinado com fotos do iNaturalist até 2024. As 636 fotos de teste criadas antes de 1º/09/2024 podem ter passado pelo pré-treino. O recorte sem essa possibilidade (n = 5.155) não acerta menos.
- **Rótulos do iNaturalist:** o grau "pesquisa" exige acordo de 2/3 dos identificadores, mas ainda há erros de identificação. Isso tende a puxar o acerto medido para baixo, não para cima.
