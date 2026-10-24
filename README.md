# Ficha digital do Projeto M

A ficha de personagem digital do **Projeto M**, o sistema de RPG de mesa de Jujutsu Kaisen da guilda — base d20, vários mestres, e personagem que atravessa mesas.

Este repositório guarda **a especificação, as decisões e os validadores**. A ficha em si vai para o Google Sheets.

Os repositórios irmãos: [o sistema](https://github.com/cupcake-mochi/JJK---Project) e [o manual em PDF](https://github.com/cupcake-mochi/JJK---PDF---RPG).

---

## Comece por aqui

**Ficha em PDF:** [seis páginas preenchíveis, quatro cores, estilo próprio](ficha-pdf/README.md). Contas automáticas com ± em cada uma e selos que abrem pelo nível; não mexe na planilha.

**Emissão e salários:** [controles, ciclos, missões e rotina diária](salarios/README.md). Extensão incremental da R53, preservando a fórmula de gastos do jogador e registrando salários em histórico próprio.

**R53 publicada na oficial:** [ficha no Google Sheets, instruções, backup e provas](r53/ENTREGA.md). São 249 cartões editáveis no próprio local, configurações atualizadas, armazenamento técnico oculto e contrato ANALISE12. Entrega no ramo `codex/publicacao-r53`; os planos B47 abaixo são históricos.

**Sem acesso remoto:** [preparação de nuvem, entradas e limites](NUVEM.md). Comandos: `bash nuvem-b47/preparar.sh` e `.venv/bin/python nuvem-b47/conferir.py --smoke`. Referências antes externas agora estão versionadas.

**Retomada atual da CONFIGURAÇÃO B47:** [plano completo e fila organizada](PLANO-RETOMADA-B47.md). Trabalhe no ramo `codex/configuracao-b47`; o `main` ainda contém a base anterior. [Três prompts para chats de nuvem](PROMPT-WORK-B47.md). [Divisão de ramos e integração](PLANO-PARALELO-B47.md).

| arquivo | o que é |
|---|---|
| [`PLANO-RETOMADA-B47.md`](PLANO-RETOMADA-B47.md) | estado vigente, capacidades novas, rota1+2 e todas as entregas restantes |
| [`ESQUEMA-ANALISE.md`](ESQUEMA-ANALISE.md) | contrato exportado, histórico até o formato9 e cuidados da migração |
| [`PROMPT-WORK-B47.md`](PROMPT-WORK-B47.md) | três prompts: implementação/integração, revisão Claude e infraestrutura |
| [`PLANO-PARALELO-B47.md`](PLANO-PARALELO-B47.md) | ramos, responsáveis, limites e fluxo de integração em nuvem |
| [`LEIA-ME.md`](LEIA-ME.md) | o guia da pasta: o que mudou, como rodar, o que ficou pendente |
| [`DECISOES-bloco-A.md`](DECISOES-bloco-A.md) | as cinco decisões que travavam a construção, com o porquê e o que foi medido |
| [`PENDENCIAS.md`](PENDENCIAS.md) | o que ainda espera decisão |
| [`TESTE-CONFIGURACAO.md`](TESTE-CONFIGURACAO.md) | cópia nativa e roteiro de bônus e mudanças |
| [`DESIGN-ficha-digital.md`](DESIGN-ficha-digital.md) | paleta, tipografia, abas, automação |
| [`ESPECIFICACAO-ficha-digital.md`](ESPECIFICACAO-ficha-digital.md) | toda fórmula, todo catálogo, todas as travas |

## Rodar os validadores

```bash
systemd-run --user --scope -q -p MemoryMax=3G -p MemorySwapMax=0 -p CPUQuota=200% nice -n15 env NODE_OPTIONS=--max-old-space-size=1500 ./rodar-tudo.sh
```

São vinte (B47: entrou a regressão da CONFIGURAÇÃO). Quinze passam em qualquer máquina; o
`regressao-kaori-na-ficha.py`, o `regressao-ficha-pessoal.py`, o `regressao-amaldicoada.py`, o `regressao-invocacoes.py` e o `regressao-configuracao.py` precisam de um LibreOffice **com o filtro do
Calc** para recalcular a ficha, e onde ele não existe essa checagem falha alto
em vez de passar em branco — é de propósito. O `regressao-delta.js` roda no
node, porque o Apps Script não pode ser testado de fora; sem node a bateria registra que ele não rodou e termina com falha.

> *Esta linha dizia **oito** enquanto o `rodar-tudo.sh` rodava dez, e o `LEIA-ME` dizia dez ao lado. Duas cópias do mesmo número, duas respostas — e nenhum validador cruzava as duas.*

## As duas regras que não mudam

**Onde a ficha e o manual discordarem, o manual vence.**

**Onde a regra não existe, não se inventa.** O que está em aberto está listado na seção 9 da especificação, e a ficha marca como pendente em vez de chutar número.

## Onde os valores moram

O `decisoes-ficha.json` é o dono dos **valores** das decisões; o `DECISOES-bloco-A.md` é o dono do **porquê**. Nenhum documento repete número de outro, e o `conferir-decisoes.py` confere que eles continuam de acordo.

Isso é a lição nº 9 do projeto aplicada aqui: um número que mora em dois documentos vai divergir.
