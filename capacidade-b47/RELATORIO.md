# B47 — capacidade e desempenho local · 16/10/2026

Implementação de A e otimização local de B, partindo de
`4187df37640b5e0966cdb342f56f9ee0a0daf16a`, no ramo
`codex/b47-capacidade`. Integração autorizada em `codex/configuracao-b47`.
O SHA publicado fica no [registro de publicação](PUBLICACAO.md); os hashes das
fontes testadas estão em [VALIDACAO.json](VALIDACAO.json).
**A+B ainda não estão concluídas nativamente.** Depois do fechamento local,
a retomada criou backup e aplicou a redução somente numa cópia descartável:
102 lotes confirmados, ANALISE 10 e zero erros nos intervalos afetados de 11
abas. Código vinculado, visual e medidas Apps Script seguem pendentes;
a revisão original continua em formato 9. O estado vigente está no
[relatório nativo parcial](NATIVO-PARCIAL.md) e na
[prova parcial](VALIDACAO-NATIVA-PARCIAL.json). As medidas locais abaixo
permanecem as do fechamento em f3a3fbd; os `.gs` não mudaram nesta retomada.

## Resultado

Capacidades centralizadas em `ficha-v01/capacidades.py`: 10 Famílias, 30
Melhorias, 30 Restrições, 10 Perícias e 10 Ofícios, compartilhados pelo personagem
e pelas 12 invocações. Livro, 25 cartões 3a, Caminho/Trilha, orçamentos e 108
posições de Família permanecem. Os cartões mantêm o desenho aprovado; a área de
cadastro foi compactada, sem iniciar C/D ou unificar/redesenhar a interface.

ANALISE 10 tem 7.356 chaves: 7.236 retidas, 11.712 descontinuadas e 120 novas.
Perícias/Ofícios têm namespaces próprios. Não há reciclagem silenciosa das
chaves `custom.treino.*`. Fontes e avisos acompanham os novos endereços.
Contrato completo em [ESQUEMA-ANALISE](../ESQUEMA-ANALISE.md).

A migração offline verifica snapshot recente e cobertura inclusive das caudas
da grade nativa. Preserva campos/notas por mapeamento explícito e bloqueia vagas
retiradas preenchidas, registros parciais sem tipo, excesso de um tipo, conteúdo
avulso, nota fora de campo e fórmulas de entrada movidas. A revisão exige prova
descartável do mesmo alvo; a oficial é recusada. `lotes.py` produz pedidos REST
sem rede, sem construir/apagar abas ou mexer nos campos anteriores; remove
reservas só depois de atualizar os consumidores. O cache CB2:CC10 é preservado.

## Medidas

Execução Linux em nuvem, Python 3.12.14, Node 24.19.0, Calc pelo executável
`soffice`; dependências Python fixadas na instalação. Memória disponível no
cgroup: 16 GiB. Gerações e cálculos pesados foram executados em série. O pico
observado nos cálculos locais ficou em aproximadamente 3,4 GiB. Não foi usado
nenhum arquivo/sessão do PC anterior.

| Medida local | Base v9 | Depois de A+B |
|---|---:|---:|
| Cadastros dos cinco grupos | 1.633 | 90 |
| Linhas de CONFIGURAÇÃO no gerador | 18.659 | 1.731 |
| Fórmulas de CONFIGURAÇÃO | 2.264 | 610 |
| Menus de CONFIGURAÇÃO | 5.156 | 495 |
| Notas de CONFIGURAÇÃO | 28.538 | 2.490 |
| Grupos de expansão de texto em CONFIGURAÇÃO | 1.219 | 66 |
| Chaves de ANALISE | 18.948 | 7.356 |
| `.gs` / soma de bytes | 23 / 9.543.357 | 20 / 5.682.399 |
| Maior `.gs` | 843.661 bytes | 816.380 bytes |
| XLSX da calculadora local | 3.763.979 bytes | 1.681.795 bytes |
| Geração integral local | 101,7 s | 37,2 s |
| Carregamento em VM Node, mediana de 5 contextos novos | 9.663,7 ms | 327,2 ms |
| CPU do gatilho de texto em VM, mediana de 100 amostras | 4,07 ms | 0,28 ms |

