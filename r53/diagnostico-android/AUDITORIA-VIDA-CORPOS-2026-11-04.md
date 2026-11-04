# Auditoria nativa: vida máxima e Bloquear

Base examinada: PR52 em `600f4ec81f74d523e7b0f07598d6a60b2b8a6c12`.
Ramo separado de auditoria. Este documento registra defeitos reproduzidos;
não contém nem publica suas correções. Oficiais, jogador e PR31 não foram
alterados. A PR52 passou nos dois checks e foi retirada do rascunho, conforme
autorização do usuário; não houve merge.

## Método

Cópia nativa descartável derivada da QA de deslocamento. Recolocada em J26 a
fórmula de vida máxima extraída do GS desta base, pois a QA anterior tinha
vida máxima controlada em 23. Para Bloquear, colocada em D59 a fórmula de
Defesa do mesmo GS (correção da PR51), evitando atribuir o problema a um molde
de Defesa antigo. B126 era a fórmula de base corporal da PR51 e retornou TRUE.
Não foi instalado o pacote completo nem executada reconstrução.

Entradas alteradas pela API, com recálculo nativo e releitura de cada cenário.
Isso testa fórmulas e dependências, **não dispara onEdit**, troca de Caminho,
automação de descanso ou recuperação após apagar células. Sem importação Office.
A conferência visual de Bloquear foi feita na interface do Google Sheets.

Regra consultada: livro R65, commit
`a98d4af981cd7166a403f7189eeb1bc3a22e4ad4`, seções Corpo Quebradiço,
Corpo Debilitado e Corpo Exaurido. Resultados sanitizados no JSON ao lado;
respostas brutas e captura permanecem fora do Git.

## P1 — Vida máxima de Corpo Quebradiço não é reduzida

O livro determina metade da vida normal, arredondada para baixo, mínimo 1,
inclusive nos aumentos futuros. A fórmula de FICHA!J26 não consulta o corpo
nem a base corporal. O gerador `ficha-v01/configuracao.py::trocas` acrescenta
os ajustes numéricos à vida, mas só limita Defesa e Deslocamento pelos corpos.

Reprodução: Origem corporal publicada, Vanguarda em D11, Constituição T19=0,
nível AH11 e Buff P26 conforme tabela. Sem progressão por níveis customizada
(DADOS_CONFIG!S15 = Não). Configuração de vida sem ajustes nos seis primeiros
casos. A tabela de progressão fornece vida inicial 8 e ganho 5 por nível.

| Corpo | Nível | Buff | Esperado | Observado |
| --- | ---: | ---: | ---: | ---: |
| Quebradiço | 1 | 0 | 4 | 8 |
| Quebradiço | 2 | 0 | 6 | 13 |
| Quebradiço | 2 | 3 | 8 | 16 |
| Exaurido (controle) | 2 | 3 | 16 | 16 |
| Debilitado (controle) | 2 | 3 | 16 | 16 |
| Próprio (controle) | 2 | 3 | 16 | 16 |

Sétimo caso: Quebradiço, nível 2, Buff 3 e CONFIGURAÇÃO C11:F11 =
TRUE / Vida máxima / somar / 6. DADOS_CONFIG!B2 confirmou 6, sem conflito.
Esperado 11; observado 22. O erro também afeta as contas dependentes:
FICHA!D41 (Aguentar) mostrou 6 em vez de 3; O41 (primeiro Insistir) mostrou
8 em vez de 4. Não são dois defeitos independentes: usam o máximo incorreto.

Correção proposta para uma próxima entrega: aplicar a redução uma única vez
à vida normal calculada, reconhecendo base corporal válida. Preservar erros,
campos vazios, demais corpos e o contrato da ANALISE. Conferir expressamente
a semântica de `trocar por` antes de decidir se essa opção substitui a vida
normal ou a final. Não foi ensaiada aqui. Testar mínimo 1, progressão custom,
troca de Origem, descanso usando o novo máximo e atualização do molde.

## P2 — Bloquear oferece uma rolagem a corpos que não podem bloquear

FICHA!Z56 permanece `="2d10 + " & D59-11`, sem consulta ao corpo.
Com a Defesa corrigida para 0, Quebradiço, Debilitado e Exaurido exibiram
**2d10 + -11**. As três regras proíbem Bloquear para o corpo real.
O problema é a indicação de uma ação indisponível; não foi observado um
mecanismo de execução automática de ataques que concedesse a ação.

Correção proposta: substituir essa indicação por uma mensagem de
indisponibilidade somente com base corporal válida e esses três corpos.
Preservar a rolagem dos demais personagens e os intermediários com Defesa
própria. Atualizar gerador e molde de restauração juntos; testar controles
positivos e negativos, incluindo custom, antes de promover.

## Cobertura e revisão

Dez cenários nativos: sete de vida (quatro divergentes e três controles
corretos) e três de Bloquear (três divergentes). Duas contas dependentes
também foram relidas no cenário de bônus. Nenhum erro de fórmula foi
retornado nesses alvos; os defeitos são mecânicos, com valores calculados
normalmente. Não equivale a uma varredura completa de todas as abas.

Não ensaiados nesta rodada: acionamento de descanso, cura de Exaurido,
progressão customizada, `trocar por`, mínimo 1 e restauração dos futuros
consertos. O histórico da PR51/52 não substitui esses ensaios. A cópia é
um ambiente parcial de QA e não deve ser distribuída como ficha pronta.

Para revisar os achados: Sol/Medium. Para implementar e integrar correções:
Sol/High, conforme AGENTS.md, sem alterar configurações automaticamente.
