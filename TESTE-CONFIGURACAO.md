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
