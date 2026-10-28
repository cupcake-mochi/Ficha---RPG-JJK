# Contrato REST e piso do XP

28/10/2026 · PR31, etapa 7 parcial. Não instalado nem publicado. Criação bloqueada.
Main produtor ef361cc e bot de42447 reconferidas antes das alterações.

## Defeito reproduzido e corrigido

DADOS_CONFIG calcula o XP acumulado relativo ao nível inicial de CONFIGURAÇÃO.
Abaixo do piso retorna exatamente “—”; no piso retorna 0. r53NovaProgDados_
exigia números em toda a curva e recusava uma cópia válida com piso maior que 2.
Reprodução antes da correção: nível 10/curva nativa → erro de curva inválida.
Agora exige “—” só abaixo do piso, zero no piso e inteiros não negativos/não
decrescentes acima. Fórmulas, índices, níveis e demais guardas continuam estritos.
Diário de base anterior diferente é recusado, sem apagar, migrar ou reescrever.

Os testes antigos usavam a tabela cumulativa iniciada em 2 mesmo com G46=10;
essa simulação estava desatualizada. O oráculo agora acompanha as fórmulas
publicadas de DADOS_CONFIG, sem chamar o inicializador. Não foi uma mudança de
expectativa para ocultar falha: a divergência foi reproduzida e confirmada no
Google. Os registros históricos de projeção de XP 3.700 foram escritas pontuais;
não comprovavam a execução deste inicializador nem a curva após recálculo.

## Sondagem Google delimitada

Uma cópia nova e descartável do Ciclo, via conector Google Drive, recebeu só
CONFIGURAÇÃO F46, F65 e F74. Sem instalar/rodar Apps Script ou tocar oficial/jogador.
Pisos 2, 10 e 30: abaixo “—”, piso 0. No piso 10, custo 10→11 de 2100 produziu
0/2100/3000 nos níveis 10/11/12. Piso 1 sem custo 1→2 ficou Pendente; com custo
explícito zero, níveis 2/3 deram 0/200. Treze fórmulas das sete guardas financeiras
coincidiram com variantes exatas do contrato REST. Cópia na lixeira e aba fechada.
Evidências privadas em nuvem-b47/saidas/curva-rest-20261028/, ignoradas pelo Git.
Não é execução nativa do inicializador, prova drive.file das Guias ou ensaio total.

## Contrato exportado

`gerar_contrato_rest.js [--conferir]` exporta contrato_rest.json, só dados públicos,
sem montar pacote/ficha. Captura hashes dos seis fontes, operações financeiras,
guardas e variantes exatas, regra/piso, custos da configuração, curva, rótulos e
quatro modelos de fórmulas de missão conferidos contra as 292 células da fábrica.
Não faz rede. Não recebe plano/endereços do navegador nem usa dados de jogador.

O consumidor fixa SHA256 1001e7c3605c754b5bf04c33cfd65542c90ef4b897deffda40167a2bafb30439,
com cópia byte a byte em dados/ficha/inicializacao-rest-v1.json. Mudança exige
revisão explícita do contrato. Não amplia equivalências de fórmula por heurística.
Não muda contratos anteriores, diários GS, permissões ou a ficha oficial.

47 cenários novos de contrato/piso e 82 de progressão passaram; sequência 67 e
leitura conjunta 43 passaram. CI completo em fechamento; esperado 2.999 cenários
de inicialização. O consumidor agora confere estes dois domínios via REST e cria
recibo cifrado histórico; não implementa diário persistido/retomada de escrita.

Faltam adaptação dos demais domínios, propriedades de Apps Script, persistência
segura de operações, autorização/cópia/fila no serviço, arte/preservação global,
automações/treinos/notas, responsável e prova nativa do fluxo inteiro. Consistência
temporal, imagens, conferência final e criação continuam falsas. Sem merge/deploy,
modelo pago, escopos novos, oficial/jogador ou publicação executável.
Próximo: Sol Alto para integrar; Médio para revisão. Não alterar configurações.
