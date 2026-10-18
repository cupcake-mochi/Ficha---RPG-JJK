# Ficha oficial — roteiro para levar ao B47 · 17/10/2026

**Executado e validado na janela acompanhada de 17/10/2026. Oficial B47
liberada para cópias.** Backup novo `1mp62IhotoQERYaIiGEGcn0AsssUJHE9vO1xI_srXCrI`
conferido antes da montagem. 36 arquivos relidos iguais; criação retomável
corrigida após timeout, 12 abas vazias preparadas por API nas dimensões do
GS, sem importar XLSX. Três continuações concluídas, comparação completa e
cópia funcional aprovadas. [Prova final](OFICIAL-B47.json).
Os estados B46 e passos abaixo documentam a preparação histórica; não são
uma tarefa a repetir. A revisão preenchida continua proibida para montagem.

> **Autorização do usuário (17/10/2026):** "Pode atualizar a ficha oficial seguindo o ROTEIRO-OFICIAL-B47.md numa sessão em que eu esteja no PC; fica liberado rodar construir() na oficial depois do backup." Vale **só** com o usuário presente na sessão e **depois** de backup nativo conferido; é a exceção à regra geral de não rodar `construir()`/`continuar()` na oficial. Continua proibido na revisão preenchida.

**Limpeza posterior:** a pedido do usuário, os 31 arquivos temporários B47,
incluindo os backups, foram enviados à lixeira após a validação. Oficial
preservada. Links abaixo são históricos; ver [inventário](LIMPEZA-B47.json).

## Estado lido (somente leitura)

- Oficial `1u0zWQFVaRTTc_VlrAJsabgAiJ1D4rTYhzG7QQWof1ro` ("Ficha - Era da Revolução"), em drive compartilhado, aberta hoje às 13:08Z.
- Estrutura **B46**: 10 abas (CARTEIRA, FICHA, FICHA AMALDIÇOADA, INVOCAÇÕES, FICHA PESSOAL, DADOS, DADOS_AM, DADOS_INVOC, GLOSSÁRIO, ANALISE). Faltam CONFIGURAÇÃO, DADOS_CONFIG e os dez `DADOS_*` de C; ANALISE antiga; fuso `Etc/GMT`.
- É o modelo que os jogadores copiam: CARTEIRA com "Coloque o nome do personagem aqui".
- **Backup nativo feito**: `117rWwlUgRHTthjPpTqS37TV_SVgpFu_-hjtQyqXPpJw` ("BACKUP OFICIAL B46 — antes da atualização B47 — 2026-10-17"), na pasta de trabalho.

## Por que não foi feito sozinho

Levar a oficial ao B47 no mesmo arquivo (mantendo o link do servidor) é refazer a ficha: 12 abas novas, CONFIGURAÇÃO, ANALISE 11, 35 `.gs`, fuso e fundo. O caminho limpo é `construir()`, que a regra do projeto proíbe na oficial. Jogadores podem copiar o arquivo durante as ~15 min em que ele fica pela metade.

## Caminho recomendado (precisa de liberação explícita da regra)

O mesmo do fechamento B46, que atualizou a oficial no próprio arquivo após backup:

1. Escolher um horário sem uso no servidor; avisar os jogadores para não copiar a ficha nesse intervalo.
2. Backup novo da oficial (o de hoje serve se nada mudou; conferir `modifiedTime`).
3. No projeto vinculado da oficial: colar os 35 `.gs` de `main` e o manifesto; reler os 36 hashes (`NATIVO-CODIGO-REVISAO-D.json` traz a lista).
4. Fuso do arquivo `America/Sao_Paulo`.
5. `construir()` e `continuar()` até FICHA PRONTA (referência: 4 execuções, 821 s em `CONSTRUCAO-D.json`; uma falha transitória do serviço pode exigir repetir o `construir()`).
6. Conferir: exportação da oficial × descartável de construção `14Ad8e5…` — fórmulas idênticas, 0 erros, 8.190 chaves; abrir uma cópia e trocar de paleta (`COPIA-FUNCIONAL-D.json`).
7. Se algo der errado: o backup permanece; a oficial pode ser restaurada copiando de volta ou pelo histórico de versões.

## Alternativa sem tocar na oficial

Publicar a descartável de construção (já em B47, verificada) como nova ficha do servidor e trocar o link no Discord. Mais segura para a ficha antiga, mas muda o link que os jogadores conhecem (e o bot, se ele lê a oficial pelo ID, ficaria fora de escopo).
