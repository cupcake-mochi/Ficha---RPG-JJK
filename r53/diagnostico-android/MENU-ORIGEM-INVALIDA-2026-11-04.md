# Capacidades herdadas de Origem custom inválida

Base: PR54 `93a109ce3477845618da3beff941af7326f17db7`.
Ramo separado: `codex/menu-origem-invalida-20261104`.
Sem merge, oficiais, jogador ou PR31. Somente cópia descartável nativa recebeu alterações.

## Defeito confirmado

DADOS_CUSTOM!CP3 e CQ3 consultavam a BASE DO LIVRO pelo nome, sem exigir
que o cartão fosse do tipo Origem e estivesse válido. Selecionar uma Origem
válida e depois apagar uma perícia obrigatória deixava suas capacidades
herdadas disponíveis. O cartão mostrava erro e B121/B126 eram falsos, mas
os menus ainda ofereciam os três corpos e as menores da Restrição corporal.
Não se deve interpretar a presença no menu como prova de aplicação de efeitos:
as regras de Defesa/descanso já possuem sua própria guarda de validade.

## Correção

A base usada exclusivamente pela herança dos menus passa a exigir exatamente
uma Origem válida com o nome selecionado, usando o mesmo COUNTIFS já empregado
na permissão de criação. Preserva o filtro de marcante exigida pelas menores,
as opções publicadas, capacidades custom válidas e avisos legítimos.
A opção genérica de menor «Criada com o mestre» não foi removida.
Não apaga escolhas residuais do jogador: corrige a lista de opções.

## Ensaio nativo

Cópia derivada da QA da PR54. Preparação e leitura pelo conector Google Sheets;
nenhuma importação de Office ou reconstrução. Não mede onEdit nem desempenho.
Cartão criado nos campos reais da CONFIGURAÇÃO e selecionado em FICHA!X11.
Fórmulas auxiliares de validação e menus recalculadas pelo próprio Google.

1. Antes da correção: cartão «QA Origem corporal» com quatro perícias e rota
   Fundamento fica válido; após apagar PERÍCIA 1, T2/B121/B126 falsos e aviso
   de campo obrigatório, mas CP3:CQ continuam oferecendo a base (erro).
2. Depois de atualizar somente CP3/CQ3: cartão permanece inválido, capacidades
   herdadas desaparecem; opção genérica de menor preservada.
3. Repor a perícia: T2/B126 verdadeiros e capacidades herdadas voltam.
4. Trocar a rota por Manejos: aviso «ROTA não combina com BASE DO LIVRO»,
   T2 falso e CP3:CQ sem capacidades herdadas.
5. Selecionar a Origem corporal publicada, mantendo o cartão custom inválido:
   três corpos e menores publicados continuam presentes, B126 verdadeiro.

## Validação da entrega

Geração `98c46466ecb7e203`, com limite de memória de 2,6 GiB e sem exportar XLSX.
Depois da geração, o empacotamento atualiza o selo de Eventos.gs; a primeira
comparação antes desse passo detectou a ausência da aba de eventos no carregador
por selo antigo. Após completar essa etapa normal, a comparação passou:
26 abas integralmente iguais à PR54, salvo CP3/CQ3 e os selos de geração.
ANALISE, 249 contextos, validações, notas e demais fórmulas preservados.

- `python3 r53/empacotar_script.py`: aprovado.
- `node r53/testes/menu_origem.js`: aprovado, duas fórmulas iguais às ensaiadas
  no Google e comparação integral com a base da PR54.
- `node r53/testes/pacote_runtime.js`: aprovado, dez arquivos e 249 contextos.
- `git diff --check`: aprovado.

Executar o teste de comparação depois do empacotamento; ele precisa do commit
base `93a109c` no histórico local. Não é uma medição de tempo ou RAM no Android.

## Limites e atualização futura

Não foi repetida a bateria completa de cartões nem o teste Android. A cópia
não é modelo de distribuição. A instalação incremental do código de restauração foi ensaiada nesta cópia;
novos destinos continuam exigindo snapshot e verificação de compatibilidade.

Para aplicar em ficha existente: autorização do destino, snapshot fresco de
CP3/CQ3 e do projeto Apps Script; comparar fórmulas com as antigas esperadas,
preparar somente as duas substituições e atualizar o molde instalado com
`preparar_menu_origem_loader.js entrada.gs SHA256 saida.gs`. O preparador
valida o hash, âncora única e ausência de instalação repetida. O helper
`menu_origem_molde.gs` verifica ambos os moldes antes de alterar qualquer um;
aceita somente fórmula antiga exata ou nova já aplicada, sem alteração parcial. Nunca
instalar o pacote integral nem executar construir/continuar. Os modelos GS
regenerados pertencem ao Git, não foram instalados na cópia ou nas oficiais.

As fórmulas sanitizadas antes/depois estão em `r53/testes/menu_origem_formulas.json`.
`node r53/testes/menu_origem.js` verifica paridade da geração com essas fórmulas
e exige que somente CP3/CQ3 mudem nas abas, desconsiderando o selo de geração.
Snapshot e evidências brutas ficam fora do Git.

Revisão: Sol/Medium; implementação integrada: Sol/High. Configurações não alteradas.

## Revisão e restauração nativa — 04/11/2026

A cópia ainda tinha o carregador anterior à PR55. Apagar CP3 pela interface
restaurou a fórmula antiga (confirmado por releitura), demonstrando que trocar
só a fórmula da célula não basta na promoção incremental.

Snapshot do Codigo.gs antes:
`792abb536784e0ac9c34f1cf5cce20c0245b89b5c2917770d568e38a597a3c79`.
Instalado somente o delta dos dois moldes, preservando todos os incrementos
existentes. Código salvo, editor recarregado e releitura integral idêntica:
`212f2acb0662169305ad9e031b753ca674158d55f471d8e4f4691faaf71f594f`.

- Apagar CP3 pela interface: onEdit recuperou a fórmula **nova**, resultado
  Corpo Debilitado para a Origem publicada selecionada.
- Sobrescrever CQ3 com 999 pela interface: onEdit recuperou a fórmula **nova**,
  resultado Reserva Condensada.
- Releitura de CP3/CQ3 integralmente igual às fórmulas sanitizadas esperadas,
  sem reposição manual de fórmula entre a edição e a leitura de cada ensaio.
- 19 verificações locais: idempotência, divergência sem aplicação parcial,
  abas/células ausentes ou duplicadas, paridade com GS, hash, âncora única,
  rejeição de instalação repetida e preservação do restante do carregador.
  Esse teste passou a integrar o smoke do GitHub.
- Comparação integral das abas contra PR54 passou novamente.

A aba auxiliar foi desocultada somente na cópia para permitir as edições
nativas e ficou visível para revisão. Não foram criados acionadores nem
instalado pacote integral. Tempos de gatilho/Android não foram medidos.
