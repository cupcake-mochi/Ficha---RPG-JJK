# Mapa de cobertura do pente-fino · 10/11/2026

Pedido do Mizuki depois da PR96: saber o que já foi conferido na ficha e o que nunca foi olhado, para a próxima
rodada ir direto no que falta.

**Como foi feito.** Li as auditorias, correções e revisões de `r53/diagnostico-android/` (04/11 a 10/11) e a
lista de testes do smoke (`nuvem-b47/conferir.py`). Cruzei com as 26 abas do modelo e com as mecânicas da
`ESPECIFICACAO-ficha-digital.md`. A busca foi por nome de mecânica, campo e aba. Este mapa **não é certificação**:
mostra onde houve olhar dedicado, não que a área está livre de erro.

## Legenda

- **Conferida:** teve auditoria dedicada, com ensaio no Sheets, e os achados foram corrigidos.
- **Parcial:** só teste local, ou auditoria de um recorte da área.
- **Nunca olhada:** nenhuma auditoria dedicada encontrada.
- **Manual por desenho:** a ficha não automatiza a área, então não há o que conferir na fórmula.

## Ficha do jogador (FICHA, FICHA AMALDIÇOADA, FICHA PESSOAL)

| área | estado | onde foi olhada | o que falta |
|---|---|---|---|
| Vida máxima e Bloquear | Conferida | AUDITORIA-VIDA-CORPOS, CORRECAO-VIDA-BLOQUEAR | — (`vida_bloquear_molde.js` consertado e no smoke em 11/11) |
| Vida e energia temporárias, caixa ± | Conferida | AUDITORIA-RESERVAS, MAXIMOS-ZERO, CORRECAO-FILA-RECURSOS, TEMP-COLAGENS | rajada de mais de dois eventos ainda pode perder entrada (limite do Google, documentado) |
| Integridade, estágios, Exaustão, deslocamento | Conferida | INTEGRIDADE-MOVIMENTO, DESLOCAMENTO-CORPORAL, AUDITORIA-CONJURACAO-INTEGRIDADE | — |
| Morrendo, socorro, cura do Exaurido | Conferida | AUDITORIA-MORRENDO, SOCORRO, CURA-EXAURIDO | Android não testado (CURA-EXAURIDO) |
| Descanso | Conferida | AUDITORIA-DESCANSO-ORIGENS, DESCANSO-EVENTO-REPETIDO | — |
| Defesa, equipamento, mãos, carga | Conferida | AUDITORIA-EQUIPAMENTO, AUDITORIA-PASSIVAS-ORIGEM | — |
| Conjuração e teto por Integridade | Conferida | AUDITORIA-CONJURACAO-INTEGRIDADE | — |
| Buff/Debuff (os 11 campos) | Conferida | CORRECAO-BUFF-DECIMAL | — (14/11: decimal deixa a caixa B/D das invocações âmbar, CORRECAO-AVISO-DECIMAL-BD) |
| Iniciativa, CD de feitiço, ataque corpo a corpo e à distância | Conferida (10/11) | AUDITORIA-COMBATE-JOGADOR, CORRECAO-AVISO-ATRIBUTO | — |
| Perícias (23) | Conferida (11/11) | AUDITORIA-CONSOLIDADA: 69 casos no Sheets em 04/11; CORRECAO-OFICIOS-TR, CORRECAO-ESPECIALIZACAO e CORRECAO-TEXTO-EXTRA (11/11) | especialização sem treino, sem marco de Corpo e texto no Extra ou em Trein/Espec avisam na caixa desde 11/11 |
| Testes de Resistência do jogador | Conferida (11/11) | CORRECAO-OFICIOS-TR, CORRECAO-TEXTO-EXTRA | Físico com menu fora de FORÇA/DESTREZA e texto no Extra avisam desde 11/11 |
| Ofícios (11) | Conferida (11/11) | CORRECAO-OFICIOS-TR, CORRECAO-ESPECIALIZACAO, CORRECAO-TEXTO-EXTRA | padrão do livro, aviso de atributo, especialização sem treino e texto no Extra ou em Trein/Espec consertados |
| Travas da criação do jogador (pontos, atributos) | Conferida (10/11) | CORRECAO-PONTOS-FICHA (PR98) | — |
| Montagem de feitiço, custo, Classe, Formas, Famílias | Conferida | 89 casos do motor R53 e as auditorias de 06/11 e 07/11 (alcance, cura, tempo, Rajada, Frágil, Fica, Sem Volta, devoluções, restrições, forma e função, Mira/Corrói) | — |
| Classe 0 e Prática Cotidiana | Conferida | AUDITORIA-CLASSE-ZERO, CORRECAO-PRATICA-COTIDIANA | — |
| Repertório normal e das Trilhas | Conferida | AUDITORIA-REPERTORIO-NORMAL, AUDITORIA-REPERTORIO-TRILHA | — |
| Liberações Máximas | Conferida | CORRECAO-LIBERACOES | — |
| Caminhos e Trilhas | Conferida contra o R66 (11/11) | AUDITORIA-CAMINHOS-TRILHAS | as cinco cartas "por combate" passaram a "por cena" em 12/11 (CORRECAO-FREQUENCIA-CENA); texto da ficha na redação do R53 (decisão do Mizuki) |
| Origens, passivas, recursos, imunidades | Conferida | AUDITORIA-ORIGENS-RECURSOS, AUDITORIA-PASSIVAS-ORIGEM, BENCAOS-IMUNIDADES, IMUNIDADE-CUSTOM, MENU-ORIGEM-INVALIDA | — |
| Talentos e Aptidões (requisitos e vagas) | Conferida (11/11) | CORRECAO-OFICIOS-TR, testes `test_motor`, "Talentos grátis" de 03/11 | limite: "aptidões a mais no teto" supõe a ordem de Refino mais favorável |
| Condições (13) | Manual por desenho | só Morrendo, Exaurido, Exaustão e Envenenado aparecem nas auditorias | nada, a menos que o Mizuki queira automatizar |
| Progressão e XP | Conferida contra o R66 (12/11) | AUDITORIA-PROGRESSAO-XP, `xp_atualizar`, `xp_nivel` | curva, missões e limiar batem; ensaio do limiar e do feito na QA da Era; um nível por missão corrigido em 12/11 (CORRECAO-TRAVA-NIVEL-MISSAO); corte do XP abaixo de 25 em 12/11 (CORRECAO-CORTE-XP-25, `corte_xp_missao`), que fecha o desconto do 7º em diante; XP congelado preso à linha em 12/11 (CORRECAO-XP-LINHA-CONGELADA, `xp_atualizar`, `xp_linha_congelada`; substitui o nome no registro do #109), instalado nas duas QAs e ensaiado no Ciclo |
| CONFIGURAÇÃO e campanha (vida rolada, ajustes) | Conferida contra o R66 (12/11); achados fechados (14/11) | AUDITORIA-CONFIGURACAO, CORRECAO-ACHADOS-CONFIGURACAO | números batem; ensaio da vida rolada no Ciclo; notas sem versão do livro, "Não autônoma" registrada como regra da casa, vida rolada com uma frase só |

## Invocações (INVOCAÇÕES, DADOS_INVOC)

| área | estado | onde foi olhada |
|---|---|---|
| Aquisição, nível obtido, Criação | Conferida | AUDITORIA-AQUISICAO-INVOCACOES, CORRECAO-CRIACAO-NIVEL-FIXO, CORRECAO-NIVEL-OBTIDO |
| Atributos, pontos e colagem | Conferida | REVISAO-PR90, REVISAO-PR91, REVISAO-PONTOS-FORCADOS |
| Perícias, treinos, TR | Conferida | AUDITORIA-PERICIAS-TREINOS-ENTIDADES, REVISAO-TREINOS-ENTIDADES |
| Buff/Debuff | Conferida | CORRECAO-COLAGEM-BUFFS, CORRECAO-BUFF-DECIMAL |
| Expansão da domada, trunfos, especiais | Conferida | AUDITORIA-EXPANSAO-DOMADA, AUDITORIA-TRUNFOS-ENTIDADES, CORRECAO-CONTAGEM-ESPECIAIS |
| Erros por nome | Conferida | REVISAO-PR88-ERROS-NOMES, CORRECAO-ISOLAMENTO-NOMES-PR88 |

Nas invocações não sobrou nenhuma área sem olhar dedicado.

## Fora do alcance desta fila

- **CARTEIRA, salários e missões:** só testes locais (2.709 + 95 + 49 verificações). O ensaio no Sheets mexe na
  PR31 e na Carteira viva, que estão fora dos limites.
- **ANALISE e contrato do bot:** testes de contrato no smoke. Mudança aqui mexe no `ANALISE12/esquema2`, que é
  preservado de propósito.
- **GLOSSÁRIO e catálogos (DADOS_*):** são texto e tabela. O catálogo é conferido pelo `conferir-catalogo.py` no
  smoke.

## Testes que não provam o que parecem

| teste | situação |
|---|---|
| `vida_bloquear_molde.js` | ~~falha~~ consertado em 11/11 e no smoke |
| `menu_origem.js` | ~~falha no histórico~~ reescrito em 11/11 (confere CP3 e CQ3) e no smoke |
| `cartas_custom.js`, `marcas_custom.js` | saem com código 0, mas pulam sem a ficha exportada: teste manual, precisa do `oficial-era.json` privado |
| `regressao-kaori-na-ficha.py` | precisa do LibreOffice e não está no smoke; o `conferir-kaori.py` do smoke confere só o catálogo |

## O que eu atacaria primeiro

Ordem sugerida, pelo tamanho do estrago se o erro existir:

1. ~~**Travas da criação do jogador.**~~ Feito na PR98. O mesmo tipo de erro achado nas entidades (colagem passando por cima do menu)
   provavelmente existe na FICHA, que é a mais usada.
2. ~~**Iniciativa, CD e ataques.**~~ Auditado em 10/11 (AUDITORIA-COMBATE-JOGADOR). São números de toda rodada de combate, e o único teste é a Kaori, fora do smoke.
3. ~~**TR e ofícios do jogador.**~~ Auditado e consertado em 11/11 (CORRECAO-OFICIOS-TR).
4. ~~**Talentos e Aptidões.**~~ Auditado em 11/11: requisitos batem com o R66.
5. ~~**Caminhos e Trilhas.**~~ Auditado em 11/11 contra o R66 (AUDITORIA-CAMINHOS-TRILHAS): números batem; as cinco cartas com frequência antiga foram corrigidas em 12/11.
6. ~~**Progressão e XP.**~~ Auditado em 12/11 contra o R66 (AUDITORIA-PROGRESSAO-XP): números batem; a trava de um nível por missão entrou em 12/11; o corte de 25 XP (12/11) resolveu o desconto do 7º em diante.
7. **Consertar os testes quebrados ou pulados.** Dois consertados em 11/11; sobram `cartas_custom`/`marcas_custom` (manuais) e a regressão da Kaori (LibreOffice).
