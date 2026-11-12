# Progressão e XP contra o R66 · 12/11/2026

Parte do pente fino de 11/11, depois da auditoria de Caminhos e Trilhas. O livro de referência é o **R66**:
`cupcake-mochi/JJK---Project@e3058ad29180fdec2efec75b512446c49bf87b3d`, arquivo
`sistema/05-material/livro/ciclo-maldito-r41/LIVRO-COMPLETO.md`, capítulo Progressão.

## O que bate com o R66

| o quê | onde na ficha | resultado |
|---|---|---|
| curva de XP, do nível 2 ao 30 | catálogo `progressao`, `DADOS!AQ5:AR33` das duas QAs | igual: 0, 200, 500, 800, 1300 … 30700 |
| XP por tamanho de missão | catálogo `missoes.tamanho`, `DADOS!CL5:CM10` das duas QAs | igual: 50, 100, 200, 300 |
| desconto da semana e falha | `DADOS!CR5:CS15` | igual do 3º ao 7º; a falha vale metade, sozinha ou junto com a posição |
| arredondamento | fórmula do XP de cada missão | igual: só no XP final, para baixo; positivo menor que 1 vira 1 |
| Limiar do nível 20 | `limiar do feito` = 20 | o XP não leva o nível além do 20 sozinho |
| marcos | catálogo `progressao.marcos` | igual: 6, 10, 14, 18, 22, 26 e 30, com +1 ponto de atributo, +1 de Refino e +1 espaço |
| maestria, espaços, Refino, Classe, Classe 0, Integridade | catálogo `progressao.formulas` e `tabela_impressa` | igual nos 30 níveis |
| ponto extra do marco de Corpo | `marcos de Corpo` e os pontos de Corpo por atributo | contado à parte dos pontos comuns |

Fora do livro, de propósito (chave `fora_do_livro` do catálogo, decisão do Mizuki): as missões Solo simples (75) e
Solo complexa (150) e os adicionais da guilda 1,25x, 1,50x e 2x.

## Ensaio no Sheets (QA da Era, entradas repostas)

A QA estava no nível 10 com 3700 de XP e nenhuma missão.

| passo | resultado | o que o livro diz |
|---|---|---|
| 20000 digitado na caixa de XP | nível 20, XP 20000 | sem o feito, para no 20 e guarda o XP |
| 23 digitado no nível, como quem teve o feito reconhecido | nível 23, XP 20000 (1200 guardados no 23) | do 20, com 5700 guardados: 21, 22 e 23 de uma vez, sobram 1200 |

**Reposição.** A base do XP (`DADOS!CZ54` = 3700) e o nível (`FICHA!AH11` = 10) voltaram pela API, que não dispara o
onEdit. A caixa de XP continuou com a fórmula `=DADOS!$CZ$47`, e as contas da `DADOS` voltaram a 3700 e ao nível 10.

## Achados

### 1. A missão pode subir mais de um nível (regra, decisão do Mizuki)

O R66 diz: "Você avança no máximo um nível por missão concluída". A ficha guarda o XP como total acumulado e põe o
nível no maior que cabe nele (`salarioNivelQueSobe_` no `Salarios.gs`; `nivelQueSobe_` no `Codigo.gs`). A conta do XP
é a mesma do livro. O que falta é a trava de um nível por missão.

Sem adicional, isso nunca acontece, porque a maior missão (300) não paga dois níveis seguidos. Com o adicional da
guilda, acontece. Medido com o código real do `Salarios.gs` na ficha de mentira do `xp_atualizar.js`:

| antes | missão | ficha | livro |
|---|---|---|---|
| nível 2, 0 de XP | Final de arco 2x (600) | nível 4 | nível 3, guarda 400 |
| nível 3, 300 de XP | Final de arco 2x (600) | nível 5 | nível 4, guarda 400 |
| nível 2, 0 de XP | Longa 2x (400) | nível 3 | nível 3 |

A diferença é de uma missão: na missão seguinte, o livro chega ao mesmo nível. O conserto seria limitar a subida a
`atual + 1` nas duas funções. O XP digitado à mão e o nível digitado à mão (o feito) continuam livres.

### 2. O desconto da semana para no 7º (decisão do Mizuki)

O livro continua depois do 7º: "Seguintes: metade da parte anterior". O menu de desconto vai do 3º ao 7º, mais as
versões com falha. Do 8º em diante não tem opção: o jogador escolhe o 7º, que paga a mais, ou digita o XP. Entrar o
8º e os seguintes muda o tamanho da tabela `DADOS!CR5:CS15`, e as fórmulas de missão apontam para esse endereço.

### 3. Teste com o Final de arco errado (corrigido)

A ficha de mentira do `r53/testes/xp_atualizar.js` dava 400 de XP ao Final de arco. O livro, o catálogo e a `DADOS`
dizem 300. Era só no teste, a ficha nunca usou esse número. O tipo foi corrigido, e o teste agora compara a tabela de
mentira com o catálogo: com 400, ele quebra.

## Fora desta auditoria

Nada mudou na ficha, nas QAs (o ensaio foi reposto) nem nas oficiais. Os achados 1 e 2 esperam a decisão do Mizuki.
