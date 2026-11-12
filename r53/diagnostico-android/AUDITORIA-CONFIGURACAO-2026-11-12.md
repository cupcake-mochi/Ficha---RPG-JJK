# CONFIGURAÇÃO contra o R66 · 12/11/2026

Item 3 do `PROMPT-CONTINUAR-2026-11-12.md`, o próximo do pente fino depois de Progressão e XP. O livro de referência é o
**R66**: `cupcake-mochi/JJK---Project@e3058ad29180fdec2efec75b512446c49bf87b3d`, arquivo
`sistema/05-material/livro/ciclo-maldito-r41/LIVRO-COMPLETO.md`.

**R67.** No mesmo dia saiu a R67 (`d11e4f3088e8`, v0.378). Ela muda 30 linhas do livro, todas na Técnica Máxima, e mais
uma no capítulo Mestrar. Nada disso cai na CONFIGURAÇÃO, então a auditoria vale para as duas.

## O que foi olhado

A aba tem quatro partes com número de livro: as regras de campanha, o custo de XP por nível, a vida rolada e as Famílias
das invocações e da técnica. A leitura foi pela API do Sheets na QA da Era (`1LBZOf9v…`), mais o gerador
(`ficha-v01/campanha.py`, `ficha-v01/familias_invocacao.py`, `ficha-v01/custom_progressao.py`).

Ficou de fora, de propósito:
- **BÔNUS E MUDANÇAS:** os 30 efeitos não têm número de livro. O mecanismo foi ensaiado na B47 (`TESTE-CONFIGURACAO.md`).
- **Cadastros custom** (listas 01 a 13): são conteúdo do mestre. Os níveis dos cartões custom foram conferidos (abaixo).
- **14 · EMISSÃO E SALÁRIOS e PESO DAS MISSÕES:** mexem na Carteira (PR31). As missões Solo já são regra da casa
  registrada (`fora_do_livro.missoes_solo`).

## O que bate com o R66

| o quê | onde na ficha | no livro | resultado |
|---|---|---|---|
| nível inicial 2; o nível 1 é opção de campanha e a curva começa no 2 | `CONFIGURAÇÃO!E46`, nota "informe o custo 1→2" | Criar um personagem; Progressão | igual |
| 9 pontos de atributo, de 0 a 3 na criação | E47, E48 | Criar um personagem, "Atributos" | igual |
| teto 6 na progressão | E49 | Progressão, "Marcos": "O máximo de cada atributo é 6" | igual |
| 9 perícias e 2 ofícios, ou 10 perícias sem ofícios | E50:E52 | Criar um personagem, "Perícias" | igual |
| deslocamento 9 m | E53 | Regras gerais, "normalmente 9 m" | igual |
| Morrendo: Aguentar 1/4, Insistir 1/3 e depois 1/2, teto 15 × Classe | E54:E57 | Dano e recuperação, tabela de Morrendo | igual |
| prazo de 3 rodadas, menos 1 por Sequela; com 3, Derrotado na hora | E58 e a conta `MAX(0;prazo−Sequelas)` | "A janela começa com 3 rodadas" | igual |
| custo de XP do nível 2 ao 29; o 30 sem custo | E66:E94 e `DADOS_CONFIG!W:Z` | Progressão, "Subir de nível" | igual (acumulado 0 … 30700) |
| dado da vida rolada: Bastião d12, Vanguarda e Guia d8, Emanador, Evocador e Incursor d6 | `DADOS_PROGRESSAO!T2:T7` e `DADOS_CONFIG!AH:AI` | linha "Dado de vida, na variante" de cada Caminho | igual |
| vida inicial e ganho por nível (12/7, 8/5, 8/5, 6/4, 6/4, 6/4), PE por nível (4, 5, 5, 6, 6, 6) e perícias fixas | `DADOS_PROGRESSAO!M2:S7`, igual à `DADOS!N5:U10` | quadro de cada Caminho | igual |
| vida rolada: o 1º nível fixo, os seguintes com o dado e a Constituição somada | `DADOS_CONFIG!AF2:AF31` | "role o dado do Caminho a cada nível em vez do valor fixo, somando Constituição normalmente" | igual |
| Famílias da entidade: 3 abertas e 1 Livre; Parceria e Múltiplas 4 e 1; Principal 5 e 2 | `CONFIGURAÇÃO!H139:H144` | Construir invocações; Repertório de Parceria; Famílias do Conjunto; Repertório Ampliado | igual |
| Famílias da técnica: 2 Livres, 3 Fechadas, 4 neutras, 9 no total | H157:H160 | Fundamento, "duas Famílias Livres e três Fechadas" | igual |
| níveis dos cartões custom: Caminho 2, 7, 15, 23, 30; Trilha 2, 11, 19, 27 | `custom_progressao.NIVEIS` | entradas de cada Caminho e Trilha | igual |

