# Ficha definitiva (24/10/2026)

> Atualização de 25/10: o usuário confirmou dois modelos oficiais. Consulte [OFICIAIS.md](../OFICIAIS.md) para os links atuais e a aplicação de Ritual. As informações abaixo registram a adoção anterior.

Base: cópia nova da Candidata A (`1427V3IO_RSToQcsO1ZgAeArXoT_PdoHukN9jAVkBfy8`), escolhida pelo Mizuki. A Original e a
Candidata A ficaram intactas.

- Planilha: `1MQqhHbIzzyoMQY5zLKOciiT5k9Y6AMI4MCSrPhu8V_k` ("Ficha R53 — definitiva (Android)")
- Apps Script: `1B6coyZOopuZb5encJpkAGalDcHUp5X4nwXc5hf9OkpNyTTEZWcVGrdtl`

## O que foi aplicado

1. Código: o projeto da cópia de teste (`18AEaLKY…`) foi comparado arquivo por arquivo com o da cópia nova. A única
   diferença eram as mudanças desta rodada (Codigo, manifesto com o serviço avançado Sheets, LotePaleta, SalarioLote);
   o conteúdo foi publicado igual ao testado. Backup do projeto anterior fora do repositório.
2. Pela API (sem gatilho): CONFIGURAÇÃO O66:O67 = 1 (missões solo), aviso novo da paleta em CARTEIRA!C29, caixa de ajuda
   em INVOCAÇÕES!AB2:AR4 nas cores da Blush clara (fundo #FFD1D1 = painel, texto #1D1616 = texto), chave `agenda`
   removida do estado em DADOS_SALARIOS!L2 (apontava para o script da Candidata A; gatilhos não vão na cópia).
3. Pelo Mizuki, no editor: `prepararSalarioLote`, `mapearLote`, `fixarBordasLote`, `fixarArteLote`.
4. EXTRATO!C2 renomeado para "Saldo inicial": os ¥ 150.000 são o dinheiro inicial de toda ficha (confirmado pelo Mizuki).

## Pente fino

- Varredura de texto (todas as abas e notas): nenhum resto de teste. "Teste" só aparece como regra (Teste de
  Resistência etc.). Os restos (missões teste-1/teste-2/fidijs, "Teste Salário", extrato e livro) só existem na cópia de
  teste.
- Comparação com a cópia de teste (xlsx exportado): mesclagens iguais em todas as abas; fórmulas iguais, salvo o
  derramamento de DADOS_SALARIOS!AA2 (a cópia de teste tem créditos, a nova não).
- Painel: Grau 4, ¥ 150.000 de referência, próximo fechamento 19/11/2026, previsto ¥ 37.500 (0 participações, parcela
  mínima), TOTAL DISPONÍVEL ¥ 150.000, conferência "Na hora, por fórmula".

## Cópias feitas pelos jogadores

Nada roda em segundo plano: gatilhos e propriedades do documento não vão na cópia, e o salário pendente é só fórmula
(depende de `TODAY()`). O risco era outro: a fórmula conta os períodos a partir da data de emissão (CONFIGURAÇÃO!O38),
e a cópia herda a emissão da base (20/10/2026). Quem copiasse meses depois e preenchesse o nome receberia os períodos
desde 20/10 na hora.

Correção (`salarioPrimeiroNome_`, desvio em `salarioEditar_`): quando o nome do personagem na CARTEIRA passa de vazio ou
do texto de exemplo para um nome de verdade, O38 vira a data de hoje. Renomear não reemite. A edição continua para o
resto da ficha (retorna false). Aplicado na definitiva pelo `preparar_salario_extrato.js` (diff de 8 linhas, conferido).
Lançamentos de teste do Mizuki no EXTRATO (−100 e +100) ficaram: somam zero.
