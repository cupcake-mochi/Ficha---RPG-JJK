# Teste da parte 3c — Famílias, Melhorias e Restrições

Destino: cópia nativa de revisão B47. Não executar `construir()` nessa cópia nem na ficha oficial. A medição integral será feita na descartável depois da integração dos demais catálogos.

## Preparação

Guarde os valores anteriores antes de testar. Os primeiros cartões ficam em CONFIGURAÇÃO: nome B1809/J1809, estado E1810/M1810, MESTRE VIU F1807/N1807 e descrição B1812/J1812. Os limites da técnica estão em F157/F158; G157:G160 mostram os valores usados. A Família318 termina no cartão iniciado na linha4017: nome J4021, estado M4022, MESTRE VIU N4019 e descrição J4024.

## Roteiro no Sheets

1. Com os cadastros vazios e a campanha sem alteração, conferir nove Famílias no catálogo e os limites do livro: duas Livres e três Fechadas. Neutras é o saldo, quatro. A ficha vazia pode avisar que o jogador ainda não distribuiu os estados; isso não é erro de fórmula.
2. Cadastrar um nome único no primeiro cartão, como “Teste de Ressonância”, com estado Neutra. O catálogo passa a dez Famílias e o saldo aumenta um. O nome aparece nos menus de Família das invocações.
3. Trocar o estado para Livre, depois Fechada. A contagem da técnica acompanha o estado; os limites não aumentam por causa do cadastro. A classificação Livre de uma entidade continua pertencendo à posição dela, independentemente do estado dessa Família na técnica.
4. Alterar F157/F158. O resumo da FICHA AMALDIÇOADA acompanha os limites. Exceder o total disponível mostra aviso e saldo negativo; limpar CAMPANHA restaura os números do livro.
5. Repetir o nome no segundo cartão, inclusive variando maiúsculas/minúsculas. Os dois cadastros mostram aviso e saem do catálogo. Um nome igual ao de uma Família do livro também é inválido. MESTRE VIU é somente lembrete; não concede aprovação.
6. Digitar descrições longas nos dois cartões. A altura compartilhada precisa acomodar ambos. Apagar a maior deve conservar o espaço da vizinha; limpar as duas deve devolver as quatro linhas a **25 pixels cada**, como no desenho original.
7. Repetir texto longo e limpeza na descrição J4024, da Família318. Conferir também o menu de estado e a caixa de seleção do último cartão.
8. Restaurar todos os valores guardados. Nenhum nome, texto, estado ou limite de teste deve permanecer.

## Evidências desta etapa — 15/10/2026

- 31 verificações focais: catálogo, nomes literais com curingas, duplicatas, estados/caixas inválidos, limites e preservação das chaves anteriores.
- Oito cenários mecânicos no Sheets, com 18 entradas restauradas e relidas sem diferenças.
- Todos os 318 checkboxes, 318 menus de estado e 108 menus de Família das entidades conferidos; 3.843 mesclagens novas verificadas.
- Textos nativos de 2.303 e 3.423 caracteres testados. Primeiro cartão: quatro linhas de101px; último: quatro linhas de177px. Limpeza devolveu ambos a25px, exatamente como antes. Os três campos de descrição usados no teste ficaram vazios.
- ANALISE inteira relida após a restauração: 9.082 chaves, nenhuma diferença nas quatro colunas e nenhum erro. Formato8; leitor local testado. As escolhas de perícia ainda vazias geram o aviso esperado da ficha em branco.
- Oito arquivos da integração salvos e comparados integralmente depois de recarregar o editor. Conferência visual: limites, primeiro/último cartão, texto longo, carteira com foto e seletor de paleta, grupo7 e nove vagas da invocação. Corrigidas24notas antigas que ainda diziam sete vagas.

As provas e capturas ficam em `../evidencias-3b/criacao-familias-*`. A bateria de montagem conserva175verificações distribuídas nas fases principal, acabamento e continuação; consulte os registros/arquivos de saída para distinguir execução completa de interrupção externa.

## Ainda pendente na 3c

Integrar os moldes já aprovados de Forma, aptidão/Bênção, Talentos, tipo de entidade, condição e dano. Melhorias e Restrições estão integradas na cópia de teste e na revisão. Os13arquivos foram salvos e comparados integralmente após recarga; a correção focal do gatilho encontrada no teste de limpeza do último cartão também foi salva, conferida e aprovada no reteste nativo. As opções gratuita/consome escolha e combinação independente de vida/talismã/reserva de PE estão aprovadas. Autonomia e alma continuam por invocação. Capacidade, custo nativo integral e reunião/limpeza final da interface ainda não estão fechados.

## Melhorias e Restrições — 16/10/2026

