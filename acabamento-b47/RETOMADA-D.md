# D — checkpoint de continuação · 16/10/2026

## Estado vigente — salvamento pedido por saldo quase esgotado

Este bloco prevalece sobre os próximos passos dos checkpoints históricos abaixo. **D continua em andamento e não foi aplicada na revisão.** A descartável D tem 22 abas, fundo canônico corrigido, textos temporários limpos, grupos restaurados exatamente, fuso São Paulo e 35 GS + manifesto relidos iguais. O diagnóstico existente `verTemposDaPaleta` executou com sucesso, sem nova concessão de permissões nem edição de código. `PALETA-NATIVA.json` confirma restauração completa ao Mizuki Escuro: 37/37 passos, quatro execuções da troca, soma de 67.473 ms de passos, 116.604 ms decorridos e carteira completa em 12.561 ms. A dúvida anterior sobre conclusão interna da paleta está resolvida.

`PONTO-EXECUCAO.json` registra a interrupção segura da leitura final: **34 de 72 blocos concluídos**, na pasta privada `d/final/`, seguindo a ordem de `d/plano-depois.json` (os nomes dos arquivos mantêm os índices do plano original e podem ter lacunas). A função de diagnóstico terminou; não há pedido de autorização pendente. Código, dados e grupos estão restaurados; não repetir lotes destrutivos/formatadores na descartável.

Próximo passo: completar a leitura final e executar `comparar-estudos.py` com a prova estrita de 12 notas e do fuso (`--retirados --notas-contextuais nuvem-b47/saidas/cd/referencia-combinada.json --prova-fuso acabamento-b47/FUSO-NATIVO.json --metadata <metadata-final.json>`). A extensão temporal do comparador está preparada, mas a conferência final ainda não foi executada. Depois, conferir acionadores instaláveis/checklist visual restante e preparar a aplicação D na revisão com backup, snapshot e releitura novos. A revisão segue com 26 abas e GMT no fechamento C.

Para retomar em ambiente sem os arquivos privados deste PC: os dados preenchidos deliberadamente não estão no Git. Recriar leituras nativas atuais usando a cópia D, seu backup `1BbJDVUD3TV4o-YU1gH_E3R8wGCZcPMZwIw49wxljXLg` e a revisão C, sem depender de upload de snapshots do personagem. As provas resumidas e IDs estão versionados. Confirmar ferramentas/conta Google; Git não fornece esse acesso. Se retomar em outro dia, fazer uma leitura final nova completa, sem misturar blocos de dias diferentes, e conferir novamente a data dinâmica AH3. Fontes/modelo canônico são os mesmos da geração C; não regenerar/escrever por rotina. Próxima ação recomendada: Sol/Médio ou modelo de programação disponível no Claude, esforço médio, para a conferência delimitada; não presumir equivalência ou configurar o seletor automaticamente.

O usuário autorizou iniciar D após o fechamento de C e pediu checkpoints frequentes porque restam 2% de uso semanal. Se necessário, continuará no Claude amanhã às 9h. Não há agendamento nem autorização para novos chats/agentes.

## Base preservada

- C concluída e publicada: `21f162076c9b49fab053ce809d418ce00117ed10`, nos ramos `codex/b47-capacidade` e `codex/configuracao-b47`.
- Leia `conteudos-b47/comum/FECHAMENTO-C.md` e suas provas. Não repetir a migração C nem os lotes v10→11.
- Revisão autorizada: `1EdEXzFRL8n21dLb60lxE2wbP4PFxFUiBdw7BiTTkNg0`.
- Apps Script da revisão: `1wdZc903PPK6EoGxFG4KcuPNx_plElCBsWxa4lEBgLUlFBD4OrbZPHYnf` (35 GS e manifesto persistidos e relidos iguais).
- Nova cópia descartável para D: `1j16g_UYCO-SURTioAxZJ0H65SxP1NhMMKjnJdfPlgxE`, criada da revisão após C; 26 abas esperadas. Não foi modificada após a cópia neste checkpoint.
- Evidência privada de abertura: `D:/JJK - Project/B47/evidencias/2026-10-16/d/abertura.json`. Dados do personagem e credenciais não entram no Git.

## Checkpoint: auditoria dos estudos concluída

`AUDITORIA-ESTUDOS.json` e `auditar-estudos.py` registram a auditoria da cópia D: 76 blocos nativos, 26 abas, 63.954 fórmulas, 5.192 validações e 5.342 notas, sem referências entrantes aos quatro estudos e sem erros de fórmula. Referências indiretas foram resolvidas conservadoramente: somente `INDIRECT(SWITCH(...))` cujos resultados/default são faixas literais em abas preservadas. Os 35 scripts canônicos não mencionam os estudos. Os três intervalos nomeados pertencem à carteira. O único `getSheets()` genérico de Codigo.gs percorre proteções, sem depender de uma posição ou estudo.

