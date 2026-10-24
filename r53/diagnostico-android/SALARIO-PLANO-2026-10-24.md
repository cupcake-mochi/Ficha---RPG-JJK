# Salário automático nas cópias · plano (24/10/2026)

Documento completo (Claude Docs): https://claude.ai/artifact/7emraQpwXw12hUoJP1ZNij

## Problema
Cópia sem acionador instalável não fecha o salário no vencimento. O carimbo de data das missões já roda no acionador
simples (vai junto na cópia); o que falta é o fechamento. A conferência atual leva 80,5 s (`salarios/VALIDACAO.json`)
e o acionador simples tem 30 s. A cópia de teste mostra "Conferência automática: Diária" apontando para a rotina de
outra ficha, que não roda nela.

## Recomendação (C): fechar na edição, em lote
1. Faixa oculta em DADOS_SALARIOS que junta por fórmula config (CONFIGURAÇÃO O38:O67), Grau (FICHA PESSOAL!AB11),
   nome (CARTEIRA!O9), missões carimbadas, histórico de Graus e último fechamento. Uma leitura só.
2. Em cada edição: compara hoje com o próximo fechamento guardado; não venceu, sai sem ler. Edição da C27 (paleta)
   nunca dispara salário.
3. Venceu: conta na memória, grava livro + estado + painel numa gravação, com o bloqueio e a trava de período repetido.
4. Grau entra no carimbo: mudança no AB11 grava data + Grau no histórico.
5. Corrigir o texto "Diária" em cópia sem rotina; padrão de peso das missões solo = 1 (decisão do Mizuki, 24/10).

Valor igual ao fechamento no dia (períodos contados por data); o crédito aparece na 1ª edição após o vencimento.
Meta de tempo: até ~22 s. Se passar de 30 s, próximas opções: híbrido fórmula + livro (E) ou rotina central (G).

## Teste (só na cópia descartável 1ESL-AageFm_eo9ybp1ITFAAKm1t6I2FKJyYp8-SFOYU)
- Nome + emissão 60 dias atrás + duas missões datadas → 2 períodos vencidos.
- Editar uma célula e cronometrar; conferir créditos à mão; editar de novo sem duplicar; trocar paleta sem salário.

## Estado
- Ainda não implementado. Aguardando o ok do Mizuki.
- Cópia de teste já tem solo simples/complexa com peso 1 (CONFIGURAÇÃO O66:O67). Na base, trocar também o padrão do
  instalador (`apps-script/Salarios.gs`).
