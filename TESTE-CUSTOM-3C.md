# Teste da parte 3c — Famílias

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

Integrar os moldes já aprovados de Forma, Melhoria, Restrição, aptidão/Bênção, Talentos, tipo de entidade, condição e dano. As opções gratuita/consome escolha e combinação independente de vida/talismã/reserva dePE estão aprovadas. Autonomia e alma continuam por invocação. Capacidade, custo nativo integral e reunião/limpeza final da interface ainda não estão fechados.
