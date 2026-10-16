# B47 — capacidade e desempenho local · 16/10/2026

Implementação de A e otimização local de B, partindo de
`4187df37640b5e0966cdb342f56f9ee0a0daf16a`, no ramo
`codex/b47-capacidade`. Integração autorizada em `codex/configuracao-b47`.
O SHA publicado fica no [registro de publicação](PUBLICACAO.md); os hashes das
fontes testadas estão em [VALIDACAO.json](VALIDACAO.json).
**A+B ainda não estão concluídas nativamente.** Não houve escrita Google.

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
| `.gs` / soma de bytes | 23 / 9.543.357 | 20 / 5.670.234 |
| Maior `.gs` | 843.661 bytes | 816.318 bytes |
| XLSX da calculadora local | 3.763.979 bytes | 1.681.232 bytes |
| Geração integral local | 101,7 s | 38,1 s |
| Carregamento em VM Node, mediana de 5 contextos novos | 9.663,7 ms | 233,1 ms |
| CPU do gatilho de texto em VM, mediana de 100 amostras | 4,07 ms | 0,28 ms |

Depois apenas de A, a mediana de carregamento era 735,3 ms. B passou a selecionar
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
- Progressão: 47 verificações, incluindo dez cenários calculados de Caminho/
  Trilha, vida, PE, treinos, duplicatas, negativos e trocar por zero.
- Famílias/autonomia: 20 verificações, incluindo 13 cenários calculados e
  independência entre entidades; Calc agora recebe as tabelas compartilhadas
  atuais e abre até três cenários por processo.
- Perícias/Ofícios: seis verificações em três cenários, primeira/décima vaga,
  atributos, pools, tipo incorreto colado, duplicata e curingas literais.
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

Não foram executados a bateria integral de `rodar-tudo.sh`, os cenários mecânicos
completos históricos de campanha/custom nem a auditoria integral de D. A
limitação histórica de FILTER no Calc não foi convertida em teste aprovado.
O roteiro agregado novo está disponível; esta rodada executou e conferiu seus
componentes, com logs separados, em vez de repetir toda a bateria após os verdes.

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

O conector confirmou conta Google e leitura real da revisão
`1EdEXzFRL8n21dLb60lxE2wbP4PFxFUiBdw7BiTTkNg0`. Metadados e campos crus dos
quatro catálogos foram lidos: nenhum dado fora dos padrões vazios. Isso não é
snapshot integral nem deve ser reutilizado para uma aplicação posterior.

Esta sessão não oferece ferramenta de leitura/atualização/execução Apps Script
ou navegador conectado, nem configuração de CLI Apps Script observável. Isso
não é uma negativa de autorização da conta. Sem salvar/reler o código, a revisão
não foi migrada: o gatilho antigo usaria a geometria anterior. Seguir o
[roteiro nativo](ROTEIRO-NATIVO.md) com nova leitura integral e descartável.
O [manifesto](manifesto-gs.json) identifica os 20 arquivos e os três que devem ser
retirados do projeto. Nunca importar o XLSX. Oficial, bot e acessos intactos.

## Integração e próxima ação

As consultas ao remoto mostraram somente `main` e `codex/configuracao-b47`, ainda
na base, sem commits/relatórios de `claude/b47-revisao` ou `codex/b47-infra`.
Não houve revisão independente ou integração fictícia dessas frentes. Receber
os SHAs, examinar diffs e guardas, integrar uma frente por vez e testar a
combinação antes de republicar. A integração desta implementação própria fica
registrada em [PUBLICACAO.md](PUBLICACAO.md).

B local tem o gargalo de recomposição reduzido. Envio oficial, persistência,
validação e medição nativas ainda dependem das ferramentas apropriadas. Como
hipótese de planejamento: 1–3 h para essa parte de A+B com acesso funcional e
relatórios disponíveis, mais 8–14 h para C/D; cerca de 9–17 h restantes, centro
13 h, sem contar espera por acesso/revisão externa. Rever após medir o Sheets.
C/D não foram iniciadas nesta entrega.

Recomendação para a próxima ação: **GPT-6.1 Sol, High**, para revisar as frentes
e executar a migração/testes nativos preservando entradas e contrato.