As leituras completas, com dados privados, estão em `D:/JJK - Project/B47/evidencias/2026-10-16/d/antes/`; plano e metadados na pasta pai. Foram lidas fórmulas, valores efetivos, notas, validações, hyperlinks e textFormatRuns, além dos metadados integrais. Não houve remoção nem alteração de conteúdo. A obtenção dos metadados integrais usou uma atualização idempotente do título existente na cópia.

Próxima ação exata: backup nativo da cópia D, releitura para confirmar o snapshot, remoção apenas dos quatro estudos na cópia D, comparação integral de fórmulas/entradas/notas/validações e resultados preservados, ANALISE com 8.190 chaves. Não remover estudos da revisão antes desse ensaio. Sol/Médio é suficiente para esse procedimento delimitado.

## Checkpoint: retirada ensaiada na descartável

Bloco acima concluído. Backup nativo da descartável antes da retirada: `1BbJDVUD3TV4o-YU1gH_E3R8wGCZcPMZwIw49wxljXLg`. A releitura integral dos 76 blocos não apresentou diferenças (`RELEITURA-ESTUDOS.json`). Foram retiradas somente as quatro abas de estudo na cópia D, que agora tem 22 abas; não repetir os pedidos `deleteSheet` nessa cópia.

Comparação pós-retirada: 72 blocos, 107.367 células com conteúdo/metadados preservados, 4.458 notas anteriores e 4.930 validações preservadas; valores efetivos e fórmulas iguais, zero erros, ANALISE 11 com 8.190 chaves únicas. A comparação estrita (`ENSAIO-RETIRADA-ESTUDOS.json`) detectou 12 notas novas nos seletores de tipo das entidades, antes vazios. Cada uma foi conferida como idêntica à ajuda calculada em `DADOS_ENTIDADES`, na coluna/linha de `notas_contextuais` do spec canônico. Não foi comprovado qual evento acionou a atualização. A prova classificada (`ENSAIO-RETIRADA-ESTUDOS-CLASSIFICADO.json`) aceita somente esses acréscimos em notas vazias; nenhuma nota manual foi ignorada ou perdida. Os seis testes de classificação de referências indiretas passaram.

Dados/recibos privados: pasta `d/antes`, `d/releitura`, `d/depois`, planos e `recibo-retirada.json` sob o diretório de evidências de abertura. Não publicar dados do personagem. **A revisão continua com 26 abas no fechamento C; ainda não recebeu a retirada.**

Próxima ação vigente: revisão visual da descartável e auditoria do fundo/fonte dos espaços novos de CONFIGURAÇÃO contra a construção canônica C; depois demais testes D. A aplicação final na revisão continua exigindo backup/snapshot/releitura novos. Sol/Médio para a conferência visual e correções delimitadas.

## Checkpoint: fundo padrão de CONFIGURAÇÃO corrigido na descartável

Bloco visual inicial concluído. Comparação nativa com a construção C (`14Ad8e5hUECLimCFuilEGSIxrhv0IWpDUEjEBR4N8N-Q`) identificou 3.988 células vazias sem qualquer formatação explícita no acréscimo `CONFIGURAÇÃO!A1733:P2812`. Receberam exclusivamente o formato-base da construção canônica (Mizuki Escuro, Roboto 10). Nenhum cartão foi redesenhado, nenhum endereço movido. Foram 313 pedidos `repeatCell` em quatro lotes, todos confirmados. **Não repetir os lotes nesta cópia.**

`FUNDO-CONFIGURACAO.json`: comparação exata do trecho inteiro antes/depois, com zero diferenças inesperadas em formatos e com valores/fórmulas efetivos, entradas, notas e validações preservados. `preparar-fundo-config.py` gera o plano offline a partir das leituras canônicas e exige candidatos vazios/sem estilo, formato-base único e cobertura exata. Os formatos anteriores, guardas, pedidos e recibos estão na pasta privada `d/formatos/` e `d/pedido-fundo.json`. Capturas `d/visual/configuracao-antes.png` e `configuracao-depois.png` conferidas a 100%.

Próximo passo vigente: demais verificações visuais/interações D na cópia `1j16g_UYCO-SURTioAxZJ0H65SxP1NhMMKjnJdfPlgxE` (carteira/foto/paleta, menus, textos longos e limpeza, grupos, inventário e 12 entidades), bateria final pertinente e cópia/gatilhos/código persistido. Só depois aplicar o conjunto aprovado na revisão com backup/snapshot/releitura novos. A revisão continua sem alterações de D. Canônicos GS/modelo não foram alterados, pois já produzem o fundo correto. Sol/Médio para seguir; registrar impedimentos sem declarar D concluída.

