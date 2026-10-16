# B47 · roteiro nativo de bônus e mudanças

[Cópia de revisão](https://docs.google.com/spreadsheets/d/1EdEXzFRL8n21dLb60lxE2wbP4PFxFUiBdw7BiTTkNg0/edit?gid=47001#gid=47001), feita diretamente da ficha do servidor, sem importar Excel. A oficial permanece intacta. As três primeiras linhas trazem exemplos; somente o bônus de Defesa está ligado. O Buff/Debuff de Defesa foi restaurado para 0.

| Passo | Ação | Resultado esperado |
|---|---|---|
| 1 | Abra a CARTEIRA e as demais abas visíveis. | Moldura da foto, imagens, larguras, caixas, agrupamentos e seletor de paleta preservados. |
| 2 | Na CONFIGURAÇÃO, desligue B11. | Defesa volta para 11 nesta cópia em branco. |
| 3 | Ligue B11 e escreva 3 no Buff/Debuff de Defesa (FICHA!L59). | Defesa 16: 11 + 3 + 2. |
| 4 | Ligue B12, a troca de Defesa por 0. | Defesa 0, mesmo com o bônus e o Buff/Debuff ligados. |
| 5 | Crie uma segunda troca ligada para Defesa. | Aviso de conflito; Defesa fica em #N/A, sem escolher uma troca arbitrariamente. |
| 6 | Desligue a segunda troca e escreva `zero` no valor da primeira. | Aviso de entrada inválida; o texto não é tratado como 0. |
| 7 | Edite uma caixa calculada da CONFIGURAÇÃO, por exemplo F46. | O gatilho simples devolve a fórmula. Entradas B:G continuam editáveis. |
| 8 | Troque a paleta na CARTEIRA. | A CONFIGURAÇÃO permanece em Mizuki Escuro; a ANALISE permanece neutra. A troca das demais abas continua conforme a ficha já fazia. |
| 9 | Exiba a ANALISE pelo menu de abas. | 5.274 chaves únicas, formato 4: 5.156 anteriores e 118 de campanha, XP, vida e sequelas. Oculte-a novamente depois. |
| 10 | Restaure os exemplos e o Buff/Debuff para 0. | Só B11 ligado; Defesa 13; sem aviso de efeito. |

Somar aceita valores negativos e decimais. Trocar por fixa o valor final da caixa. Duas trocas ligadas da mesma caixa são conflito; uma linha desligada não afeta a conta.

Uma caixa de seleção apagada também conta como desligada. Um texto estranho no lugar do estado lógico continua gerando aviso, para não ser tratado como uma marcação válida.

## Contrato com o bot

Cada efeito tem seis chaves: `efeito.N.ligado`, `.caixa`, `.como`, `.valor`, `.tipo_de_fonte`, `.fonte`, com N de 1 a 30. A parte é `configuração`. Os diagnósticos são `aviso.efeito.N` e `aviso.efeito_caixa.<caixa>`.

A ANALISE 2 já está no `main` do gerador e nas cópias de validação do bot. A base do servidor consultada nesta rodada ainda tinha formato 1 e 2.650 campos. A cópia de revisão preserva sua apresentação e recebe o contrato mais recente com efeitos e regras de campanha, formato 4. O bot precisa reconhecer e conferir esses efeitos antes de esta etapa ser publicada para jogadores.

Conteúdo custom e automatização das exceções de Origem continuam em etapas separadas.

## Parte 2 · campanha

Testar apenas na cópia; guardar e restaurar todos os valores originais.

1. CAMPANHA E46:E59 vazia usa LIVRO, inclusive nível inicial 2. O comparador local deve dar IGUAIS à parte 1.
2. Nível inicial E46 = 5 e custo de saída do nível 5 E69 = 700: XP acumulado do nível 5 é 0 e do nível 6 é 700. O custo 1→2 exige definição da campanha se ela começar no nível 1; vazio aparece Pendente.
3. Cada regra altera só a conta correspondente. Zero é explícito; texto inválido não vira zero e produz aviso.
4. Vida rolada E59 = Sim, Caminho Vanguarda, nível 4, Constituição 3, Buff 5 e dados 5/4/6: vida máxima 40. Vida inicial 8 + Constituição 12 + dados 15 + Buff 5. Dado ausente/999 dá aviso e #N/A. Trocar por continua fixando o resultado final.
5. Prazo 5, uma caixa de Sequela e extras 2: próxima queda dispõe de 2 rodadas. Descanso curto conserva as sequelas; longo limpa caixas e extras.
6. ANALISE 4: 5.274 chaves únicas, preservação das 5.156 anteriores, sem erros de fórmula. Regras e rolagens constam no contrato.
7. Restaurar entradas, efeitos de exemplo e resultados temporários. Inspecionar as grades de regras, XP, vida e o campo de extras. CONFIGURAÇÃO permanece Mizuki Escuro e o lado J:O fica reservado ao custom.

Validação local: regressao-campanha.py (13 cenários), comparar-ficha-01.py, conferir-ficha-xlsx.py, regressao-construir.js, regressao-configuracao.py, regressao-paleta.js e ler-analise.py --teste. O rodar-tudo.sh agora inclui a regressão de campanha; sua bateria integral de 21 não foi repetida nesta etapa.


## Parte 3a · custom e correção R52

Contrato atual: formato 5, 6.174 chaves; 25 cartões em J:O, oito tipos. Os trechos acima descrevem as etapas anteriores.

1. Custom vazio: todos os valores preexistentes devem continuar IGUAIS à parte 2. Confira carteira, foto, paleta e grades em todas as abas visíveis. CONFIGURAÇÃO não acompanha troca de paleta e não congela linhas.
2. Cadastre Arma (Porrete, 1 mão, Concussão, Versátil, 1d6, Força 4, Volume 1,5), Escudo (Proteção 4, teto 1, Força 4, Volume 2), Uniforme (Grau 4, Proteção 3, teto 2, Força 4, Volume 2) e Item (Volume 0,7). Duas armas somam Volume 3; três itens somam 2,1.
3. Vanguarda nível 10, Força/Destreza/Constituição 3, Buff de Defesa 2, arma + escudo + uniforme acima: Proteção 7, Defesa 20, deslocamento 4,5 m por falta de Força. Trocar Defesa por 0 prevalece sobre tudo.
4. Ferramenta baseada na arma conserva dano/treino. Volume 0 explícito vale zero; volume vazio herda a base. Grau/estigma/desgaste aparecem no inventário e podem ser ajustados na instância. Ferramentas de uniforme e de item também conservam os cálculos da base.
5. Origem sem base: quatro perícias distintas e quatro rotas disponíveis. Marcial sem energia altera os três indicadores e conserva os PE como Esforço (50 nesse cenário). Ofício/CE4 podem nascer do cartão e continuar editáveis na ficha.
6. R52: marcante própria vinculada a Latente é inválida e não entra no menu. Vinculada a Restrição corporal é válida. Origem do zero aceita marcante própria; trocar sua base para Latente invalida essa marcante e passa a oferecer Tentativa e Erro. Menor própria vinculada a Latente continua válida. Menores com exigência respeitam a marcante da Origem/base.
7. MESTRE VIU desligado não bloqueia o cadastro. Nome repetido com livro/custom, campo fechado desconhecido, número em texto, base/rota incompatíveis e vínculo inexistente geram aviso e deixam o cadastro inválido. Trocar tipo exige revisar/apagar campos não utilizados.
8. Selecionar capacidade válida devolve a fórmula do texto quando havia texto manual. Capacidade inválida ou nome avulso conserva o texto manual. Menus de equipamentos/itens permitem digitação livre; marcante usa lista estrita com as permissões da R52.
9. Restaure todas as entradas de teste. Confirme 6.174 chaves únicas, nenhum erro de fórmula e os 4.904 valores/fórmulas não vazios do DADOS_CUSTOM iguais ao gerador nativo. Não importar XLSX, não executar construir na cópia preenchida, não publicar na oficial.

Evidências da correção: ../evidencias-custom/testes-nativos-r52.json, regressao-custom-03-r52.log, conferir-ficha-02-r52.log, regressao-construir-03-r52.log, regressao-pessoal-02-r52.log e scripts-salvos-r52.json. Os dados temporários foram restaurados após cada cenário nativo. A bateria integral e o arnês de 114 mutações da parte 1 não foram repetidos.


Fechamento para teste do usuário (15/10): montagem nativa autorizada concluída na cópia descartável da base, sem importar XLSX. Detectado timeout na instalação individual de menus; CONFIGURAÇÃO agora usa gravação de validações em matriz. Geração09 e regressao-construir04 aprovadas. Retomada final: 289.568 ms; menus: cerca de 67,5 s. Caminho concluído em três execuções: 667.506 ms (não inclui tentativas com falha nem intervalos entre retomadas).

Na montagem final: 13 abas/17 faixas sem erros de fórmula, 204 menus/55 checkboxes/175 seletores estritos de CONFIGURAÇÃO conferidos. Defesa 20, Proteção 7, deslocamento 4,5 m, volumes 3 e 2,1; troca por zero, restrição da marcante herdada e 50 Pontos de Esforço passaram. As 121 entradas temporárias foram restauradas e relidas, sem diferenças. DADOS_CUSTOM tem 4.904 entradas iguais ao gerador; ANALISE mantém 6.174 chaves únicas. Revisão visual das áreas registradas em ../evidencias-custom/montagem-*.png, incluindo carteira/foto/paleta, recursos/sequelas, inventário, regras/XP/vida e cartões, sem bordas quebradas nas vistas inspecionadas.

Helper removido e Código.gs relido após recarregar editor independente, igual ao local. Maior .gs: 806.439 bytes (teto 900 KiB). Evidência consolidada: ../evidencias-custom/fechamento-montagem-base-r52.json. O descartável é evidência de construção e conserva o script antigo copiado da oficial; a execução usou o gerador atual do projeto da revisão. Testar manualmente na cópia de revisão vinculada no início, que tem os dez scripts atuais. Não executar construir nela. Partes 3b/3c aguardam teste de 3a pelo usuário.


## Teste delegado pelo usuário · 15/10/2026

Usuário pediu que o agente fizesse o teste e seguisse. Roteiro focal repetido na revisão: arma/escudo/uniforme/item, Defesa 20, Proteção 7, deslocamento 4,5 m, volumes 3/2,1, troca por 0, Latente invalidando marcante própria, Origem sem base permitindo, rota sem energia com 50 PE, ferramenta herdando arma com volume 0 explícito, menor com texto e nome duplicado invalidado. As 156 entradas foram restauradas e relidas: nenhuma diferença. Auditoria posterior de 13 abas/17 faixas: zero erros de fórmula. Sem nova montagem ou bateria integral desnecessária. Evidência: ../evidencias-custom/teste-delegado-3a.json.

Próximo: aprovação do desenho da aba ESTUDO 3B e integração por etapas; ver ESTUDO-CUSTOM-3B.md.


## Parte 3b · roteiro e fechamento em 15/10/2026

Testar somente em cópia nativa; nunca importar XLSX ou rodar construir sobre ficha preenchida. Contrato atual: ANALISE 6, 7.387 chaves. A oficial permanece intacta.

1. CONFIGURAÇÃO a partir da linha 737: cadastre Caminho e Trilha, com BASE DO LIVRO opcional. Nos registros curtos a partir de 877, crie Perícia Rituais Urbanos (Essência) e Ofício Cartógrafo do Véu (Inteligência). Todas as opções fechadas usam lista.
2. Caminho: vida inicial 10, por nível 6, dado d8, PE por nível 7, Força/Constituição, Rituais Urbanos/Acrobacia, troca por arma Sim, categoria selecionada Yumi. Nível 5, Constituição 3: vida 49 e PE 35. Selecionar pelo menu marca as duas perícias e treina somente a categoria permitida.
3. Essência 4, Inteligência 2, Maestria 1: perícia treinada 5 e ofício especializado 3. Contam nos orçamentos existentes. Efeito trocar por 0 fixa o total em 0.
4. Vida rolada Sim, resultados 8/4/6/2: vida 45; resultado 9 é rejeitado porque excede d8. Restaurar campanha vazia.
5. Trilha baseada em Múltiplas Invocações: 4 ativas e 4 famílias. Nenhuma permite alterar limites em BÔNUS E MUDANÇAS; troca de teto por 5 e +2 famílias produzem 5/5 neste cenário.
6. Duplicar o nome da perícia invalida os dois registros. Número em texto ou atributo inexistente gera diagnóstico e impede entrada no catálogo válido. Marcante publicada Tentativa e Erro continua disponível para Origem baseada em Latente.
7. A mesma perícia entra nos menus das entidades e da Ficha Amaldiçoada; o ofício aparece na entidade. Entidade com Essência 0 e Maestria 1 usa +1 para essa perícia.
8. Caminho usa2/7/15/23/30; Trilha2/11/19/27. Selecionar custom preenche os nove cartões existentes do grupo7. No nível5, a entrega2 aparece normal e a7 riscada, com “Abre no7”. Texto longo cabe inteiro no cadastro e no mesmo cartão da ficha. Editar o cadastro atualiza o automático; texto manual permanece com a referência atualizada na nota. Trocar livro↔custom não deixa o automático anterior preso nem apaga anotações. Não existe bloco duplicado no fim da ficha. Perícias23/Ofícios11 aparecem em duas colunas e duplicata cruzada invalida ambas.
9. Inspecione foto/paleta da carteira, abas principais, cartões longos/curtos e novos treinos. CONFIGURAÇÃO fixa; novas áreas da FICHA na paleta escolhida. Restaurar todas as entradas e reler sem diferenças.

Executado: testes nativos acima, regressao-progressao.py, regressao-construir.js com casos de texto longo, 122 verificações de paleta e leitor. A regressão 3a completa teve uma falha de FILTER da calculadora local; cenário equivalente passou no Sheets, sem alterar o teste para esconder a falha. A bateria integral de 23 validadores não foi repetida.

Montagem nativa: 14 abas e zero erros nas faixas auditadas; 188 checkboxes e 488 seletores da CONFIGURAÇÃO (575 células validadas). Duas execuções concluídas em 376.821 ms; uma falha inicial do serviço Google ficou registrada separadamente. Treze scripts de produção gravados/conferidos e helper removido. Capacidade final: 133 registros 3b, 158 com a 3a. Maior .gs: 837.710 bytes. Evidências em ../evidencias-3b/, especialmente montagem-nativa-3b-auditoria.json, testes-nativos-3b.json, teste-menus-entidades-3b.json, conferencia-area-nova.json e capturas visuais.


Gatilho final testado por edição real, depois de conferir o código salvo: Vanguarda 13,690 s (65 treinos), retorno ao custom 15,051 s (só Yumi e perícia fixa custom treinada). Ambos concluídos, sem limite de tempo. RangeList grava os booleans em lote; a regressão completa de construção passou novamente. Após o teste, entradas/notas das duas fichas e os 76 alvos originais foram relidos sem diferenças; áreas novas sem erros e três entradas das entidades/técnica vazias. Sem cenário ativo. Ver fechamento-3b-gatilho.json e tempos-onedit-final-completo.txt.


## Invocações · nove Famílias e autonomia individual

- Em cada entidade, abaixo de Aquisição, AUTONOMIA começa Autônoma. Mudar a primeira para Não autônoma deve somar uma Livre nova ao total aberto e manter a segunda Autônoma. Não deve alterar ALMA nem Integridade.
- Padrão: Autônoma 3 abertas/1 Livre; Não autônoma 4/2. Parceria ou Múltiplas: 4/1 → 5/2. Principal: 5/2 → 6/3.
- CONFIGURAÇÃO B133:G149 ajusta os ganhos, sem selecionar autonomia. CAMPANHA em branco usa o sistema. Livres fazem parte das abertas; ultrapassar nove ou ter mais Livres que abertas deve avisar.
- Selecionar Amparo na nona caixa deve liberar suas Formas/Melhorias. Repetir na oitava deve acusar duplicata. A categoria Livre indicada no rótulo deve aplicar o desconto correspondente.
- Preservar escolhas antigas 1–7 e texto/nota da Definição. Verificar nove menus em cada uma das 12 entidades e uma linha vazia acima da Definição.
- Nota deve dizer regra do sistema prevista para o Guia de Criação, padrão Autônoma, ganho e necessidade de ordem prévia (exceto Reação).
- Regressão focal: python3 regressao-familias-invocacao.py. Artefatos de cálculo são locais e jamais importados no Google.
