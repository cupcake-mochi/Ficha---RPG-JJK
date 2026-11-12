# A linha congelada · 12/11/2026

Substitui a regra do nome no registro (`CORRECAO-XP-CONGELADO-NOME-2026-11-12.md`, PR #109).

Depois do #109, o Mizuki pediu para congelar a linha:

> "congelar o xp da linha mesmo, pq alguem pode reescrever o nome e sem querer escrever um pouco diferente, xp vai
> somar"

Ele também confirmou a ordem:

> "a pessoa colocou XP manualmente, as proximas [missões] que ele por, nao congelam, tudo bem. As que ele teve ANTES de
> por o xp manualmente, ai sim congelar"

E pediu cuidado: "deixar claro pra pessoa q apagar após congelar, n muda nada".

## Quando congela

1. A pessoa anota as missões no painel da FICHA PESSOAL.
2. Ela digita o XP total na caixa de XP da FICHA (`FICHA!AN11`, `r53LivreXp_`).
3. Nessa hora, cada missão do painel que tem XP ganha `[XP congelado: x · id]` na nota. A base do XP (`DADOS!CZ54`) é
   acertada para o total ser o número digitado.
4. As missões anotadas depois são normais: somam e, apagadas, o XP desce.
5. Digitar o XP de novo congela o que estiver no painel naquela hora.

## O problema do #109

O #109 reconhecia a mesma missão pelo nome do registro, sem diferença de maiúscula, espaço e acento. Mas uma letra
trocada ou outra palavra contava como missão nova, e o XP somava de novo.

## A regra agora

Nada na linha congelada descongela: nem o mesmo nome, nem o nome com erro, nem outra missão, nem outro tipo, nem a caixa
vazia.
- **O XP total não mexe.** O que muda no XP da caixa volta para a base.
- **A marca acompanha o XP da caixa.** Fica com 0 na caixa vazia e passa para o id do salário da missão que está nela.
- **Missão nova vai numa linha vazia.**
- **Para liberar uma linha:** com a caixa vazia, digite o XP de novo (o `r53LivreXp_` tira a marca das caixas sem XP),
  ou apague a marca da nota.

Fica de pé o que já valia:
- **Missão comum apagada:** o XP desce o valor dela. O nível não desce, porque a subida pelo painel só sobe.
- **Missão congelada apagada:** o XP não desce, porque o XP digitado já contava com ela.

**Ajuda da caixa de XP** (`Codigo.gs`, chave `xp`). Ela já dizia que mudar ou apagar uma missão congelada não mexe no
XP. Agora diz também que uma missão nova escrita por cima de uma linha congelada não conta, e que as novas vão numa linha
vazia.

## Onde mudou

| arquivo | o quê |
|---|---|
| `apps-script/Salarios.gs` | `salarioXpCongelado_`: sai o descongelamento por nome diferente e sai o `salarioMesmoNome_`; o `map` fica na assinatura, sem uso |
| `apps-script/Codigo.gs` | a ajuda da caixa de XP |
| `r53/diagnostico-android/preparar_xp_linha_congelada.js` e `xp_linha_congelada_salario.json` | o preparador (dois pares, depois do `preparar_xp_congelado_nome.js`) e o trecho para o console do editor |
| `r53/testes/xp_linha_congelada.js` (novo, no smoke) | o preparador e o trecho: ida e volta, recusa de repetir e de código divergente, e um editor de mentira |
| `r53/testes/xp_congelado_nome.js` | parte do salário sem a linha congelada |
| `r53/testes/xp_atualizar.js` | os casos novos (abaixo); 107 checks |
| `missoes_enxutas.js`, `missoes_sem_registros.js`, `salario_lote.js` | a cadeia ganhou o preparador novo no fim |

**Casos no `xp_atualizar.js`**, com o total travado em 1000 depois do XP digitado:
- **Mantidos do #109:** o mesmo nome com variação, e apagar e redigitar nome e tipo nas duas ordens. O total não mexe.
- **Erro de digitação:** "Missao B." no lugar de "Missão B". O total não mexe.
- **Outra missão:** "Missão D", Curta, na linha congelada. O total não mexe, a marca fica com 50 e o nível não sobe.
- **Liberar a linha:** com a caixa vazia e a marca apagada, a "Missão D" conta inteira (1050).
- **Nome novo sem apagar o tipo:** na linha congelada, também não conta.

**Smoke completo:** saída 0.

## Instalação nas QAs

O Codigo instalado das duas recebeu o trecho de `node r53/diagnostico-android/preparar_xp_linha_congelada.js`. Foi
salvo, o editor foi recarregado e o hash conferido.

| QA | antes | depois |
|---|---|---|
| Era (`1LBZOf9v…`) | `b5861c145394` | `4f6600227cd1` |
| Ciclo (`1HQqGOVG…`) | `6ecbe5931682` | `4f6600227cd1` |

A Era ainda não tinha os pendentes do #108 e do #109 no Codigo, então recebeu, em ordem:
1. o corte de 25 nos moldes (`preparar_corte_xp_missao.js`, 292 moldes);
2. o nome no registro (`preparar_xp_congelado_nome.js`);
3. a linha congelada.

Depois dos dois primeiros, o hash ficou igual ao do Ciclo (`6ecbe5931682`), que já tinha os dois.

A ajuda da caixa de XP não entrou nas QAs: a caixa não tem nota nelas, e o texto mora no módulo compactado. Entra na
próxima montagem.

## Ensaio no Ciclo (entradas repostas)

O Ciclo partiu do nível 2, com XP 0 e o painel vazio.

| passo | XP | nível | com o #109 |
|---|---|---|---|
| "Ensaio linha", Longa, na AW15 | 200 | 3 | 200 |
| 500 digitado na caixa de XP: a missão congela com 200, base 300 | 500 | 4 | 500 |
| nome apagado e reescrito com erro ("Ensaio linah"): id novo, a marca vai junto | **500** | 4 | 700 |
| missão nova numa linha vazia ("Ensaio nova", Curta, BC15): soma e não congela | 550 | 4 | 750 |

**Reposição** pela API, que não dispara o onEdit:
- AW15:AX15 e BC15:BD15 limpas, com as notas;
- as três linhas novas do `DADOS_SALARIOS` limpas;
- `DADOS!CZ54` = 0 e `FICHA!AH11` = 2.

O nível voltou a 2 e o XP a 0.

**A Era não foi usada no ensaio.** O painel dela tinha as missões "Ensaio A" (congelada) e "Ensaio D", com o XP em 4100
e a base em 3850. Os registros "Ensaio A" a "D" estão no `DADOS_SALARIOS`. É o ensaio do #109, de outra sessão, e não
foi reposto. Fica para quem fez repor, ou para o Mizuki liberar. O estado de partida era nível 10, XP 3700, painel vazio
e só a linha 2 no `DADOS_SALARIOS`.

## Fora deste conserto

- **Oficiais:** nada foi aplicado. Para elas faltam os três trechos, na ordem acima: o corte, o nome e a linha.
- **O aviso na nota da missão:** a nota da missão mostra só `[XP congelado: x · id]`. Pôr uma frase ali pede mexer no
  atalho (`r53/atalho_livre.js`, que gera o `atalho_livre.gs`) e no salário juntos, e ficou de fora.