## Checkpoint: textos nativos e regressão de paletas

`TEXTOS-NATIVOS.json`: edições reais na cópia, nos requisitos dos dois primeiros cartões de Forma (`B1911`, `J1911`). Quatro linhas cresceram de 25 para 150 px com 3.368 caracteres à esquerda; para 258 px com 5.081 caracteres à direita; continuaram em 258 px ao limpar a esquerda e voltaram a 25 px ao limpar a direita. Restauração exata de valores/valores efetivos, formatos, notas e validações no bloco `B1911:O1914`. Não há texto temporário nesses campos. Capturas e leituras de todas as fases na pasta privada `d/`. A regressão `node regressao-textos-custom.js nuvem-b47/saidas/cd/combinado-modelo.json` também passou seus sete cenários, com 136 grupos de altura.

`PALETAS-VM.json`: `node regressao-paleta.js` terminou com TODOS PASSARAM, incluindo cores/arte nas 122 paletas, cenários de cópia, troca interrompida e cliques que retomam a troca. É VM com custos históricos simulados, não latência atual nativa.

Teste nativo de paleta na cópia D: seleção real de `Mizuki · Claro · rosa e magenta` alterou a carteira sem autorização/ativação manual; CONFIGURAÇÃO continuou em Mizuki Escuro. O valor original `Mizuki · Escuro · ameixa e rosa` já foi reposto e confirmado por leitura nativa. **Ainda conferir a convergência completa das cores/arte nas outras abas antes de declarar restauração integral da paleta.** Cliques/seleções e edições normais continuam os passos; não é necessário instalar gatilhos. As capturas `carteira-claro.png`, `carteira-escuro.png`, `configuracao-fixa-durante-claro.png`, `ficha-topo.png` e `amaldicoada-topo.png` registram estados intermediários; não usar a captura intermediária clara da FICHA como prova do estado final escuro.

Próxima ação exata: concluir a conferência da restauração da paleta enquanto revisa as abas visíveis, grupo 7, inventário e as 12 entidades/abertura de grupos; falta a aplicação D na revisão. Última aba visualizada: FICHA AMALDIÇOADA, célula A1, zoom 75%, tab IAB 32 (pode não sobreviver ao turno; localizar pelo ID da cópia). Recomendação Sol/Médio para continuar os testes delimitados.

## Checkpoint: grupos, retenção A+B e código copiado

`GRUPOS-NATIVOS.json`: cabeçalhos/numeração abriram as fileiras recolhidas e a coluna da direita, incluindo a última entidade. Os metadados confirmaram as seis fileiras e ambas as colunas de entidades abertas (12 fichas acessíveis). A abertura é assíncrona: algumas leituras imediatas antecederam o gatilho; a leitura posterior da fileira 4 comprovou a abertura sem novo clique. Foram restaurados seis grupos modificados, com comparação exata de todos os rowGroups/columnGroups de INVOCAÇÕES contra o estado inicial. Nenhum dado foi editado nesse ensaio. A mecânica das 12 fichas permanece coberta pela prova integrada C, sem alteração das fontes.

`RETENCAO-AB.json`: contrato, leitor, endereços e carregador passaram no modelo C de hash bruto `939bb2afb657a74d222d800e30e1c2e6bd2413a18b03755d688045d5b03ddf39`, usando o perfil histórico `b47-v10` para a **retenção A+B**, sem trocar expectativas. São 83 verificações, zero falhas bloqueantes e dois riscos de manutenção: prefixos de aviso diferentes (o leitor reprova todas as mensagens testadas) e endereços literais em INDIRECT (destinos nativos finitos já auditados). Não apresentar esse perfil como cobertura isolada dos novos catálogos C ou como recálculo Calc.

`NATIVO-CODIGO-COPIA-D.json`: projeto vinculado da cópia D localizado por Extensões → Apps Script: `1WXWUmNRmfrS5zKKOK9HrlCrJTEEUbtCgin0SdeMFMd8fKP0SVQznPPuS`. **35 GS e manifesto relidos integralmente e hashes iguais** aos canônicos do fechamento C. Nenhum código foi editado; apenas foi habilitada a exibição do manifesto no editor. Os gatilhos simples de altura e paleta funcionaram na cópia sem autorização/ativação manual. Não confundir com auditoria de gatilhos instaláveis (não foi executada ainda).

Capturas adicionais privadas: carteira, topo da FICHA/AMALDIÇOADA, inventário/treino de armas de FICHA PESSOAL, cartões originais do grupo 7, glossário, abertura de entidades e largura inteira da ficha 12. Os cabeçalhos de cor das seis abas dinâmicas voltaram ao escuro; ainda falta fechar a conferência de todas as etapas de cor/arte antes de declarar convergência integral. A revisão permanece sem qualquer aplicação de D.