## Ensaio no Sheets (QA do Ciclo, entradas repostas)

O ensaio confere o exemplo da Kaori no livro: Bastião com Constituição 2 começa no nível 2 com **14 + 9 = 23** de vida.
O Ciclo partiu do nível 2, sem Caminho e com CON 0. A escrita foi pela API, que não dispara o onEdit. O Buff/Debuff de
vida da QA (`FICHA!P26`) já estava em 24 e ficou ligado, então todo resultado tem +24.

| passo | vida máxima (`FICHA!J26`) | conta |
|---|---|---|
| Bastião e CON 2, vida fixa | 47 | 23 + 24 |
| vida rolada "Sim" e 7 no nível 2 | 47 | (12 + 2) + (7 + 2) + 24; o registro mostra d12, 14 e 9 |
| 12 no nível 2 | 52 | (12 + 2) + (12 + 2) + 24 |
| 13 no nível 2, acima do d12 | #N/A | o aviso "Confira as rolagens da vida" aparece na `CONFIGURAÇÃO!C130` |

Com a vida rolada ligada, a conta entra pelas mesmas camadas da vida fixa: o Casco, o Corpo Quebradiço, os efeitos de
BÔNUS E MUDANÇAS e o Buff/Debuff. Isso foi conferido na fórmula instalada.

**Reposição:** `FICHA!D11` = "Escolha seu Caminho", `FICHA!T21` = 0 e `CONFIGURAÇÃO!F59` e `F101` vazias. Conferido
depois: vida máxima 24, regra em uso "Não", nenhum aviso.

## Achados

Nenhum número da CONFIGURAÇÃO diverge do R66. Os achados são de texto e de nome, e todos esperam a decisão do Mizuki.

### 1. As notas citam o R51

Os números já são os do R66, mas as notas ainda dizem R51:
- "Valor padrão do livro R51.", no cabeçalho LIVRO das três grades (E45, E64 e E99);
- "Regra da campanha. Campo vazio usa o valor do R51.", em 11 das 14 regras.

O texto vem do `ficha-v01/campanha.py` (`cab()` e a nota padrão). A proposta é tirar a versão: "Valor padrão do livro."
e "Campo vazio usa o valor do livro.". Assim a nota não envelhece a cada revisão. Entra na decisão sobre a redação do
R66 na ficha.

### 2. "Não autônoma" fora do livro e com nome que o livro já usa

O ganho da Não autônoma (+1 Família Livre, que conta como uma aberta nova, e a ordem prévia para agir) está marcado na
nota como "regra do sistema prevista para o Guia de Criação; ainda não abordada no livro". Dois pontos:
- **Não está no catálogo.** A chave `fora_do_livro` guarda as regras da casa (Solo, adicionais, corte de 25), mas não
  esta. Ela vive só no `familias_invocacao.py`.
- **O R66 usa o mesmo nome para outra coisa.** Em "Cura e reparo": "Um corpo não autônomo não tem alma e é imune ao
  dano de Alma". Nos corpos amaldiçoados, autônomo quer dizer com alma. Quem marcar "Não autônoma" num corpo sem alma,
  seguindo o livro, ganha a Família Livre e a ordem prévia, e a ficha não registra a imunidade a Alma.

Precisa de decisão: trocar o nome do campo da ficha, registrar a regra em `fora_do_livro`, ou as duas coisas.

### 3. As notas da vida rolada parecem se contradizer

| onde | texto |
|---|---|
| regra "Vida rolada" (E59) | "Cada nível seguinte guarda o resultado do dado, sem Constituição" |
| título do registro (C98) | "Registre o resultado do dado nos níveis seguintes; Constituição entra normalmente." |
| caixa ROLAGEM (F101:F129) | "Resultado guardado, sem Constituição." |

As três estão certas: a pessoa anota só o dado, e a ficha soma a Constituição. Mas, lidas juntas, parecem dizer coisas
opostas. Proposta de texto: "Anote só o dado; a ficha soma a Constituição." Mudança só de texto, no `campanha.py`.

### 4. Buff/Debuff de vida em 24 nas duas QAs

As duas QAs têm `FICHA!P26` = 24. Isso não está no estado de partida do `PROMPT-CONTINUAR-2026-11-12.md`. Parece sobra
de um ensaio de outra sessão. Não mexi: a vida máxima das duas está 24 acima do que o Caminho daria.

## Fora desta auditoria

Esta auditoria não mudou a ficha, as QAs (o ensaio foi reposto) nem as oficiais. Os achados 1 a 3 esperam a decisão do
Mizuki. O achado 4 espera ele dizer se o 24 deve ficar.
