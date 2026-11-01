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