Depois apenas de A, a mediana de carregamento era 735,3 ms; antes das guardas
de geração, B media 233,1 ms. As amostras da combinação final ficam em
VALIDACAO.json. A geração final foi cronometrada no roteiro focal (37,2 s),
com selos e auxiliares incluídos; a medição intermediária era 38,1 s. B passou a selecionar
a origem de cada molde antes de percorrer seus destinos e a analisar as notas
uma vez, preservando valores, bordas, menus e exceções. Compactação Python/JS,
idempotência e carregamento em várias ordens passaram depois da mudança.
O gatilho continua lendo os quatro limites de Range uma única vez por edição.

Tempos de VM medem CPU/compilação locais, sem serviços Google. Os tempos de
carregamento/edição nativos, envio/salvamento e `construir()` nativo **não foram
medidos**. Não projetar a queda percentual da VM sobre o tempo real do Sheets.

## Validação executada

[VALIDACAO.json](VALIDACAO.json) contém resultados pequenos e medidas; modelos,
logs volumosos, venv e snapshots sintéticos ficam na saída ignorada.

- Instalação e smoke documentados executados antes das alterações; smoke final
  repetido após preparar a retirada dos três fragmentos no índice Git.
- Capacidade/contrato: 13 verificações, incluindo retirada exata de chaves,
  primeira/última capacidade, fontes das nove Famílias e referências fora da grade.
- Migração: 19 verificações **sintéticas**, com modelos reais v9/v10, campos e
  notas preenchidos, slots 130/131, perda/excesso, cauda nativa, destinos e lotes.
- Peças: 54 verificações mecânicas, com herança, nomes literais, inválidos,
  Classe 0, última vaga e independência/desconto de Família.
- Progressão: 51 verificações, incluindo dez cenários calculados de Caminho/
  Trilha, vida, PE, treinos, duplicatas, negativos e trocar por zero.
- Famílias/autonomia: 20 verificações, incluindo 13 cenários calculados e
  independência entre entidades; Calc agora recebe as tabelas compartilhadas
  atuais e abre até três cenários por processo.
- Perícias/Ofícios: sete verificações em quatro cenários, primeira/décima vaga,
  atributos, pools, tipo incorreto colado, duplicata, curingas literais e tipo
  apagado em cartão vazio.
- Compactação: 20 abas/fixtures; construção simulada completa em três fases:
  185 verificações, com ordens de carga e arquivos ausentes.
- Texto: sete cenários de altura compartilhada e limpeza, quatro leituras dos
  limites por edição. A última Restrição agora é a vaga direita, mais estreita;
  o mesmo texto exige 81 px, contra 68 px da antiga vaga esquerda 395.
- Leitor: `TESTE: OK`, formato 10; só o aviso esperado da ficha vazia sem escolhas
  suficientes de Perícia/Ofício.
- Campanha/custom: quatro e doze verificações **estruturais**. Os contratos
  congelados v3/v4 continuam sendo exigidos, reconhecendo somente as alterações
  exatas já aprovadas no formato 7 (nove Famílias e respiro da Definição).

A revisão posterior mostrou que o `TESTE: OK` antigo do leitor verificava a
forma do contrato, mas ignorava erros de fórmula e certos avisos custom. Isso
limitava a declaração inicial. O leitor agora reprova qualquer erro exportado e
qualquer aviso custom; preserva nomes textuais como `007` e `VERDADEIRO`. O
recálculo local também qualifica IFS/SWITCH/TEXTJOIN no namespace XLSX. A execução
final voltou a mostrar só o aviso esperado, com checagem explícita de erros.

Para eliminar os 25 `#NAME?` das validações básicas 3a, o gerador divide cada
expressão em três auxiliares ocultas, sem alterar ordem/mensagens/regras. Maior
expressão: 5.031 caracteres (antes 11.211), colunas DADOS_CUSTOM 284 → 287. A
migração cresce essa grade antes de escrever. Cinco verificações em Calc
cobrem os 25 vazios, oito moldes válidos, colisão com livro e número inválido.

