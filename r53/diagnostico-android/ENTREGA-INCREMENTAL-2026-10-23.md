# Consolidação da candidata C e promoção ensaiada — 23/10/2026

**Atualização vigente — promoção aplicada com autorização específica:** as 37 etapas
foram aplicadas na oficial após snapshot nativo atualizado e preflight completo.
Veja [PROMOCAO-APLICADA-2026-10-23.json](PROMOCAO-APLICADA-2026-10-23.json).
As 498 fórmulas, os 15.869 literais, as três barras e a grade foram relidos;
contrato integral de 73.576 células preservado, com 18.393 chaves e zero erros.
Código instalado e relido integralmente igual à C; salários, entradas, nomes e
proteção preservados. Abertura web e barras conferidas; `onOpen` (2,714 s) e
`salarioAposAbrir` (17,307 s) concluíram. Estes são tempos Apps Script no servidor,
não medidas Android. O teste da oficial no Android FALHOU no telefone do usuário:
carregamento infinito. A C abre normalmente nesse mesmo aparelho e o snapshot R52
abre um pouco lento. Leia `ANDROID-OFICIAL-FALHA-POS-PROMOCAO-2026-10-23.json`.
Cópia nativa pós-promoção ABRE e permite uso no telefone do usuário; amigo também
testou e abriu, conforme relato. Código da cópia relido integralmente igual ao
instalado na oficial. O link direto da oficial à CARTEIRA também FALHOU:
continua carregando sem abrir. Esse teste está concluído; não repetir como pendência.
Causa ainda não isolada; não cortar recursos nem substituir a oficial automaticamente.
Prompt portátil salvo em `nuvem-b47/saidas/diagnostico-mobile-20261023/diagnostico-pos-promocao/`
como `PROMPT-RETOMADA-CODEX-ANDROID-2026-10-23.txt`, ignorado pelo Git.
Se ausente em outro computador, retomar pelo registro JSON sanitizado. R52 é secundária.
A abertura continua sendo a prioridade; cores e quatro Sementes ficam adiadas.
Não reaplicar as etapas; a oficial já contém a promoção. Novas intervenções
exigem snapshot e escopo próprios. Capturas privadas em
`nuvem-b47/saidas/diagnostico-mobile-20261023/promocao-aplicada/`, ignorada.
Próxima conferência: Sol/Medium; futura implementação de cores: Sol/High.

**Registro anterior de preparação e ensaio (histórico):**


Base conferida: `86f9bac`, branch `codex/otimizacao-android-r53`, checkout inicialmente limpo.

## Conclusão da etapa de abertura

O aceite funcional da candidata está sustentado pelo relato do usuário: C abre e permite uso nos aparelhos fracos; A não abre. As evidências sanitizadas anteriores registram 267 verificações nativas, igualdade completa de ANALISE A:D e ausência de erros nas 27 abas. Não há justificativa nova para reduzir capacidades ou repetir a bateria completa. Isso não constitui medição de tempo/RAM nem aprovação de promoção à oficial.

## Conferência nesta continuação

- Google Drive/Sheets acessível pelo conector; nenhuma sessão de documento conectada.
- Apps Script C acessível no navegador autorizado deste computador.
- Metadados C: 27 abas, 710.587 posições, ANALISE com 18.394 linhas e quatro colunas; tamanho Drive 1.803.404 bytes, modificação informada em 23/10/2026 às 13:57:53.246 UTC.
- Leitura focal: FICHA S26/S30/S34 contêm SPARKLINE nativo; ANALISE C5956 contém texto literal com apóstrofo inicial preservado. Não foi repetida varredura completa.
- Codigo.gs instalado foi lido pelo editor: 661.836 caracteres; onOpen registra menus e só chama o módulo leve quando existe paleta pendente. O carregador conserva r53CorrecaoAbertura_ e r53CorrecaoAndroid_. Não é o pacote integral regenerado.
- Helper concluirEnsaioPaletaC removido e persistência confirmada após recarregar: 659.964 caracteres, exatamente o original menos o sufixo de 1.872 caracteres. A rodada anterior recarregava antes de terminar o salvamento; nesta rodada aguardou-se a conclusão. SHA-256 do arquivo salvo: `6112c6cf4ff34c88cea6c944b55aaf62a878e2310bb502b2ac5d2131f2d57e80`. Capturas integrais privadas salvas localmente. O teste conferir_carregador_salvo.js passou igualdade integral do delta, abertura sem catálogo e delegação da paleta pendente em VM local.
- Teste focal local testes_constantes.js aprovado: 603 conversões, sete restaurações, idempotência e escape de apóstrofos. É mock local, complementa a evidência nativa anterior.
- Memória consultada antes de qualquer geração; nenhuma geração pesada executada.