[Cópia nativa descartável](https://docs.google.com/spreadsheets/d/1D215acC6Dxhu8i7x0aF7pmiNbJ95_U1CiH4980QozLk/edit#gid=47001). Criada da revisão pelo Drive, sem importar Excel. Migração pontual, sem executar construir().

Primeira Melhoria: CONFIGURAÇÃO B4037 (nome), E4038 (base), E4039 (Família), E4040 (Peso), E4041 (TR), B4044 (requisitos), B4050 (efeito), F4035 (MESTRE VIU). Última: cartão da linha 14277, nome B14281. Primeira Restrição: cartão da linha 14306; nome B14310, base E14311, devolução E14312, frequência E14313. Última: cartão da linha 18640; nome B18644, base E18645, devolução E18646, frequência E18647.

1. Guardar os valores anteriores. Cadastrar um nome único com base Rápido; deixar os demais campos vazios. Selecionar o nome no cartão existente da Ficha Amaldiçoada e comparar preço, ação, alcance e avisos com outro cartão usando Rápido do livro.
2. Repetir a comparação com Longe, Muito Longe, Reação, Toca a Alma, Inescapável e Prende. Conferir o alcance de Classe 0 e uma habilidade da entidade. Rajada deve conservar a regra de classe reduzida da entidade.
3. Criar uma Melhoria sem base, com Peso e TR. Testar Família custom no nono espaço de duas entidades: o menu deve abrir apenas onde ela foi escolhida. O estado Livre da técnica não concede esse desconto à entidade.
4. Usar nomes com curingas literais. Duplicar um nome, inclusive mudando maiúsculas/minúsculas; testar base, Peso e caixa de seleção inválidos. Os registros problemáticos devem mostrar aviso e sair do catálogo, sem cobrar as caixas vazias.
5. Criar Restrição com base Atrasar e comparar com o livro. Duas Restrições de frequência devem gerar aviso; devoluções não pagam a Forma. Testar também a última vaga de ambos os tipos.
6. Conferir bordas, notas, checkboxes, menus e herança nos primeiros e últimos cartões. O lado vazio do último par não é um cadastro adicional. Após salvar os scripts, testar textos longos nos dois cartões vizinhos e a limpeza, conservando o piso de 25 pixels.
7. Restaurar e reler todas as entradas. Conferir a ANÁLISE e varrer erros nas fichas e tabelas de apoio.

Provas já concluídas: 54 verificações locais; 15 pares base/custom iguais em 17 campos no Google; 566 consultas nativas, sem erros. Os 16 valores que diferem da calculadora focal pertencem aos mesmos pares de invocação, por causa das Famílias Livres presentes na cópia nativa. Todas as 395 entradas temporárias foram restauradas com igualdade integral. Nenhum erro de fórmula nas 13 abas verificadas. ANÁLISE 9: 18.948 chaves únicas e 75.796 células iguais ao modelo. Evidências em `../evidencias-3b/pecas-*`.

## Fechamento em andamento · 16/10/2026

Revisão migrada pontualmente em66lotes. Guarda de4270fórmulas anteriores passou;13808valores/fórmulas anteriores preservados,1184menus atualizados e somente o cabeçalho B4031 acrescentado em uma célula vazia. ANALISE9 da própria revisão:75796células,18948chaves únicas, zero diferenças;13abas sem erros.

Regressão focal final54OK. Montagem:22ordens de carregamento,19ausências e150checagens de fluxo em3fases passaram. Os13arquivos da etapa foram salvos no Drive e relidos integralmente.

Textos reais:2401 e3545caracteres nos cartões vizinhos; altura110/186px por linha, vizinho preservado ao apagar um lado, ambos voltaram a25px na limpeza. Última Restrição:2755caracteres inteiros,7linhas de68px. Todos os3campos temporários e suas notas restaurados exatamente. A limpeza do último cartão excedeu30s e não encolheu; correção focal em Codigo.gs reduz os limites do evento a4leituras para1219grupos. regressao-textos-custom.js passa7cenários, incluindo alturas exatas, limpeza e custo constante de leitura. Correção salva e relida integralmente em outra sessão. Reteste nativo curto/longo/limpeza:25/68/25px nas sete linhas, com execuções concluídas em18,769/12,998/11,862s. Todos os3campos temporários e notas restaurados exatamente; provas pecas-textos-correcao-final.json e pecas-textos-restauracao-conferida.json.

Validação encerrada. Processo pausado conforme pedido do usuário; não iniciar Formas nesta rodada.

Leitor completo encerrado com `python3 ler-analise.py --teste`: retorno0,18.948chaves, formato9 e TESTE:OK. A ficha vazia mantém somente o aviso esperado de escolhas de perícia/ofício. Prova: ../evidencias-3b/pecas-leitor-final.json. Nenhum teste ficou em execução na pausa.
