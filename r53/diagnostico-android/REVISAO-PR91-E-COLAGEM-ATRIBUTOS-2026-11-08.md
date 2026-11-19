# PR91 revisada e colagem de atributos reproduzida · 08/11/2026

## Revisão da PR91

Sem bloqueio encontrado no escopo da PR. A PR91 estava aberta e
mergeable no commit `b804d1a45bbdd83c04411b45b3ed30525ba8eb34`,
sobre a PR90 em `4eeb276b3938105f9e33a647e9fa0657a700b4f8`.
As execuções de [pull request](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/42541110669)
e [push](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/42541086468)
passaram nesse commit.

Repeti o teste focal do preparador, incluindo a aplicação, a reversão
e a recusa de fórmulas divergentes em pt_BR e en_US. O comparador
percorreu 280.056 posições em 26 abas e reproduziu o plano versionado
byte a byte. Confirmou 24 fórmulas e uma nota. A releitura inicial
nas duas QAs já correspondia ao plano completo. O preparador emitiu
zero pedidos de aplicação. A matriz de 52 observações pertence à
rodada anterior de implementação.

Na entidade 1 de cada QA, deixei uma perícia repetida e apaguei o
cabeçalho mesclado `INVOCAÇÕES!O37:S37` com Backspace. A barra de
fórmula ficou vazia. A fórmula original voltou sozinha em ambas,
`=DADOS_INVOC!$HT$2`, e tornou a exibir
`⚠ PERÍCIAS · 3 DE 4 · REPETIDA`. O ensaio cobre a recuperação do
cabeçalho visível com o código já instalado nas descartáveis.

## Atributo copiado como texto

A observação da revisão da PR90 foi reproduzida pela colagem nativa
de valores nas duas QAs. É um problema anterior à PR91.

Em uma entidade de nível 1, parti de Força 3, Destreza 3 e
Constituição 0. Em `INVOCAÇÕES!O21`, digitei apóstrofo seguido de 3,
copiei a célula com Ctrl+C e usei Ctrl+Shift+V em `Q20`
(Constituição). Apliquei os mesmos atalhos com 3 numérico como
controle. A origem foi o campo de buff de Força e não participa
dos pontos de Constituição ou dos PV observados.

| Valor relido em Q20 | Constituição efetiva | Pontos gastos | PV máximo |
| --- | ---: | ---: | ---: |
| Texto `3` | 0 | 6 | 5 |
| Número `3` | 3 | 9 | 8 |

O texto ficou gravado nas duas planilhas. A validação estrita
continuou ativa e a fórmula de normalização com `N()` devolveu
zero. A colagem com o número devolveu o resultado esperado. A
digitação direta no campo de pontos continua sendo um caminho
distinto, que a revisão anterior viu ser bloqueado para texto.

O próximo item é corrigir o tratamento dos pontos colados como
texto. O caso comprovado é o de um dígito válido gravado como texto.
Os ensaios não estendem essa conclusão a negativos, frações ou
valores acima de seis. A correção deverá preservar as escolhas
gravadas e a validação do menu.

## Preservação

As entradas sintéticas e os formatos numéricos que mudaram no
ensaio foram restaurados. Cada cópia teve 22 posições no cenário,
com dez valores e dois formatos efetivamente repostos.
A comparação final cobriu 86.494 posições por cópia, incluindo
MONTAGENS inteira `A1:I9543`. Zero diferenças nos campos comparados
e metadados iguais, incluindo formatação condicional. As abas
de teste foram fechadas.

Ramo `codex/revisao-pr91-fila-20261108`, apenas revisão e evidência.
Dados sanitizados em `revisao_pr91_colagem_atributos_2026-11-08.json`.
Snapshots e capturas em
`nuvem-b47/saidas/revisao-pr91-fila-20261108/`, ignorado pelo Git.
As escritas Google desta rodada se limitaram às duas descartáveis.
