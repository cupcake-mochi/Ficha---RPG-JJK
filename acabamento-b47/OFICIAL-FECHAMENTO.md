# B47 — oficial concluída e liberada · 17/10/2026

A ficha oficial está pronta para os jogadores copiarem no link existente:
[Ficha - Era da Revolução](https://docs.google.com/spreadsheets/d/1u0zWQFVaRTTc_VlrAJsabgAiJ1D4rTYhzG7QQWof1ro/edit).
C, D, manutenção dos testes antigos, medidas e publicação oficial concluídos.

## Salvamento e segurança da atualização

O usuário confirmou presença no PC e janela sem cópias em 17/10, 23:31Z.
A montagem e validação terminaram antes da interrupção do PC. Backup nativo
novo conferido antes de alterar a oficial:
[Backup B46](https://docs.google.com/spreadsheets/d/1mp62IhotoQERYaIiGEGcn0AsssUJHE9vO1xI_srXCrI/edit).
Conteúdo, notas, validações, mesclas, grupos e estilos das dez abas iguais.
Os seis GS antigos e o manifesto também foram guardados fora do Git.

35 GS + manifesto publicados com hash antes de salvar, espera do salvamento,
nova abertura e releitura dos 36 arquivos iguais. Nenhuma autorização nova,
alteração de acesso ou do bot. Revisão preenchida preservada, sem montar nela.
Dados do personagem e recibos volumosos permanecem fora do Git. Exportações
XLSX foram usadas somente para comparação local; nenhuma foi importada.

## Construção e validação

A criação inicial de abas ultrapassou o limite do serviço. A retomada agora
cobre essa preparação, além do preenchimento, com proteção contra adoção de
abas desconhecidas ou preenchidas. Só o transporte de Ficha.gs mudou;
ABAS/ARTE mantiveram o hash. 22 verificações locais aprovadas.
As 12 abas vazias faltantes foram preparadas por API nas dimensões dos GS;
o conteúdo veio das continuações nativas. Não é um teste de construção nova
exclusivamente pela criação individual do Apps Script.

Três continuações concluídas: 187, 169 e 254 segundos no relógio interno.
A última registrou **FICHA PRONTA**, menus, notas, paleta e ligações conferidas,
sem acabamento pendente. Total interno de sucesso: 610 s, excluindo tentativas
anteriores, correção/publicação e preparação via API. Não é comparação
controlada de velocidade com a execução histórica de 821 s.

Comparação integral contra a descartável construída anteriormente:

| Verificação | Resultado |
|---|---:|
| Abas, na mesma ordem | 22 |
| Fórmulas | 66.242 |
| Células com conteúdo na foto do comparador | 102.973 |
| Notas | 4.470 |
| Validações na exportação | 2.194 |
| Chaves de ANALISE, todas únicas | 8.190 |
| Erros de fórmula | 0 |
| Diferenças em conteúdo, notas, validações, mesclas, grupos e estilos | 0 |

Regras condicionais comparadas separadamente por API: iguais nas 22 abas,
normalizando somente IDs para nomes das abas. Exportações não provam
gatilhos, proteções ou identidade de abas. Os hashes do código têm prova
própria de releitura, não são inferidos da exportação.

## Cópia funcional e persistência após a queda

[Cópia de teste da oficial](https://docs.google.com/spreadsheets/d/1mSVpDt8L8OI4S9ouASYOAXQiPklKJ_aKxiQwAGDVfVc/edit):
troca de Mizuki Claro para Mizuki Escuro antes do fim da primeira aplicação,
sem nova autorização. Regras condicionais iguais à oficial. Nas 14.517
células de cores conferidas, as 14.500 de FICHA!A147:AX436 não tiveram deriva.
Só CARTEIRA!A1:C1 mudou em relação ao padrão natural: fundo 251727/texto
FBE4EF, previstos no tema Mizuki Escuro; padrão natural 17131F/F4F1F7.
Essa verificação de cores é delimitada, não auditoria integral da cópia.

Os 99 valores de controle em CARTEIRA!C27:M35 foram restaurados exatamente.
Depois da queda do PC, uma nova leitura confirmou essa restauração e que
os metadados/regras condicionais da oficial permaneciam iguais ao snapshot
final: 22 abas, pt_BR, America/Sao_Paulo. Última modificação da oficial
recebida do Drive: 18/10/2026 00:19:36.115Z. Não foi necessário repetir a
montagem ou republicar código.

Provas públicas: [OFICIAL-B47.json](OFICIAL-B47.json),
[comparação integral](OFICIAL-COMPARACAO-FINAL.json) e
[transporte](RETOMADA-CRIACAO.json). Recibos nativos, exportações e imagem
final ficam na pasta privada de evidências indicada na prova.

Sem pendência obrigatória desta entrega. B84, carregamento integral sob
demanda, permanece otimização futura delimitada e não foi implementada.
Próxima ação eventual: Sol/Médio para manutenção focal.
