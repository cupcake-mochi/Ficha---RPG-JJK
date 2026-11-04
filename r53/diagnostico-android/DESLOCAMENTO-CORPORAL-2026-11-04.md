# Deslocamento dos corpos da Restrição — revisão focal

Ramo separado `codex/deslocamento-corporal-20261104`, baseado na PR51 em
`60a504b98737461a105988ebaca430db4be6a5e6`. Depende do indicador de base corporal
`DADOS_CUSTOM!B126` introduzido naquela PR. Não altera a PR51 nem a PR31.
Nenhuma oficial ou ficha de jogador foi editada e não houve merge.

## Regra e defeito

Conferência da R65 no commit
[`a98d4af981cd7166a403f7189eeb1bc3a22e4ad4`](https://github.com/cupcake-mochi/JJK---Project/blob/a98d4af981cd7166a403f7189eeb1bc3a22e4ad4/sistema/05-material/livro/ciclo-maldito-r41/LIVRO-COMPLETO.md),
seções Corpo Debilitado, Corpo Quebradiço e Corpo Exaurido.

- Debilitado e Quebradiço têm deslocamento próprio de 0 m.
- Exaurido tem limite de 4,5 m em movimento leve no chão. Com vida atual menor
  ou igual à metade do máximo, arredondada para baixo, passa a 0 m. Recuperar
  vida acima desse limite devolve o deslocamento permitido.
- A limitação pertence ao corpo real, sem transferência automática para
  intermediários com atributos próprios.

A fórmula anterior de `FICHA!O67` considerava carga, Exaustão, Buff/Debuff e
CONFIGURAÇÃO, mas não esses corpos. Na cópia nativa, Corpo Exaurido com 3 de
23 PV mostrava **4,5 m**. Após a correção, mostrou **0 m**.

## Alteração

`ficha-v01/configuracao.py` envolve a conta já configurada com os limites
corporais, usando endereços derivados do índice. Não há troca global de
coordenadas. O ramo sem base corporal e o corpo próprio mantêm a conta anterior.
O teto do Exaurido não aumenta um resultado normal que já seja menor ou zero.
A configuração numérica não pode fazer esses corpos ultrapassarem sua limitação.

O reconhecedor `anterior()` aceita somente o envoltório exato, incluindo as duas
ocorrências iguais da conta original. Fórmulas adulteradas não são reconhecidas
como esse envoltório.

A geração GS foi refeita, `4fe598ff94b97c2f`, e o pacote foi reempacotado.
Comparação completa das 26 abas-fonte, desconsiderando apenas o selo `geracao`:
**a única diferença é FICHA!O67**. ANALISE inteira, estilos, notas, validações,
invocações e demais fórmulas permanecem iguais. O pacote conserva 249 contextos.
As muitas linhas de GS alteradas são principalmente os selos da geração comum.

## Testes

`python3 r53/testes/deslocamento_corporal.py --pedidos /tmp/deslocamento-pedidos.json`
confere o envoltório e gera 37 cenários com resultados esperados explícitos.
A fórmula testada é extraída do GS gerado. Somente as referências são trocadas
por tokens para entradas controladas na aba de QA, sem reimplementar a regra.
O script não acessa Google nem escreve em planilhas remotas.

**37/37 cenários recalculados no Google Sheets e aprovados**, incluindo máximos
pares/ímpares, limiar exato, máximo 1/0, movimento menor/zero, meia marcha,
carga, Exaustão, somar/trocar, erros de configuração nos ramos aplicáveis,
corpo próprio e base corporal falsa. Os dois resultados `#N/A` esperados foram
mantidos e testados com `ISNA`, não contados como erros acidentais.

**Quatro mudanças adicionais na aba FICHA da cópia**, usando as fórmulas reais
em `O67` e `DADOS_CUSTOM!B126`:

| Estado | Resultado |
| --- | --- |
| Exaurido, 11 de 23 PV | 0 m |
| Exaurido, 12 de 23 PV | 4,5 m |
| Debilitado, 23 de 23 PV | 0 m |
| Quebradiço, 23 de 23 PV | 0 m |

A cópia de movimento foi criada a partir da QA anterior. Só recebeu as duas
fórmulas acima, as entradas dos cenários e uma aba auxiliar de testes. Não é uma
implantação integral da PR51. Por exemplo, a Defesa exibida nessa cópia ainda
pode vir de um molde anterior. O teste é exclusivamente de deslocamento.
Os valores controlados da vida máxima não testam a redução própria do Quebradiço.

- `node r53/testes/pacote_runtime.js`: aprovado no pacote regenerado.
- `node r53/testes/descanso.js`: 60 cenários aprovados.
- `node r53/testes/pacote_leve.js`: 123 verificações aprovadas.
- `git diff --check`: aprovado.
- Visual do deslocamento na cópia conferido no Google, sem mudança de layout.

O ensaio de tabela controla o booleano da base corporal. Não repete a validação
nativa dos cartões custom feita na PR51. Não houve bateria ampla de toda a ficha,
medição Android nem teste nativo de restauração após apagar a célula calculada.
As entradas integradas foram alteradas pela API, que não dispara `onEdit`.

## Aplicação futura em fichas existentes

Ainda não aplicada. Exige autorização, snapshot atual e conferência do alvo.
Não reconstruir ficha preenchida nem instalar o pacote integral por cima dos
incrementos existentes.

1. Conferir a presença e a fórmula correta de `DADOS_CUSTOM!B126`, vinda da PR51.
2. Aplicar o delta de `FICHA!O67`, conservando formato, nota e validação.
3. Atualizar também o molde de O67 usado pela restauração no código instalado,
   com guarda da fórmula anterior. A troca isolada da célula não basta como
   publicação permanente.
4. Ensaiar a restauração e a mudança de vida na cópia de promoção, reler o código
   salvo e os resultados antes de qualquer aplicação autorizada.

Snapshots, pedidos da cópia e evidências brutas estão fora do Git. Este relatório
é sanitizado. Pendências separadas continuam sendo Bloquear nos corpos, vida
máxima do Quebradiço e outras regras não abrangidas por este delta.

Para revisar: Sol/Medium. Para preparar aplicação integrada: Sol/High, conforme
AGENTS.md. Nenhuma configuração do usuário foi alterada.