Foi criada e relida uma cópia nativa de segurança antes das tentativas de limpeza. Seu link fica no registro privado local; não versionar snapshot ou código capturado. A cópia não equivale a backup de acionadores/propriedades do projeto.

## Entrega incremental proposta para revisão

| Componente | Escopo exato | Condição de aplicação |
| --- | --- | --- |
| Fórmulas | 249 FD + 249 FX de DADOS_R53 | Conferir originais atuais e resultados contra snapshot; reutilizar compactação validada |
| Grade | Apenas ANALISE E:L vazias | Conferir conteúdo, notas, validações, nomes, proteções e dependências atuais; preservar A:D |
| Constantes | 15.869 constantes de ANALISE C | Instalar primeiro recuperação compatível; preservar escape e conferir A:D integralmente |
| Carregador | Delta sobre código realmente instalado | Capturar código atual, preservar salários/catálogos e abertura leve; excluir somente helper de QA na C |
| Barras | FICHA S26/S30/S34 | Conferir visualmente proporções/cores com recursos positivos em cópia descartável antes de incluir |

O preparador existente preparar_loader.js também incorpora mudanças de paleta da fonte atual. NÃO o reaplicar cegamente para limpar a C nem usá-lo como delta exclusivo de abertura: a fonte contém ajuste pós-lock ainda não instalado. O pacote integral regenerado também não é o instalador incremental aprovado.

## Pendências concretas antes de promoção

1. Limpeza do helper e releitura integral: concluídas.
2. QA visual das barras: concluída em cópia nativa, com 25%, 50%, 75%, 100%, zero e máximo zero. Detectado que SPARKLINE com 0/0 desenhava barra cheia; guarda de atual/máximo não positivo validada em QA e aplicada apenas em S26/S30/S34 da C após snapshot novo. Entradas D/J preservadas (0/0, 0/0 e 65/65). A correção adiciona 105 bytes ao texto das fórmulas; contagens de fórmulas/grade permanecem iguais. Não houve nova varredura completa; o inventário final anterior é histórico. Fonte ficha-v01/ficha_pessoal.py corrigida; sintaxe e emissão focal das três barras conferidas. A geração integral 0c4547e1ace6efd9 antecede essa correção: seus GS não foram regenerados nesta rodada e não devem ser promovidos como versão atual das barras.
3. Capturar snapshot novo da oficial e código vinculado imediatamente antes de preparar pedidos executáveis; conferir acionadores existentes sem criar ou ativar nenhum. A oficial permanece somente leitura nesta etapa.
4. Gerar delta a partir desse snapshot, ensaiar em cópia nativa e produzir rollback por célula/código com pré-condição do estado aplicado, preservando edições posteriores. Após timeout, reler antes de retomar.
5. Apresentar os pedidos e evidências para eventual promoção autorizada. Não substituir a oficial automaticamente.

A especificação preliminar foi concretizada no lote privado `promocao/delta.json`, com snapshot atual, código capturado, pré-condições e recuperação. As evidências antigas do outro computador continuam indisponíveis; o ensaio usa novas capturas nativas.

Cores e quatro Sementes de Sem Técnica permanecem frentes independentes. Nenhum ensaio de paleta foi executado, nenhuma função construir/continuar foi chamada e nenhum acionador/acesso foi alterado.

Próxima ação: Sol/Medium para conferência focal do salvamento e barras; Sol/High para preparar o delta integrado de promoção. Configurações não foram alteradas.

## Estado de fechamento da candidata

A candidata de abertura está consolidada com os relatos Android e as evidências existentes. Nenhuma nova redução de capacidade é necessária. Limpeza do código e QA focal das barras concluídas; a promoção da otimização à oficial ainda exige captura atual, preparação e ensaio do delta completo. A fonte regenerada anterior não substitui o carregador instalado. A cópia de QA mantém valores sintéticos exclusivamente para revisão visual.

## Lote incremental ensaiado nesta continuação

O snapshot atual da oficial e a cópia de ensaio foram criados nativamente. O carregador oficial foi capturado pelo editor, sem edição. As 498 fórmulas FD/FX, as 73.576 células de ANALISE A:D, as colunas E:L e sua formatação foram lidas em blocos delimitados. A memória disponível era cerca de 2,9 GB; não houve geração integral ou bateria mecânica repetida.

