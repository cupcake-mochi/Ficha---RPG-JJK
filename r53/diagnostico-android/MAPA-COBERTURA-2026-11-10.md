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
| Vida máxima e Bloquear | Conferida | AUDITORIA-VIDA-CORPOS, CORRECAO-VIDA-BLOQUEAR | `vida_bloquear_molde.js` falha desde antes da PR96 e está fora do smoke |
| Vida e energia temporárias, caixa ± | Conferida | AUDITORIA-RESERVAS, MAXIMOS-ZERO, CORRECAO-FILA-RECURSOS, TEMP-COLAGENS | rajada de mais de dois eventos ainda pode perder entrada (limite do Google, documentado) |
| Integridade, estágios, Exaustão, deslocamento | Conferida | INTEGRIDADE-MOVIMENTO, DESLOCAMENTO-CORPORAL, AUDITORIA-CONJURACAO-INTEGRIDADE | — |
| Morrendo, socorro, cura do Exaurido | Conferida | AUDITORIA-MORRENDO, SOCORRO, CURA-EXAURIDO | Android não testado (CURA-EXAURIDO) |
| Descanso | Conferida | AUDITORIA-DESCANSO-ORIGENS, DESCANSO-EVENTO-REPETIDO | — |
| Defesa, equipamento, mãos, carga | Conferida | AUDITORIA-EQUIPAMENTO, AUDITORIA-PASSIVAS-ORIGEM | — |
| Conjuração e teto por Integridade | Conferida | AUDITORIA-CONJURACAO-INTEGRIDADE | — |
| Buff/Debuff (os 11 campos) | Conferida | CORRECAO-BUFF-DECIMAL | caixa B/D mostra "B/D 2" para 1,5 (só visual) |
| Iniciativa, CD de feitiço, ataque corpo a corpo e à distância | Conferida (10/11) | AUDITORIA-COMBATE-JOGADOR | menu de atributo vazio ou sem acento dá #N/A (decisão do Mizuki) |
| Perícias (23) | Parcial | AUDITORIA-CONSOLIDADA: 69 casos no Sheets em 04/11 | sem colagem de texto ou valor fora do menu |
| **Testes de Resistência do jogador** | **Nunca olhada** | só os das entidades foram conferidos | treino, maestria e TR treinado do jogador |
| **Ofícios (11)** | **Nunca olhada** | nenhuma auditoria | contagem, atributo e treino |
| Travas da criação do jogador (pontos, atributos) | Conferida (10/11) | CORRECAO-PONTOS-FICHA (PR98) | — |
| Montagem de feitiço, custo, Classe, Formas, Famílias | Conferida | 89 casos do motor R53 e as auditorias de 06/11 e 07/11 (alcance, cura, tempo, Rajada, Frágil, Fica, Sem Volta, devoluções, restrições, forma e função, Mira/Corrói) | — |
| Classe 0 e Prática Cotidiana | Conferida | AUDITORIA-CLASSE-ZERO, CORRECAO-PRATICA-COTIDIANA | — |
| Repertório normal e das Trilhas | Conferida | AUDITORIA-REPERTORIO-NORMAL, AUDITORIA-REPERTORIO-TRILHA | — |
| Liberações Máximas | Conferida | CORRECAO-LIBERACOES | — |
| Caminhos e Trilhas | Parcial | testes locais `caminho_*` (smoke) | sem auditoria no Sheets |
| Origens, passivas, recursos, imunidades | Conferida | AUDITORIA-ORIGENS-RECURSOS, AUDITORIA-PASSIVAS-ORIGEM, BENCAOS-IMUNIDADES, IMUNIDADE-CUSTOM, MENU-ORIGEM-INVALIDA | — |
| **Talentos e Aptidões** (requisitos e vagas) | **Parcial, fraco** | testes locais `test_motor` e o recurso "Talentos grátis" de 03/11 | nenhuma auditoria dos requisitos no Sheets |
| Condições (13) | Manual por desenho | só Morrendo, Exaurido, Exaustão e Envenenado aparecem nas auditorias | nada, a menos que o Mizuki queira automatizar |
| Progressão e XP | Parcial | `xp_atualizar`, `xp_nivel` (local) | sem auditoria no Sheets |
| CONFIGURAÇÃO e campanha (vida rolada, ajustes) | Parcial | só tocada pela PR96 (leitura do Buff) | sem auditoria dedicada |

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
| `vida_bloquear_molde.js` | falha (não descasca a camada das bênçãos); fora do smoke |
| `menu_origem.js` | falha no histórico (B01, `Socorro.gs` não existia no commit antigo); o `menu_origem_molde.js` cobre |
| `cartas_custom.js`, `marcas_custom.js` | saem com código 0, mas pulam sem a ficha exportada: não rodam de verdade |
| `regressao-kaori-na-ficha.py` | precisa do LibreOffice e não está no smoke; o `conferir-kaori.py` do smoke confere só o catálogo |

## O que eu atacaria primeiro

Ordem sugerida, pelo tamanho do estrago se o erro existir:

1. ~~**Travas da criação do jogador.**~~ Feito na PR98. O mesmo tipo de erro achado nas entidades (colagem passando por cima do menu)
   provavelmente existe na FICHA, que é a mais usada.
2. ~~**Iniciativa, CD e ataques.**~~ Auditado em 10/11 (AUDITORIA-COMBATE-JOGADOR). São números de toda rodada de combate, e o único teste é a Kaori, fora do smoke.
3. **TR e ofícios do jogador.** Foram conferidos nas entidades e nunca no jogador.
4. **Talentos e Aptidões.** Requisito errado deixa montar personagem ilegal sem aviso.
5. **Consertar os testes quebrados ou pulados**, para o smoke voltar a provar o que diz.
