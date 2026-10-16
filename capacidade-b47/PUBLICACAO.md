# Publicação · capacidade B47 · 16/10/2026

Base: `4187df37640b5e0966cdb342f56f9ee0a0daf16a`, com a preparação de nuvem.
Código de produção testado: `f1ff7a6785f179df78a91a619bbd60388acd4bc1`.
Correção da regressão histórica e reexecução: `8276ca6fbdc11ff0f35547c7935a09441b0a6e4a`;
único diff de código naquele fechamento: `regressao-progressao.py`.
O fechamento local f3a3fbd acrescentou documentação/evidências.
Retomada nativa: ferramentas em `186e844`, revisão adicional `efd8dd8`
integrada em `3323803`, auditor/evidência parcial em `6a226c3`.
Fontes de produção e 20 `.gs` permanecem iguais a f1ff7a6.

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
Revisão adicional recebida em efd8dd8 examinou o núcleo em 8276ca6 e não
encontrou bloqueios locais. Os helpers posteriores de migração/auditoria não
receberam essa revisão externa; foram testados pelo integrador.

Validação local final: 23 etapas focais concluídas após reexecução integral de
Progressão; ver resultado bruto e reexecução nas [evidências](VALIDACAO.json).
20 `.gs` reproduzidos byte a byte, todos abaixo de 900.000 bytes. Detalhes,
medidas e limitações no [relatório](RELATORIO.md) e [manifesto](manifesto-gs.json).

Retomada PC partiu de `ad1b55de210e534b950a3e66ecb2f91f2f2b8d27`.
Correções: `1448436` (visibilidade herdada), `50ba7c7` (Windows/LF) e
`1341d48` (envio sem formatos redundantes, fracionamento e testes).
O fechamento é publicado nos dois ramos autorizados por avanço normal.

**A+B concluídos nativamente.** Código, menus, casos positivos/negativos,
textos, gatilhos espontâneos na cópia e construção integral foram conferidos.
Prova conjunta da descartável: [VALIDACAO-NATIVA-PC.json](VALIDACAO-NATIVA-PC.json).
Construção reservada: 17 abas/1.968 menus; 672s aproximados nas três execuções.
Medidas de interface/releitura em separado das durações dos acionadores.

Revisão original migrada com backup/snapshot fresco, guardas e releitura igual:
ANALISE 10, 7.356 chaves, 509 entradas/notas exatas, zero erros e divergências
em 400.917 células de 17 abas. Mais 22.094 células superiores/carteira/ficha
pessoal/cache comparadas ao backup, sem divergências inesperadas. Os 20 GS e
manifesto foram relidos integralmente iguais após a aplicação. Prova final:
[REVISAO-NATIVA-PC.json](REVISAO-NATIVA-PC.json). Incidentes de timeout,
confirmação por releitura e otimização validada estão no
[checkpoint PC](RETOMADA-PC.md); nunca reaplicar o diário concluído.

Oficial, main, bot e acessos intactos. C/D não iniciadas. Bot/formato 10 e
variante histórica formato 4 continuam externos. Calc indisponível e bateria
POSIX impedida por fcntl no Windows; não foram contabilizados como aprovação.
Os GS continuam exatamente os de f1ff7a6; sem nova geração pesada.

Próxima ação/modelo: **GPT-6.1 Sol, High**, para conferir o fechamento e o uso
de A+B. Nova etapa C/D somente mediante nova autorização.