O código preparado é exatamente o carregador limpo e validado da C. `preparar_promocao_loader.js` verifica o hash dessa referência e prova que a derivação da oficial não difere fora dos três corpos conhecidos: correção Android, conversão de constantes e módulo leve de paleta. Assim, não incorpora a alteração pós-lock da fonte ainda não instalada. Os salários, o carregador de abertura anterior e os catálogos permanecem preservados. A cópia recebeu esse código e a releitura após recarga foi integralmente igual. Hash anterior da oficial: `a15cf71f23cc0c95a16973900171ae2f5aa6d25b1575d29b7cc5c515943212a1`; hash proposto: `6112c6cf4ff34c88cea6c944b55aaf62a878e2310bb502b2ac5d2131f2d57e80`.

O lote contém 25 etapas de fórmulas, dez de literais, uma de barras e uma de grade. A aplicação usou somente `userEnteredValue` nos conteúdos; formatos, notas e validações foram comparados. Na cópia:

- 498 fórmulas FD/FX relidas exatamente iguais à C, com resultados e metadados preservados;
- 15.869 constantes convertidas com `updateCells/stringValue` RAW, preservando apóstrofos; a recuperação por Apps Script continua usando o escape RichText validado;
- 73.576 células de A:D comparadas integralmente após a migração: valores, tipos, notas, validações e formatos iguais; 18.393 chaves únicas e zero erros no contrato;
- edição nativa de ANALISE C5956 restaurada automaticamente, com valor e metadados exatos;
- três barras copiadas da C com a guarda de zero, sem mudança nas entradas;
- 147.152 posições vazias removidas; 27 abas e grade final de 710.587 posições;
- restauração das oito colunas exercitada e todos os 147.152 formatos relidos iguais, sem valores/notas/validações novos; grade otimizada reaplicada depois;
- recuperação e reaplicação de um lote de 20 fórmulas exercitadas, com resultados, notas, validações e formatos iguais;
- três intervalos nomeados, proteção salarial e sentinelas de configuração/saldo preservados.

A oficial tem três acionadores existentes: `salarioRegistrarEdicao`, `salarioAposAbrir` e `salarioDiario`. Foram apenas inspecionados. A cópia não recebe os acionadores instaláveis da oficial; o ensaio não configura outros. O comportamento salarial automatizado já validado anteriormente não foi apresentado como novo teste de pagamento.

### Aplicação futura, após autorização específica para a oficial

1. Conferir novamente o horário/tamanho da oficial, seu código e todos os alvos contra o snapshot. Se houver mudança, renovar snapshot e reavaliar o delta; não sobrescrever edições posteriores. O registro desta rodada manteve a oficial em 1.919.122 bytes e modifiedTime `2026-10-23T06:31:43.275Z` até a conferência final.
2. Conferir hash do carregador atual; guardar nova captura e instalar somente o código incremental ensaiado. A instalação e a releitura devem anteceder a conversão dos literais. Não instalar o pacote integral nem executar construir/continuar.
3. Para cada etapa de células, reler TODOS os seus alvos. `conferir_etapa_promocao.py` classifica a leitura contra os valores anteriores/propostos. Aplicar somente se estiver inteiramente no estado anterior. Depois de timeout, reler: se aplicada, não repetir; se mista, divergente ou incompleta, parar e reconciliar.
4. Para a grade, conferir novamente E1:L18394 vazias, nomes, proteções e dependências. A classificação por número de colunas não substitui essa conferência. Não repetir deleteDimension se já houver quatro colunas.
5. Repetir as releituras focais/integrais do contrato e sentinelas usadas no ensaio. Preservar os três acionadores, sem criação ou reativação.
6. Se necessário, recuperar somente alvos ainda iguais ao valor proposto. Reverter o código apenas se seu hash continuar igual ao instalado; restaurar grade/formatos a partir do lote privado. Não reverter um documento inteiro por cima de alterações posteriores. O snapshot nativo é contingência adicional, não substitui o preflight por célula.

Os lotes, códigos, capturas, registros de alvo e imagens estão exclusivamente em `nuvem-b47/saidas/diagnostico-mobile-20261023/promocao/`, ignorada. A cópia de ensaio está registrada em `registro-alvos.json` privado. A próxima etapa na oficial requer autorização explícita: o pedido vigente a mantém somente leitura.

A fonte Python das barras contém a guarda nova, mas os GS integrais anteriores ainda não foram regenerados. Isso não impede o lote incremental, que usa as fórmulas nativas capturadas da C e o carregador ensaiado. Não promover a geração integral antiga como atualização das barras.

Próxima ação recomendada: Sol/High para aplicação incremental autorizada e suas conferências. Sol/Medium para revisão focal do lote. Sem alteração automática de configurações; paleta e Sementes permanecem frentes separadas.
