# Dados das entidades

28/10/2026 · PR 31 em rascunho. Não instalado. Criação continua bloqueada.
Main produtor ef361cc e bot main de42447 reconferidas, sem mudanças externas.

## Implementação

Contrato gerado do fonte público completo, com overlays e metadados de
redutores/Famílias. Endereços calculados a partir das âncoras reais das 12
entidades; rótulos/defaults conhecidos e separação dos cartões R53 conferidos.
73 perfis: seis por entidade e uma escolha do conjunto. 1.165 entradas:

| Grupo | Por entidade | Total |
|---|---:|---:|
| Identificação | 9 | 108 |
| Atributos, bônus e treinos | 29 | 348 |
| Recursos e estado de uso | 8 | 96 |
| Famílias | 19 | 228 |
| Inventário e Volumes | 18 | 216 |
| Talentos e Expansão | 14 | 168 |
| Defesa usa do conjunto | — | 1 |

Restaura valores, fórmulas e notas das entradas. Vida e Integridade atuais
voltam às fórmulas do modelo; máximos/resultados ficam protegidos. Famílias
limpam escolhas individuais e restauram estados calculados custom, mantendo
os nomes e as definições da mesa. Equipamento não recebe estoque ou recursos.
Nome/COMO É/degrau da Expansão estavam fora dos 249 cartões do editor e são
tratados aqui, sem apagar cálculos ou modificar a Técnica Máxima.

Entradas são matrizes apenas de âncoras. A geometria de cada mescla é verificada
por inteiro. Menus de fábrica são preservados e comparados por critério,
referência/lista, documento, interface e ajuda. Aceita a rigidez do fonte ou
a dos modelos publicados; o valor real entra no fingerprint para detectar
mudanças posteriores. Catálogos custom podem mudar de conteúdo, mas não é
aceita uma validação arbitrária nem referência a outro arquivo.

O adaptador `validacoes.gs` só separou a descrição da leitura individual para
permitir leitura em lote. Escritor/descritivo anteriores mantidos. Executor,
assinaturas e contratos anteriores não foram alterados. Cada perfil usa
quatro escritas por chamada, orçamento/diário existentes e recibo terminal.
Cache volátil invalidado; caches persistentes e MONTAGENS continuam separados.

## Validação

- 305 cenários locais de entidades aprovados: 73 grupos completos, 1.165
  entradas, 36.719 bytes de recibos, maior diário pendente 3.165 bytes.
- Quedas antes/depois de todas as escritas dos seis grupos representativos e
  do conjunto; retomada, edição posterior e preservação dos domínios vizinhos.
- Fórmulas regionais/desconhecidas, foto em célula, menus, mesclas com mesma
  âncora mas tamanho alterado, matriz parcialmente gravada e notas concorrentes.
- Teste de quota conjunta ampliado para 571 nomes reais de perfis com operações
  sintéticas, mais reserva de 100 KB. Resultado final a registrar.
- Coleção prevista 2.610 cenários de inicialização; CI final a registrar.

## Leitura das oficiais

Somente leitura nas duas oficiais, após metadata: INVOCAÇÕES, sheetId 996249592,
grade 1.394 × 45. Nove faixas delimitadas por arquivo: conjunto e primeira/
última entidade (cabeçalho, talentos, Trilha e Expansão). Por arquivo:
195 entradas/validações e 284 guardas conferidas.

Valores/fórmulas e critérios/referências dos menus coincidem. A fórmula da
barra de vida usa separador de coluna `\` no array pt_BR e `;` dentro de MAX;
essa variante inteira foi incorporada, sem aceitar referências ou contas novas.
Os 105 menus da amostra estão estritos na publicada. A rotina os preserva,
assim como a variante não estrita que o construtor público produz.

Há duas notas contextuais por arquivo, no tipo da primeira/última entidade,
que não são notas estáticas do fonte: foram geradas a partir da definição.
A inicialização limpa a nota herdada; a futura fase de automações precisa
regenerá-la com as definições da mesa. Isso é pendência explícita, não uma
alegação de notas nativas idênticas. Não houve cópia, escrita, Apps Script,
OAuth ou acionador nesta rodada. Evidências privadas em
`nuvem-b47/saidas/entidades-20261028/`, ignoradas pelo Git.

## Limites e próxima ação

Os testes não calculam fórmulas nem provam escrita/retomada no Apps Script.
A leitura representativa não valida todas as entidades nativamente ou as
mesclas por API. Fotos só são aceitas vazias ou com o marcador de fábrica;
imagem em célula/fórmula causa recusa. Nenhuma foto é apagada. Imagens
sobrepostas ainda precisam de identificação/limpeza pela fase de arte.

Criação permanece bloqueada: faltam arte, orquestração e orçamento total,
conferência conjunta, automações/treinos/notas contextuais, novo responsável,
integração drive.file e prova nativa completa em cópia descartável. Os recibos
não tornam o conjunto uma transação. Modelo/conta/cópia precisam ser provados
pelo criador confiável, sem parâmetros de autorização vindos do navegador.

Protótipos continuam fora do pacote/bot. Sem merge/deploy, oficial/jogador
editado, escopo novo ou modelo pago. Próximo: fase de arte em cópias novas.
GPT-6.1 Sol / Alto para implementação; Médio para revisão focal (AGENTS.md).