Não foram executados a bateria integral de `rodar-tudo.sh`, os cenários mecânicos
completos históricos de campanha/custom nem a auditoria integral de D. A
limitação histórica de FILTER no Calc não foi convertida em teste aprovado.
O roteiro focal ampliado executou suas 23 etapas. Passaram 22 na execução
agregada; a comparação histórica de Progressão exigiu reconhecer a fatoração
U2:U26 → JY:KA. Ela agora recompõe cada fórmula congelada inteira, exigindo
guarda, condições, mensagens e ordem idênticas, com contraprovas de alterações.
Progressão foi reexecutada integralmente e passou. Nenhum código de produção
mudou entre esses dois checkpoints. O JSON preserva o resultado bruto e a
reexecução, em vez de apagar a falha inicial.

Reprodução do roteiro focal: `bash rodar-tudo.sh --b47-focal`. A exportação v9
usa `4187df3` em worktree temporário e o mesmo Python instalado; o temporário é
removido sem alterar a árvore atual. Para medidas: `medir-carregamento.js`,
`medir-edicao.js` e `exportar-base.py --medir-geracao`, todos nesta pasta.

## Visual e Google

As [seis prévias](previas/) foram inspecionadas: primeiras/últimas vagas e
transições de seção, bordas, títulos, menus e caixas de seleção. São
**rasterizações locais dos metadados**, com Oswald do repositório e DejaVu Sans
substituindo Roboto; campos calculados ficam vazios. Não são capturas do navegador
nem do Google. `previas.py --png` as reproduz. O Chromium da nuvem recusou
navegação `file://` com `ERR_BLOCKED_BY_ADMINISTRATOR`; não se contornou a política.
A conferência visual nativa e textos preenchidos no Sheets permanecem pendentes.

No fechamento local f3a3fbd, o conector confirmou conta Google e leitura real da revisão
`1EdEXzFRL8n21dLb60lxE2wbP4PFxFUiBdw7BiTTkNg0`. Metadados e campos crus dos
quatro catálogos foram lidos: nenhum dado fora dos padrões vazios. Isso não é
snapshot integral nem deve ser reutilizado para uma aplicação posterior.
A retomada posterior obteve leituras integrais novas das faixas alteradas e
validou a migração Sheets na descartável; ver NATIVO-PARCIAL.md.

Esta sessão não oferece ferramenta de leitura/atualização/execução Apps Script
ou navegador conectado, nem configuração de CLI Apps Script observável.
A consulta separada ao Codex Document Control também retornou zero sessões
Sheets conectadas. Isso
não é uma negativa de autorização da conta. Sem salvar/reler o código, a revisão
não foi migrada: o gatilho antigo usaria a geometria anterior. Seguir o
[roteiro nativo](ROTEIRO-NATIVO.md) com nova leitura integral e descartável.
O [manifesto](manifesto-gs.json) identifica os 20 arquivos e os três que devem ser
retirados do projeto. Nunca importar o XLSX. Oficial, bot e acessos intactos.

## Integração e próxima ação

A listagem inicial de referências locais era incompleta: o clone só buscava
`main`. A consulta completa `git ls-remote --heads origin` encontrou as frentes.
Foram revisados e incorporados por merges separados:

- infraestrutura `b8ab7b56aac71ad0c85d0a3cff0c94d026062189` (cinco commits desde a
  base; só `infra-b47/`), com 15 testes próprios reproduzidos;
- revisão `287b2c1408c893c20a003cd6caa6241504336f02`, publicada no ramo alternativo
  `claude/kind-feynman-sewhec` (cinco commits; só `revisao-b47/`). O ramo lógico
  `claude/b47-revisao` ainda estava na base. Os ramos históricos de outros temas
  não foram integrados.

