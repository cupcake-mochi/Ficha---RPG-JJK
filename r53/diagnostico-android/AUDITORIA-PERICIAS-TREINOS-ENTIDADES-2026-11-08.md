# Perícias e treinos das entidades · 08/11/2026

As descartáveis Era e Ciclo reproduziram dois problemas no resumo de
perícias e um descompasso na ajuda do campo Ofício Compatível. Os
modificadores de perícias válidas e dos Testes de Resistência passaram
nos controles da matriz. A auditoria parte de `1eb4965`, com a PR90 em
`4eeb276b3938105f9e33a647e9fa0657a700b4f8`.

## PT01 · Perícia repetida ocupa duas vagas

Selecionar Atletismo, Atletismo, Investigação e Sentir Energia mostra
**PERÍCIAS · 4 DE 4** embora haja apenas três perícias distintas.
Atletismo aparece duas vezes, cada linha com o mesmo bônus. O cabeçalho
fica sem aviso de repetição. Isso pode esconder uma escolha que ainda
falta na montagem.

Reprodução pela matriz em uma entidade de cada cópia e pelo menu nativo
na entidade 1 das duas. No ensaio de interface, `INVOCAÇÕES!O38/O40/O41`
já tinham três perícias diferentes e `O39` estava vazia. Digitar
Atletismo por teclas e confirmar a opção oferecida elevou o resumo de
3/4 para 4/4. A validação estrita da célula permaneceu ativa.

## PT02 · Perícia retirada do catálogo ainda ocupa vaga

Cadastrei a perícia sintética `QA Perícia ~*?` com Constituição e a
selecionei nas duas entidades de teste de cada cópia. Ela apareceu
no catálogo com o nome literal, inclusive os caracteres especiais.
Depois limpei apenas o nome e o atributo do cadastro em
`CONFIGURAÇÃO!BB13/BE14`, preservando as escolhas das entidades.

A opção saiu de `DADOS_PROGRESSAO!AG25:AH25`. O nome gravado continuou
na ficha da entidade, perdeu o bônus e seguiu contado. O resumo
manteve 4/4 ou 7/7, com apenas três ou seis escolhas válidas, e sem
aviso de escolha inválida no cabeçalho. Repor o cadastro trouxe o
bônus original de volta. A remoção e a reposição foram ensaiadas
pela API nativa nas quatro combinações de entidade e cópia. O teste
mede o cabeçalho e o bônus, sem avaliar os avisos que o Google
possa mostrar na própria célula.

Em ambos os achados, `DADOS_INVOC!GU2:GU13` conta textos não vazios
com `COUNTIF(...;"?*")`. `HT2:HT13` sinaliza apenas estouro de
quantidade. O cálculo de bônus consulta o catálogo separadamente e
devolve vazio quando o nome sai dele. Uma correção pode preservar
as escolhas gravadas, contar as válidas distintas e sinalizar
repetições, escolhas sem cadastro e excesso de vagas.

## PT03 · A ajuda do ofício omite o cadastro

A nota de `INVOCAÇÕES!L42` orienta que dá para escrever outro ofício.
O campo `L43` usa uma lista estrita de ofícios do livro e do cadastro
custom. Digitar um nome fora da lista pelo teclado foi recusado nas
duas cópias e deixou a célula vazia. A ajuda precisa indicar o cadastro
em CONFIGURAÇÃO antes de escolher o ofício. Forja funcionou como opção
de catálogo em entidades de criação e não consumiu vaga de perícia.
Esse ensaio é sobre o campo e sua ajuda, sem validar reparos ou a
permissão narrativa de cada entidade para usar o ofício.

## Controles de cálculo

O manual estabelece o total de perícias treinadas em
`4 + piso(Inteligência / 2)`, bônus de atributo e Maestria para perícia
treinada, e apenas um TR com a Maestria do invocador. O Físico escolhe
entre Força e Destreza. Vigor usa Constituição, Intelecto usa
Inteligência e Espírito usa Essência.
[Manual de invocações no commit e3058ad](https://github.com/cupcake-mochi/JJK---Project/blob/e3058ad29180fdec2efec75b512446c49bf87b3d/sistema/05-material/livro/manual/60-invocacoes.md)

As 40 observações de entidade incluem 34 controles aprovados e seis
reproduções de PT01/PT02. As quatro tentativas de interface são uma
rodada separada. Usei as entidades 1 e 12, invertendo as posições da
matriz entre as duas cópias.

- As 23 perícias do catálogo foram exercitadas em cada cópia. O mapa
  de atributos do catálogo vivo coincide com `catalogo-projeto-m.json`.
  Testei modificadores positivos, zero, negativos e uma perícia custom
  ligada à Constituição.
- Inteligência base de 0 a 6 produziu limites 4 a 7 e o excesso válido
  de cinco escolhas sobre quatro foi sinalizado. Buffs de Inteligência
  mudaram o modificador da perícia, enquanto a quantidade continuou
  usando o atributo base. Isso registra o comportamento atual da ficha.
- Os quatro TRs funcionaram com e sem treino, com as duas opções de
  Físico e com buffs e debuffs. Os degraus de Maestria foram conferidos
  nos níveis 9/10, 17/18 e 25/26. Domadas e criadas com nível fixo
  baixo usaram a Maestria do invocador de nível mais alto.

A conferência de armas foi de leitura nas duas cópias. A nota do
equipamento orienta usar o atributo e o dano da arma com desvantagem.
A matriz de cálculo cobriu os modificadores de perícias e TRs.

## Preservação

As 61 entradas do escopo voltaram aos valores originais em cada cópia.
Comparei **86.474 posições por cópia**, incluindo **MONTAGENS inteira
em A1:I9543, 85.887 posições**, e outras 587 no escopo funcional. A
comparação de MONTAGENS cobriu valores digitados, calculados e exibidos,
notas e validações. O escopo funcional incluiu ainda formatos informados
pela API e campos de texto rico. Zero diferenças nos campos comparados
e metadados iguais, incluindo formatação condicional. As duas abas do
navegador usadas para o ensaio foram fechadas.

O ramo de auditoria contém o relatório e a evidência sanitizada
`auditoria_pericias_treinos_entidades_2026-11-08.json`, além do apontador
de retomada. Snapshots, leituras completas e capturas ficaram no
diretório ignorado `nuvem-b47/saidas/auditoria-pericias-entidades-20261108/`.
As escritas Google foram restritas às entradas de teste das duas
descartáveis. A PR31 permaneceu em `765e3b24fb49a1ca8c6fd4cfaf16aa6fa6bad943`.
