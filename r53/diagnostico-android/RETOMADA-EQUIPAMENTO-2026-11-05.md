# Pausa solicitada pelo usuário — equipamento

PR64 em rascunho, ramo `codex/correcao-equipamento-20261104`, base PR63.
Implementação publicada no commit `a8c9bdc`. Sem merge ou mudanças nas
oficiais, jogador, PR31, permissões ou acionadores.

## Concluído

- E01: Versátil reconhece os dados do catálogo, incluindo `1d8` → `1d10`.
- E02: quantidade inválida/zero não fornece equipamento nem volume negativo.
  Quantidade em branco continua valendo uma unidade. K92:K99 recebe validação
  estrita de inteiro não negativo ou vazio.
- E03: mão secundária considera o estoque restante após a principal.
  Seleções antigas continuam visíveis com aviso, sem contribuição mecânica.
- Gerador, fontes GS, pacote e preparador incremental atualizados.
  Geração `4a11f363478f92f5`. Testes locais focais e preflight concluídos.
- Aplicados 63 pedidos nativos em cada descartável Era/Ciclo: 54 fórmulas,
  uma nota e oito validações. Codigo incremental salvo nas duas pelo editor.
- Quinze cenários de recálculo passaram em cada cópia (30 execuções): catálogo,
  Versátil, uma unidade nas duas mãos, duas unidades na mesma linha e em linhas
  distintas, primeira linha sem estoque, quantidade negativa/fracionária/texto,
  escudo sem estoque/equipado, Espadão em cada mão e volume manual de linha
  livre com/sem estoque.
- Os dois checks smoke de `a8c9bdc` estavam SUCCESS ao pausar.
- Todas as 15 entradas temporárias por cópia foram restauradas e relidas sem
  divergências. AG98 voltou à fórmula nova da correção, não à anterior.
  A correção permanece instalada somente nas descartáveis.

## Pendências antes de declarar pronta para revisão

1. Reabrir os dois editores e conferir o Codigo persistido contra o SHA-256
   `a09bf672a520e0750d239386f23f14e300eda84094668b7771cee605e028ebac`.
   O salvamento foi observado, mas esta releitura após recarregar ficou pendente.
2. Testar pela interface a rejeição de quantidade negativa e a restauração
   de S66/AG92 por edição real. O recálculo por API não comprova onEdit.
   Não executar construir/continuar. Fazer snapshot novo antes dos ensaios.
3. Restaurar os campos e eventuais notas dinâmicas após os testes, conferir
   todos os alvos do plano, registrar evidências e atualizar a descrição da PR64.
4. Conferir checks do último commit e só então retirar o rascunho se conforme.
5. Continuar Bênçãos/imunidades. Apenas pesquisa preliminar nesta rodada:
   Casco, Estímulo Muscular e imunidade de Corpo Amaldiçoado ainda precisam
   de cenários nativos e controles. Não são novos erros confirmados.

Não promover às oficiais nem tocar PR31. Livro usado: R66 de JJK---Project,
commit `e3058ad29180fdec2efec75b512446c49bf87b3d`.

## Evidências privadas locais

`nuvem-b47/saidas/correcao-equipamento/pausa-20261105.json` contém IDs das
descartáveis, snapshots, pedidos, casos, resultados e releitura da restauração.
Também há `Codigo-proposto.gs` nessa pasta. Diretório ignorado pelo Git.
Não versionar snapshots, dados pessoais ou credenciais. Em outro computador,
descobrir as conexões e obter snapshots novos. Não presumir abas/autorização.

Recomendação: Sol/High para ensaios restantes, Sol/Medium para revisão focal.
Não alterar configurações automaticamente.
