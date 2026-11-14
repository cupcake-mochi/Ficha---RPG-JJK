# Achados da CONFIGURAÇÃO decididos · 14/11/2026

Fecha os quatro achados abertos da `AUDITORIA-CONFIGURACAO-2026-11-12.md` (#112). Nenhum número de regra mudou: só texto,
um registro no catálogo e o Buff/Debuff de teste das QAs.

## As decisões do Mizuki

| Achado | Decisão | O que mudou |
|---|---|---|
| 1. As notas citam o R51 | Tirar a versão | "Valor padrão do livro." e "Regra da campanha. Campo vazio usa o valor do livro." |
| 2. "Não autônoma" fora do `fora_do_livro` | É regra da casa, vai sair num livro de guias | Nome mantido; regra registrada no catálogo |
| 3. As notas da vida rolada se contradizem | A frase "Anote só o dado; a ficha soma a Constituição." | Três textos reescritos |
| 4. Buff/Debuff de vida em 24 nas QAs | Zerar nas duas | `FICHA!P26` esvaziado nas duas QAs |

Palavras dele sobre o achado 2: "é uma regra da casa, invocações não autonomas funcionam dessa forma, ira vir em uma
atualização de um dos livros de guias". A anotação existe desde 15/10/2026 (`PENDENCIAS.md`, `ESTUDO-CUSTOM-3C.md`,
`TESTE-CONFIGURACAO.md`) e o `NOTA_AUTONOMIA` do `familias_invocacao.py` já a dava como prevista para o Guia de Criação.
O "corpo não autônomo" do livro (Cura e reparo: sem alma, imune ao dano de Alma) é outra coisa; o nome coincide.

## Textos

| Lugar | Antes | Depois |
|---|---|---|
| E45, E64, E99 (nota) | Valor padrão do livro R51. | Valor padrão do livro. |
| F47:F57 (nota, 11) | Regra da campanha. Campo vazio usa o valor do R51. | Regra da campanha. Campo vazio usa o valor do livro. |
| F59 (nota, Vida rolada) | … Cada nível seguinte guarda o resultado do dado, sem Constituição, no registro abaixo. | … Nos níveis seguintes, anote só o dado no registro abaixo; a ficha soma a Constituição. |
| C98 (texto) | … Registre o resultado do dado nos níveis seguintes; Constituição entra normalmente. | … Nos níveis seguintes, anote só o dado; a ficha soma a Constituição. |
| F100:F129 (nota, 30) | Resultado guardado, sem Constituição. Não há sorteio automático. | Anote só o dado; a ficha soma a Constituição. Não há sorteio automático. |

A regra não mudou: o registro guarda o dado puro e a ficha soma a Constituição (o ensaio da Kaori na auditoria
confirma). Só a redação dizia isso de dois jeitos que pareciam opostos.

Arquivos: `ficha-v01/campanha.py` (fonte) e `apps-script/Configuracao.gs` (gerado), trocados por contagem exata
(3 + 11 + 1 + 1 + 30 no `.gs`).

## Catálogo

`catalogo-projeto-m.json`, `fora_do_livro`:

- `invocacao_nao_autonoma`: `familias_livres_adicionais` 1, `ordem_previa` "toda ação, exceto a Reação";
- `invocacao_nao_autonoma_nota`: a origem da regra e a diferença para o corpo não autônomo do livro.

O `conferir-catalogo.py` ganhou uma conferência: o número do catálogo tem de ser o padrão `livres_nao_autonoma` do
`familias_invocacao.py`. Resultado: TUDO VERDE.

## QAs

Nas duas (Era e Ciclo), pela API do Sheets:

- as notas e o texto de C98 da tabela acima;
- `FICHA!P26` vazio. A vida máxima (`FICHA!J26`) caiu de 24 para 0, que era só o bônus (as QAs estão sem Caminho).
  A vida atual (`D26` = 6) não foi mexida.

Lido de volta nas duas: notas novas, C98 novo, P26 vazio, J26 = 0.

## Oficiais

Nada aplicado. Quando o Mizuki der o ok para a rodada das oficiais, entram as notas e o texto de C98 (sem o P26, que
era só das QAs).