A1 foi resolvido com selos em abas/complementos, lista de complementos esperados,
remoção das sobras pelo emissor e recusa de projetos mistos antes de tocar Sheets.
A1/I1/I2 também têm validação no empacotador e `--remover` explícito: oito casos
com snapshot remoto sintético, manifesto/HTML preservados. Cinco contraprovas de
carregamento usam arquivos v9 antigos antes/depois dos novos, sem contaminar as
7.356 chaves. A2/B1 foram resolvidos no leitor; B3, nas validações auxiliares.
M2/M3/M4/M5 já estavam tratados na redução/guarda e receberam os testes externos.

O perfil `b47-v10` descreve o contrato real (cinco campos por Perícia/Ofício).
As sondas de leitor e endereços aceitam o modelo atual sem gerar outra cópia; a
de avisos percorre as novas auxiliares. Contrato, leitor e endereços externos
passaram no alvo real. Restam dois avisos informativos: os endereços de INDIRECT
continuam em texto, mas derivados e dentro da faixa, e avisos históricos usam
prefixos diferentes de ⚠, agora tratados pela chave. Não são validação nativa.
A atualização externa revisou A (`2f3c62f`/`4610c88`) e reproduziu
independentemente suas 14 etapas focais, além de confirmar os 20 `.gs` byte a
byte. O integrador testou as correções no alvo real e a combinação posterior.
Não houve nova auditoria independente dessa combinação final. A atualização
`287b2c1` acrescentou uma combinação simulada de A + infra + patches (anterior
a esta integração), sem alterar produção. Seu teste histórico compila; o
pacote atual foi validado pelos oito casos de `testar-envio.py`. O manifesto
da infra foi regenerado e comparado ao atual: mesmos 20 nomes, tamanhos e
hashes. `MANIFESTO-BASE.json` permanece v9 histórico, explicitado no README
com link ao manifesto atual; não é o pacote de envio.

Achados posteriores R1/R2 correspondem às correções de geração/leitor descritas
acima. R3 ganhou tabela histórica de formatos e registro da variante paralela;
o reconhecimento do formato 10 no bot fica explicitamente pendente, fora desta
rodada. R4 ganhou procedimento de interrupção/recuperação e aviso de lotes não
atômicos. R5 foi corrigido: cartão vazio aceita tipo vazio e repetição não é
avaliada com nome vazio; a contraprova encontrou um parêntese incorreto na
primeira tentativa, corrigido antes da publicação. R6 passou a conhecer até
nove fragmentos. A receita antiga `migracao-criacao.py` está sinalizada em NUVEM.

B2 permanece como limitação histórica: nomes contendo o separador ` · ` podem
ser ambíguos nas listas exportadas. Esta rodada preserva o texto cru e não muda
a regra de nomes nem o formato das listas; qualquer mudança exige decisão de
contrato e teste dos consumidores. Não é perda silenciosa por renumeração.

A combinação é publicada somente após seus testes. As origens e SHAs finais
ficam em [PUBLICACAO.md](PUBLICACAO.md). Não houve mensagens automáticas aos chats.

A retomada PC concluiu A+B nativamente: código salvo/relido, construção,
cópia funcional, medidas e migração guardada da revisão. Zero erros/diferenças
em 400.917 células de 17 abas, 509 entradas/notas exatas e 22.094 células
superiores preservadas. Controles nativos demonstraram equivalência da formatação
pela âncora, eliminando repeatCell redundante; 19 testes de migração e sete
contraprovas da otimização passaram. Detalhes e incidentes no
[checkpoint PC](RETOMADA-PC.md), provas conjunta/final e
[PUBLICACAO.md](PUBLICACAO.md). Produção GS f1ff7a6 permanece inalterada.

A antiga hipótese de planejamento (1–3h para o trecho nativo de A+B e 8–14h
para C/D) era uma estimativa de trabalho, sem espera por acesso ou recuperação
de envios. Não é prazo de entrega nem autorização para C/D. C/D não foram
iniciadas e ficam fora deste fechamento. Bot/formato 10 e variante histórica
4 continuam externos; limitações de Calc/fcntl e ausência de baseline nativo
equivalente para percentual de latência estão registradas no checkpoint.

Recomendação para a próxima ação: **GPT-6.1 Sol, High**, para revisar A+B e
seu uso; novo conteúdo/etapa exige nova autorização.
