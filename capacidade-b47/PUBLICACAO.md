# Publicação · capacidade B47 · 16/10/2026

Base: `4187df37640b5e0966cdb342f56f9ee0a0daf16a`, com a preparação de nuvem.
Código de produção testado: `f1ff7a6785f179df78a91a619bbd60388acd4bc1`.
Correção da regressão histórica e reexecução: `8276ca6fbdc11ff0f35547c7935a09441b0a6e4a`;
único diff de código: `regressao-progressao.py`. Este fechamento acrescenta
apenas documentação/evidências; fontes e 20 `.gs` permanecem iguais.

Ramo próprio: `codex/b47-capacidade`. Integração autorizada:
`codex/configuracao-b47`, por avanço sem reescrever história, depois da
conferência do remoto e dos testes da combinação. `main` não recebeu merge/push.

Origens examinadas e incorporadas separadamente:

- `codex/b47-infra`: `b8ab7b56aac71ad0c85d0a3cff0c94d026062189`, merge
  `73bd04e8f5c5f7c4bfb94fa3c5314831a4d07fea`.
- `claude/kind-feynman-sewhec` (nome alternativo de `claude/b47-revisao`):
  `287b2c1408c893c20a003cd6caa6241504336f02`, merges
  `77d0d1d3b6d1752efa8cf767664bc0502a07a4bf`,
  `4ea06708572b94a90fd309f461d416b9cd35edd8` e
  `4bb684097d81589353b37b054585f58552e72fc8` (último: só auditoria/teste histórico).
- Correções do integrador: `e5871e3749cce244810dbd6c1f545db4a2916e1f` e
  `f1ff7a6785f179df78a91a619bbd60388acd4bc1`.

A consulta inicial às referências locais era incompleta: o fetch do clone só
buscava main. `git ls-remote --heads origin` e fetch explícito localizaram as
frentes acima. A revisão externa reproduziu A em `4610c88` (14/14 etapas e
20 `.gs` iguais); a combinação posterior recebeu os testes do integrador.
Revisão externa do último SHA permanece desejável, sem presumir que ocorreu.

Validação local final: 23 etapas focais concluídas após reexecução integral de
Progressão; ver resultado bruto e reexecução nas [evidências](VALIDACAO.json).
20 `.gs` reproduzidos byte a byte, todos abaixo de 900.000 bytes. Detalhes,
medidas e limitações no [relatório](RELATORIO.md) e [manifesto](manifesto-gs.json).

Google: leitura confirmada da revisão em ANALISE 9; nenhuma escrita, envio,
backup/snapshot integral atual, construção ou migração nativa desta rodada.
Sem ferramenta Apps Script, credencial CLI ou sessão Sheets conectada; acesso
a Drive/Sheets não comprova acesso de execução ao projeto. Seguir o
[roteiro nativo](ROTEIRO-NATIVO.md) com nova leitura, backup e descartável.
Nunca importar XLSX nem reconstruir a revisão preenchida. Oficial, bot e
acessos permanecem fora da publicação. C/D não foram iniciadas.

Próxima ação: aplicação e medidas nativas com ferramenta oficial funcional.
Recomendação: **GPT-6.1 Sol, High**, para preservar entradas e conferir o
contrato junto do código salvo e relido.
