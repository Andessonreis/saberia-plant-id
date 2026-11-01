# Índice v1.0.1 (reforço de aroeira, mulungu e umburana-de-cambão)

`plant-index-v1.0.1.bin`, sha256 `d8c97ff0419fcafb04201bf22ef1196c66de983e6210a0e1be89b2287cc9a5d2` (também em `SHA256SUMS`). O arquivo é distribuído pelas releases, não por esta pasta, que guarda só a lista de mudanças e as métricas. Ele usa o mesmo formato, os mesmos rótulos e textos, o mesmo limiar (0,75) e o mesmo modelo (`plant-classifier-int8.onnx`, sha256 6452d330…) do índice publicado (v1.0, sha256 b1c553fe…). 

**O resultado principal da avaliação continua sendo o do índice v1.0.0: 88,8 % na 1ª opção, sem ajuste.**

## Ressalva metodológica (leia antes dos números)

As espécies reforçadas e as referências extras foram escolhidas **depois de ver onde o índice publicado errava no conjunto de teste**. Por isso, os ganhos de aroeira e mulungu medidos nesse mesmo teste são **otimistas**: houve desenvolvimento depois de ver o teste. Para uma estimativa sem esse viés, veja a seção "Teste novo" abaixo, feita em observações que não tinham sido usadas em nada.

## O que mudou em relação ao v1.0

- **Saíram 3 referências** "todos os direitos reservados": *Genipa americana* (obs. 198336222), *Pityrocarpa moniliformis* (obs. 189385896) e *Spondias mombin* (obs. 198336115).
- **Entraram 70 referências** CC0/CC BY/CC BY-SA, sem nenhuma NC. A lista com crédito está em `referencias_adicionadas.csv`.
  - 18 são fotos extras (2ª e 3ª foto) de observações do iNaturalist que **já estavam** no índice.
  - 52 são fotos de campo do Wikimedia Commons, conferidas uma a uma pela categoria e pela descrição.
- **Fotos descartadas:** 3 caíram na revisão humana. "Aroeira salsa" é *Schinus molle*, não *Astronium urundeuva*. "Erythrina mulungu seed" é outra espécie que já está na base. "Noronha2014 28" não tem categoria de espécie e não dá para conferir. Outras 2 saíram porque o autor tem foto no teste e 1 porque repetia uma referência que já existia. Tudo isso está em `removidas_e_descartadas.json`.
- **Por que não entrou nada novo do iNaturalist:** não há observação com licença livre dessas 3 espécies que esteja fora do teste e seja de um observador fora do teste.
- **Controle de vazamento:** nenhuma referência nova vem de observação do teste, do conjunto fora da base ou do mini teste. Nenhuma é cópia de foto de teste por dHash, e a maior semelhança de vetor com qualquer foto de teste é 0,933.

## Antes e depois, nas mesmas 5.791 fotos de teste (otimista para as 3 espécies)

| Recorte | v1.0.0 | v1.0.1 |
|---|---|---|
| Top-1 geral | 88,8% (88,0–89,6) | 89,2% (88,3–90,0) |
| Top-3 geral | 96,2% (95,7–96,7) | 96,6% (96,1–97,1) |
| Aceitas no limiar 0,75 | 76,1% (75,0–77,1) | 76,4% (75,3–77,5) |
| Acerto entre aceitas | 97,2% (96,7–97,7) | 97,4% (96,9–97,9) |
| Top-1 espécies-chave (n = 1.986) | 84,3% (82,7–85,9) | 85,8% (84,1–87,2) |
| Top-1 demais espécies (n = 3.805) | 91,1% (90,2–92,0) | 91,0% (90,0–91,8) |
| Fora da base: falso positivo (n = 300) | 12,3% (37/300) | 12,3% (37/300) |
| Aroeira-do-sertão, top-1 (n = 77) | 55,8% (43/77) | 76,6% (59/77) |
| Mulungu, top-1 (n = 100) | 59,0% (59/100) | 73,0% (73/100) |
| Umburana-de-cambão, top-1 (n = 95) | 69,5% (66/95) | 70,5% (67/95) |
| Mini teste de qualidade inferior, top-1 (n = 99) | 88,9% | 90,9% |

Foto a foto, 32 erradas viraram certas e 11 certas viraram erradas (McNemar exato p = 0,0019). Sete espécies perderam 1 ou 2 fotos no top-1: *Erythrina mulungu* 24 → 22 de 30, umburana-de-cheiro 32 → 30 de 53, *Spondias mombin* 27 → 25 de 30, angico 65 → 64 de 100, *Ceiba glaziovii* 29 → 28 de 29, copaíba 16 → 15 de 30 e *Pityrocarpa moniliformis* 24 → 23 de 30. Duas dessas perdas, uma de *Spondias* e a de *Pityrocarpa*, vêm só de ter tirado as fotos "todos os direitos reservados". Esses números são idênticos aos da versão com as 3 fotos que caíram na revisão: elas não mudavam nenhuma predição do teste.

## Teste novo (estimativa sem o viés de ter olhado o teste)

Usamos 117 observações das 3 espécies que **não foram usadas em nada antes**: fora do teste principal, do conjunto fora da base, do mini teste, das referências e da calibração. São de grau pesquisa, ou "precisa de ID" com 2 ou mais identificadores concordando, com 1 por observador e qualquer licença, já que servem só para medir. Nenhuma é cópia de referência ou de foto de teste. Os detalhes estão em `teste_novo_3_especies.json` e o script é `../scripts/teste_novo_alvo.py`.

| Recorte | n | v1.0 top-1 | v1.0.1 top-1 | v1.0 top-3 | v1.0.1 top-3 |
|---|---|---|---|---|---|
| Todas | 117 | 51,3% (42,3–60,2) | **73,5% (64,9–80,7)** | 73,5% | 86,3% |
| Observador sem nenhuma foto no teste principal | 47 | 51,1% (37,2–64,7) | 76,6% (62,8–86,4) | 76,6% | 85,1% |
| Criadas a partir de 1º/12/2025 | 12 | 5/12 | 7/12 | 9/12 | 10/12 |
| Aroeira-do-sertão | 20 | 6/20 (30%) | 17/20 (85%) | 9/20 | 18/20 |
| Mulungu | 68 | 34/68 (50%) | 48/68 (71%) | 49/68 | 55/68 |
| Umburana-de-cambão | 29 | 20/29 (69%) | 21/29 (72%) | 28/29 | 28/29 |

Foto a foto, 26 erradas viraram certas e nenhuma certa virou errada (McNemar exato p < 0,0001).

**Leitura:** o ganho se confirma em fotos que não influenciaram a escolha das referências. Aroeira e mulungu melhoram claramente, e umburana-de-cambão fica praticamente igual. Ressalvas: o n é pequeno; 70 das 117 observações são de observadores que também têm foto no teste principal, embora sejam de observações diferentes; e este teste novo só mede as 3 espécies reforçadas. O efeito colateral nas outras espécies só aparece na tabela anterior. As fotos do teste novo, no geral, são mais difíceis que as do teste principal, que já tinha ficado com as melhores fotos de cada observador.

## Recomendação

O v1.0.1 pode ser publicado como atualização do índice. Os créditos de `referencias_adicionadas.csv` precisam ir junto, e as fotos CC BY-SA podem exigir que a lista de créditos siga a mesma licença. O número a divulgar continua sendo o do v1.0 (88,8 %) até haver uma nova avaliação independente.

## Como refazer

Os scripts ficam em `../scripts/`: `fetch_commons.py`, `melhorar_refs.py`, `avaliar.py metrics`, `comparar_indices.py` e `teste_novo_alvo.py`.
