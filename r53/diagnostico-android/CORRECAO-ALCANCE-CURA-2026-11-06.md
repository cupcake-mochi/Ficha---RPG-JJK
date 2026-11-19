# Alcance de cura e PV temporários · 06/11/2026

Base PR72 em `b7c06b0`. A regra foi conferida na R66 em
`JJK---Project@e3058ad29180fdec2efec75b512446c49bf87b3d`, seções
Formas e Alcance e área. A auditoria anterior está em
`AUDITORIA-ALCANCE-CURA-2026-11-06.md`.

Nos 36 resumos dos feitiços comuns do personagem, o alcance de
cura e PV temporários vem de `alcance_beneficio`. Quando o feitiço
também causa dano e as medidas são diferentes, os rótulos
identificam cada distância. Quando as medidas coincidem, como em
Toque e Aura, o cartão exibe a medida compartilhada uma vez.

O delta conserva as funções, as montagens, o alcance ofensivo,
a área, a base Média de cura, a alocação de pontos e o custo de PE
com Integridade. Trunfos, invocações e Classe 0 mantêm seus resumos
próprios. A tentativa preliminar com Liberação confirmou que os
campos de cura e PV temporários estão desabilitados nesse cartão.
Os três resumos de Liberação foram retirados do delta e relidos
iguais à PR72 nas duas cópias.

## Ensaio nativo

Dez cenários por descartável, Era e Ciclo, com resultados iguais:

- Classe 3 em Projétil. Cura isolada e PV temporários isolados
  mostraram 9 m. Dano isolado mostrou 18 m.
- Dano e cura na Classe 3 mostraram “Dano 18 m · Cura 9 m”.
  No estágio 2, dano, cura e PV temporários mostraram “12 PE ·
  Dano 18 m · Cura/PV temp. 9 m”.
- Cura isolada de Classe 6 mostrou 18 m. Toque mostrou 1,5 m
  e Aura conservou a origem no conjurador e raio de 3 m.
- A cura com Guarda conservou a base e o preço da peça.
  Alocar acima do saldo continuou gerando o aviso de revisão.

No ensaio preliminar, elevar o nível mantendo uma Integridade
absoluta alterou o estágio. A bateria final usa o máximo recalculado
na condição inteira e a metade desse máximo no controle do estágio 2.

Código e Editor foram salvos e relidos integralmente nas duas
cópias. Após apagar `FICHA AMALDIÇOADA!D81` pela interface, o
Apps Script devolveu a fórmula nova e os dois alcances em ambas.

Entradas temporárias repostas. Foram comparadas 723 células por
cópia, incluindo 518 posições de MONTAGENS e os três resumos de
Liberação. Somente as 36 fórmulas previstas diferiram, com notas e
validações preservadas e sem erros nos intervalos relidos.
Evidência privada em `nuvem-b47/saidas/correcao-alcance-cura/`.

## Preparação incremental

Geração `a00e1dcd00966e8b`. O preparador `preparar_alcance_cura.js`
exige as versões de Código e Editor ensaiadas na PR72 e compara as
36 fórmulas do snapshot antes de montar pedidos de
`userEnteredValue`. O plano inverso recusa fórmulas divergentes.
Uma eventual promoção exige snapshot atualizado e verificação de
compatibilidade. A comparação do pacote integral regenerado conferiu
280.001 posições e os metadados de 26 abas. As únicas diferenças de
valores foram as 36 fórmulas previstas.

O Editor conserva os 251 contextos e atualiza a recuperação dos
36 resumos. A rota de recuperação do módulo e a assinatura do atalho
usam as fórmulas novas. Código e Editor relidos nas descartáveis:

- Código `5c8c7493600367d4c004c3c85a4cc0f5e82459ec4cb4a54ccdb1c769741e3a2c`.
- Editor `aa77309cb42e08f49dbe1f427c72b0c68ec6168fbf6b2294d4d3555a7a7b5c09`.
