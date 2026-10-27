# Nível e textos pessoais · 27/10/2026

Continuação da PR 31 do produtor, em rascunho. Base main atual
`9536746405f12a9e159e9173b54a2a861c0a871a`, incorporada pelo merge `8cb12ac`.
O fechamento de desempenho e a base de XP dessa main foram preservados.
Protótipos fora do pacote, sem menus, eventos, endpoints ou integração com o
bot. Nenhuma ficha oficial ou de jogador foi alterada.

## Código e testes locais

- Executor privado extraído do financeiro para perfis fixos; API pública,
  formato do diário financeiro v1 e assinatura compatíveis com `4f3555d`.
- Nível/base: usa regra resolvida e curva atual da campanha; limpa somente
  AH11/CZ54, preserva fórmulas de XP. Exige diário financeiro da mesma operação
  e missões vazias, com 292 fórmulas reconhecidas. Não faz conferência geral
  de todos os outros domínios.
- Textos: 14 entradas e notas, com rótulos conhecidos e espelhos preservados.
  Nome volta ao texto de preenchimento; foto pessoal desconhecida é recusada.
  Imagens sobrepostas, escolhas e estado mecânico continuam pendentes.
- CellImage/objetos em entrada não são serializados como `{}` e confundidos
  entre si; o leitor compartilhado recusa antes de escrever.

Comandos executados:

```sh
node r53/testes/inicializacao_financeiro.js
node r53/testes/inicializacao_progressao.js
node r53/testes/inicializacao_identidade.js
node r53/testes/xp_nivel.js
```

259 cenários de inicialização: 101 financeiros, 80 nível/base e 78 textos.
Cobrem prévia envelhecida, fórmulas incompatíveis, notas, imagens, todas as
fronteiras de escrita antes/depois, edição após pausa, repetição, preservação
fora do domínio, assinatura financeira anterior e ordem entre financeiro e
nível. XP: 20.643 verificações/9.900 combinações; sem a exportação opcional.
A VM não calcula fórmulas do Sheets. Os três testes entram no smoke Linux.

## CI Linux

Código `280a7dcd0b3fb56b0a43dd6e0d88aaadcb08d634`: [run 40534237271](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/40534237271)
aprovado em 27/10/2026 às 15:47:26 UTC (12:47:26 Brasília). Confirmados no log
os 101/80/78 cenários, pacote autossuficiente de nove arquivos sem os
inicializadores, limites de tamanho, regressões de salário/missões/editor,
sintaxe de 277 fontes Python e 206 JS/GS, catálogo, progressão e Kaori.
O run duplicado do push foi cancelado; o run da PR passou no mesmo código.
O registro posterior é documental e usa `[skip ci]`; não exige nova bateria.

## Leituras nativas e defeito encontrado

As duas oficiais foram consultadas somente para leitura: metadados de 30 abas
e âncoras de regra, curva, XP, nome/foto e total de missão. As seis âncoras
comparadas corresponderam ao fonte, permitindo os separadores conhecidos.
Na cópia atual da Era, 380 conferências de rótulos/entradas, regra de nível,
XP, referências da curva e 292 fórmulas de missão passaram.

A regra G46 foi devolvida com `;` na API. O primeiro protótipo de progressão
exigia `,` e recusaria essa leitura. Corrigido somente para aceitar a variante
conhecida. Duas regressões novas: variante aceita sem reescrever a fórmula;
variante com limite alterado (30 para 31) recusada antes de escrever.

## Projeção nativa dos efeitos

Alvo: **QA Carteira — nível e textos — DESCARTÁVEL — 27-10-2026**,
cópia da Era `1odoHfNp…`. Privada, na pasta ChatGPT. Fonte e destino distintos
conferidos antes de escrever. Nenhum acesso novo ou Apps Script foi autorizado.

Este teste aplicou os mesmos alvos/valores por `spreadsheets.batchUpdate` do
conector. **Não executou o inicializador, seu diário, trava ou retomada no
Apps Script. Não foi criação pela Carteira nem prova do OAuth das Guias.**

1. Ler metadados, entradas, validações, espelhos, regra, curva e missões.
2. Inserir 14 textos/notas fictícios; regra inicial 10, nível antigo 29 e base
   antiga 77.777. Ler e conferir a preparação: sem diferenças, missões vazias.
3. Restaurar nome de preenchimento, limpar outras 13 entradas/notas, escrever
   nível 10/base 3.700, sem incluir fórmulas/formatos/validações nas máscaras.
4. Conferir as 14 entradas e notas: todas no estado esperado. XP total na DADOS
   e na FICHA 3.700; espelhos de nome vazios. Regra da campanha continuou 10.
5. Comparar 8.998 campos de fórmulas/entradas não alteradas, notas, formatação,
   validação e chips nos intervalos lidos: zero diferenças. É comparação
   delimitada desses intervalos, não auditoria integral do workbook/catálogos.
6. Inserir missão fictícia do tipo Curta (50 XP, opção lida da validação real):
   total da missão 50; XP total/exibido 3.750; base 3.700 e nível 10.
7. Retirar a missão: XP voltou a 3.700. Conferência visual no Google das abas
   CARTEIRA, FICHA e FICHA PESSOAL; nenhum formato foi refeito.
8. Enviar a cópia à lixeira e fechar a aba. A tela confirmou o descarte
   recuperável. Não reabrir/restaurar essa cópia para continuar testes.

## O que não foi comprovado

O ensaio financeiro Apps Script anterior é do código `4f3555d`, antes desta
extração e da main atual. Não transporta aceite nativo para os novos perfis.
Não houve teste de falha/retomada nativo combinado, duas identidades Google,
modelo de servidor sintético, imagens sobrepostas, escolhas, inventário,
cartões, propriedades de recuperação ou automações de novo responsável.

Ainda falta orquestrar os domínios com conferência final conjunta. Depois de
alterar o nível, repetir o financeiro antigo recusa por alteração de campo
protegido; não reiniciar todas as fases e não apagar diários para contornar.
Todas as respostas conservam `criacaoDisponivel=false`. Nada foi integrado
ou publicado na Discloud. Próxima implementação integrada: GPT-6 Astra / Alto;
revisão focal: Médio. Não mudar a configuração automaticamente.