Próxima ação vigente: conferir execuções/gatilhos da cópia e encerramento da paleta; terminar o checklist visual/interações; auditar o estado final da cópia contra o snapshot; preparar aplicação D na revisão com backup/snapshot/releitura novos. Investigar a data de emissão da carteira: a captura mostra 17/10 enquanto o cliente está em 16/10 à noite; metadata Sheets está em Etc/GMT e manifesto Apps Script em America/Sao_Paulo. **Nenhuma alteração de fuso foi feita.** Determinar a fórmula/origem e o efeito antes de corrigir, sem alterar datas/contas do jogador por inferência. Sol/Médio para as próximas verificações.

## Checkpoint: data de emissão corrigida na cópia D

A investigação acima foi concluída: a única fórmula temporal em todas as leituras nativas é `CARTEIRA!AH3`, a emissão calculada por TODAY. O fuso Sheets foi alinhado ao manifesto Apps Script já existente e ao projeto: `Etc/GMT → America/Sao_Paulo`. A fórmula permaneceu idêntica e o texto mudou de `Emitida 17.10.2026` para `Emitida 16.10.2026`, conferido com relógio UTC convertido para São Paulo. Prova: `FUSO-NATIVO.json`. Código GS não foi alterado; a configuração do arquivo nativo viaja com suas cópias. A revisão ainda está em GMT; incluir esta alteração na aplicação D somente após a comparação integral.

Na comparação final da cópia contra `d/antes`, esta é uma alteração efetiva intencional somente em `CARTEIRA!AH3`; as 12 notas de ajuda já estão classificadas na prova anterior. O comparador estrito atual não admite essa diferença automaticamente: conferir e registrar explicitamente a prova temporal, sem ignorar genericamente alterações de valores efetivos.

Histórico de execução inspecionado no projeto D: 50 execuções recentes, todas Concluídas (46 onSelectionChange, quatro onEdit, duração máxima observada 25,703 s). Não é auditoria de todo o histórico; o seletor de tamanho de página não foi alterado com sucesso. Ainda falta conferir acionadores instaláveis e a conclusão interna da paleta. A leitura de registros de Cloud da execução 23:11:33 retornou “Nenhum registro está disponível”, portanto não prova estado interno da troca. Próximo passo: tentar a função existente de leitura `verTemposDaPaleta` no editor; se o Google exigir consentimento, não conceder novos acessos por conta própria. Continuar o restante independente se houver espera. Sol/Médio.

## Próximos blocos

1. Auditar dependências das quatro abas temporárias: `ESTUDO CAMPANHA`, `ESTUDO CUSTOM`, `ESTUDO 3B`, `ESTUDO 3C`. Confirmar nomes/IDs nativamente; procurar fórmulas, validações, intervalos nomeados, gráficos, regras e scripts. A geração canônica de C já produz 22 abas sem estudos; isso sozinho não prova a ausência de dependências na revisão preenchida.
2. Ensaiar a retirada na cópia D e comparar resultados, notas, validações e ANALISE (formato 11, 8.190 chaves). Só então preparar aplicação na revisão, com backup e snapshot/releitura novos.
3. Conferir acabamento nos moldes aprovados: CONFIGURAÇÃO e cadastros, carteira/foto/paleta, grupos, menus, textos longos, recolhimento e 12 entidades. Investigar o fundo/fonte padrão nos espaços novos de CONFIGURAÇÃO, comparando a construção canônica antes de corrigir.
4. Validar cópia funcional, gatilhos, persistência do código e bateria pertinente à versão final. Calc não está instalado neste Windows e `fcntl` não existe aqui: registrar impedimentos reais; não declarar bateria integral aprovada por smoke.
5. Publicar fechamento com provas e pendências explícitas.

## Limites

Preservar escolhas, resultados e endereços das entradas. Não importar XLSX no Google. Nunca executar `construir()`/`continuar()` na revisão preenchida ou oficial. Sem main, force push, bot, ficha oficial, alterações de acesso ou agentes extras. Fontes sincronizadas do projeto são somente leitura. Trabalhos pesados em série, após conferir memória. Novo desenho exige estudo/aprovação; conservar o desenho aprovado evita essa ampliação.

Trabalhar em `codex/b47-capacidade`, publicar checkpoints verificáveis e reunir em `codex/configuracao-b47` somente após conferir a base. Atualizar este arquivo a cada bloco: realizado, prova, próximo passo e estado nativo. Recomendação para a próxima ação: Sol/Médio, pois a auditoria inicial é delimitada e preserva os moldes aprovados.
