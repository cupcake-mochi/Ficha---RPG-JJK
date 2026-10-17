# Revisão antes do merge de `codex/configuracao-b47` em `main` · 17/10/2026

Revisor: Claude Opus (integrador), a pedido do usuário. `main` (`15e0af9`) é ancestral da branch: o merge é fast-forward, sem conflito. 82 commits, 338 arquivos, cerca de 101 mil linhas (a maior parte gerada ou prova).

## O que foi olhado

- **Segredos e credenciais**: busca no diff por chaves, tokens, senhas, `client_secret`, chaves privadas e e-mails. Nada encontrado; as ocorrências de "token" são de tokenização de fórmula e de instruções para não copiar credenciais.
- **Dados do personagem**: os XLSX versionados (`nuvem-b47/fixtures/*.xlsx`, `ficha-v01/ficha-projeto-m-0.1.xlsx`) são modelos em branco ("Coloque o nome do personagem aqui", "Nick do jogador"), documentados em `NUVEM.md` como referência local. As exportações da revisão desta sessão ficaram fora do Git.
- **Arquivos grandes**: só `arte/fontes/YujiSyuku.ttf` (8,4 MB, fonte livre usada na arte). Todos os `.gs` abaixo do teto de 900 KiB.
- **Código Apps Script**: dos 35 `.gs`, 34 são gerados (`GERADO POR …`) e conferidos nativamente (36/36 iguais na revisão e na descartável de construção). O único escrito à mão é `Codigo.gs`; o diff dele contra `main` foi lido inteiro.

## Achados em `Codigo.gs` (nenhum bloqueia o merge)

1. **Diagnóstico deixado no `onEdit`**: linhas `console.log('B47 tempo: …')` (cerca de oito por edição). Só ruído no registro do Cloud; tirar numa próxima versão junto com outra mudança de código, para não republicar só por isso.
2. **Endereços literais** em leituras novas (`'B737:O792'`, `'M8:V8'`, `'BO8:CA8'`, `'AA2:AB22'`, `'K4'`/`'K7:K8'`, `'CB2:CC10'`, `'AV2:AV132'`, `'BD2:BD24'`, `DADOS_CUSTOM!B2:T26`). Funcionam no layout atual; são o mesmo risco de manutenção registrado em `RETENCAO-AB.json`. Se o gerador mover essas faixas, o `Codigo.gs` precisa acompanhar.
3. **Leitura por `getDataRange()`** em `habilidadesDaFicha_` e `notasVivas_`: o índice `matriz[linha-1][coluna-1]` falharia se uma caixa ficasse abaixo da última linha com conteúdo. Hoje não acontece (construção nativa e `regressao-pessoal.js` passam); vale um teste de borda se o layout crescer.
4. **`paleta_base`** (deste fechamento): corrige a deriva em cópias; comprovado em VM e nativamente (`COPIA-FUNCIONAL-D.json`).

## Testes

Ver `BATERIA-D.json`: bateria do `rodar-tudo.sh` mais os testes que estavam fora dela. Dois testes antigos do simulador foram consertados sem mudar expectativa (`regressao-pessoal.js`: `Range.getNotes` e `RangeList.setValue`, que o código passou a usar).

## Conclusão

Sem bloqueio para o merge em `main`. Ficha oficial e bot não fazem parte do merge.
