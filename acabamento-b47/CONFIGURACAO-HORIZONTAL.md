# CONFIGURAÇÃO horizontal — concluída na oficial

Pedido posterior à entrega B47, aplicado em 17/10/2026: limpar notas
inúteis e organizar a CONFIGURAÇÃO como as invocações, com listas que
abrem para a direita. Uma introdução por lista explica o conteúdo e as
siglas; nenhuma explicação nova repetida por cartão ou célula.

Oficial: https://docs.google.com/spreadsheets/d/1u0zWQFVaRTTc_VlrAJsabgAiJ1D4rTYhzG7QQWof1ro/edit#gid=1364162823

São 14 listas recolhíveis, identificadas mesmo quando fechadas. Geral
ganhou um índice no espaço livre; os 25 cartões gerais agora ficam em
pares, com larguras iguais. A grade caiu de 2.812 para 400 linhas,
distribuídas em 238 colunas agrupadas. A abertura de Formas explica
ALC (alcance), P (personagem), E (entidade), Classes e TR.

Das 3.995 notas anteriores, foram removidas 2.575 orientações genéricas
repetidas ou duplicatas entre rótulo e entrada. As 1.420 ajudas específicas
foram preservadas. As orientações de uso ficam visíveis nas aberturas e
no índice, sem novas notas repetidas nos títulos.

## Validação e publicação

[Prova resumida](CONFIGURACAO-HORIZONTAL-VALIDACAO.json):

- Geração integral pelo gerador canônico; código e XLSX de fábrica sem
  dados do personagem. Os valores do modelo de transformação coincidem
  com a geração integral, inclusive as referências diretas que substituem
  os 840 INDEX dependentes da posição vertical.
- Ensaio e oficial: 2.960 campos e 1.110 validações preservados, incluindo
  caixas de seleção; 8.190 chaves/valores iguais e origens remapeadas.
- Oficial: 22 abas, zero erros no recálculo nativo; 4.165 mesclas e 27
  regras condicionais iguais ao alvo, 14 grupos de colunas e nenhum
  grupo de linhas na CONFIGURAÇÃO.
- Texto longo testado no Google: altura de 42 para 356 pixels; apagar a
  outra lista mantém 356; apagar o último texto retorna a 42. Campos
  temporários restaurados e comparação completa novamente sem diferenças.
- Cópia e oficial: 35 GS e manifesto relidos iguais após recarregar
  (36/36 em cada projeto). Hashes conferidos antes de salvar; manifesto
  preservado, nenhuma autorização ou mudança de acesso.
- Expansão e recolhimento testados pelos botões da oficial. Zoom de
  inspeção restaurado a 100%; Geral aberto e demais listas recolhidas.

A migração da oficial usou snapshot atual, backup novo e 33 lotes nativos,
preservando entradas por cópia de células. Não executou construir/continuar
nem importou XLSX. A cópia de ensaio e o backup foram movidos para a
lixeira após a validação; oficial preservada. São 33 temporários removidos
no processo completo, conforme [inventário](LIMPEZA-B47.json).

## Manutenção

`ficha-v01/configuracao_horizontal.py` transforma a apresentação depois
das regras. Exportações de testes de domínio permanecem anteriores à
transformação; um roteiro nativo deve traduzir endereços pelo mapa.
`reorganizar-configuracao.py` planeja a migração sem rede e bloqueia notas
alteradas ou entradas fora da área prevista para Geral. Remove regras
condicionais antes da cópia e reinstala as 27 regras remapeadas.

`conferir-configuracao-horizontal.py` compara snapshots nativos sem escrita.
`testar-configuracao-horizontal.js` cobre quatro cenários de altura entre
categorias e exige uma leitura em lote por edição. Sintaxe dos 35 GS válida;
maior arquivo com 826.532 bytes, abaixo do teto de 900.000.

Snapshots, recibos e capturas ficam fora do Git em
`D:/JJK - Project/B47/evidencias/2026-10-17/pos-d/`, prefixo `horizontal-`
ou `configuracao-horizontal-`. Não restaurar temporários nem repetir a
migração. Próximos ajustes: Sol/Médio; aguardar os novos problemas do usuário.
