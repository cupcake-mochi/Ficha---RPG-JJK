# Ficha digital do Projeto M

A ficha de personagem digital do **Projeto M**, o sistema de RPG de mesa de Jujutsu Kaisen da guilda — base d20, vários mestres, e personagem que atravessa mesas.

Este repositório guarda **a especificação, as decisões e os validadores**. A ficha em si vai para o Google Sheets.

Os repositórios irmãos: [o sistema](https://github.com/cupcake-mochi/JJK---Project) e [o manual em PDF](https://github.com/cupcake-mochi/JJK---PDF---RPG).

---

## Comece por aqui

| arquivo | o que é |
|---|---|
| [`LEIA-ME.md`](LEIA-ME.md) | o guia da pasta: o que mudou, como rodar, o que ficou pendente |
| [`DECISOES-bloco-A.md`](DECISOES-bloco-A.md) | as cinco decisões que travavam a construção, com o porquê e o que foi medido |
| [`PENDENCIAS.md`](PENDENCIAS.md) | o que ainda espera decisão |
| [`DESIGN-ficha-digital.md`](DESIGN-ficha-digital.md) | paleta, tipografia, abas, automação |
| [`ficha-invocacao/`](ficha-invocacao/) | a ficha da invocação, planilha separada. O dono dos valores é o [`invocacao.json`](invocacao.json) |
| [`ESPECIFICACAO-ficha-digital.md`](ESPECIFICACAO-ficha-digital.md) | toda fórmula, todo catálogo, todas as travas |

## Rodar os validadores

```bash
./rodar-tudo.sh
```

São treze, e os treze passam.

> *Esta linha dizia **oito** enquanto o `rodar-tudo.sh` rodava dez, e o `LEIA-ME` dizia dez ao lado. Duas cópias do mesmo número, duas respostas — e nenhum validador cruzava as duas.*

## As duas regras que não mudam

**Onde a ficha e o manual discordarem, o manual vence.**

**Onde a regra não existe, não se inventa.** O que está em aberto está listado na seção 9 da especificação, e a ficha marca como pendente em vez de chutar número.

## Onde os valores moram

O `decisoes-ficha.json` é o dono dos **valores** das decisões; o `DECISOES-bloco-A.md` é o dono do **porquê**. Nenhum documento repete número de outro, e o `conferir-decisoes.py` confere que eles continuam de acordo.

Isso é a lição nº 9 do projeto aplicada aqui: um número que mora em dois documentos vai divergir.
