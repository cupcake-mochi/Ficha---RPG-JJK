# Auditoria de Morrendo e socorro — 04/11/2026

Base PR55 `20aba91899cae8793dd69c259dab9e5aa0643e36`, sobre PR54.
Ramo de diagnóstico separado. Não altera código de produção, oficiais,
fichas de jogador ou PR31. Sem merge. Apenas uma cópia descartável de QA.

Regra confrontada: livro R65, commit `a98d4af981cd7166a403f7189eeb1bc3a22e4ad4`,
Dano e recuperação → Morrendo/Socorro. O livro usado é a mesma referência
local dos ensaios anteriores; não houve busca de outra versão nesta rodada.

## Contas aprovadas no Google

`python3 r53/testes/morrendo_nativo.py` prepara uma tabela com as quatro
fórmulas extraídas dos GS reais. Substitui somente suas referências de entrada
por células controladas; usa DADOS_CONFIG S10:S14 da cópia, relidos como
1/4, 1/3, 1/2, 15 e 3. Não reimplementa o cálculo da ficha no campo de resultado.

Onze cenários, quatro resultados comparados por cenário (44 comparações):
máximos 1/3/4/11/45/46/93/395/100/20; Classes 1/2/3/7; zero a três caixas
de Sequelas e extras. Todos os onze indicadores OK foram TRUE no Google.
Inclui os exemplos do livro: 93/Classe 3 → 24,31,45; 395/Classe 7 → 99,105,105.
Janela: 3/2/1 rodadas e derrota imediata com três ou mais Sequelas, contando extras.

Isso verifica as contas, não o acompanhamento completo de uma queda.

## P1 — Aplicar cura não distingue tratamento de Morrendo

A nova ação da PR54 grava diretamente FICHA!D26, inclusive quando a vida
atual é zero. Não guarda tratamento, escolha de Aguentar/Insistir ou janela.

`node r53/testes/morrendo_cura_diagnostico.js` executa a função real
`aplicarCuraRecebida` com serviços simulados e confirmação positiva:

- Situação: Morrendo, Aguentar, máximo de referência 23, cura recebida 3.
- Livro: requer 6 de tratamento; vida permanece 0 e tratamento acumula 3.
- Ação atual: grava D26=3, sem registro separado de tratamento.

**Não foi execução nativa do menu nesta rodada.** O diagnóstico retorna
`conforme:false`; não é um teste aprovado nem deve ser contado entre os 44.
O problema afeta a ação de cura em Morrendo, não invalida o ensaio anterior
com vida positiva nem implica que toda edição manual do ± seja cura.

Antes de promover a PR54, tratar essa condição explicitamente. Uma contenção
mínima é impedir a aplicação automática a zero com orientação para socorro;
a solução completa exige registrar a queda e acumular tratamento separado.
Não reduzir todo ajuste positivo do ± nem usar vida temporária como tratamento.

## P2 — Painel usa máximo atual, não a referência da queda

O livro exige anotar e conservar o máximo no momento da queda. D41/O41/Z41
leem J26 diretamente. Não foi encontrado estado persistente da queda no
fluxo revisado. A ficha hoje funciona como calculadora dinâmica nesses campos.

Ensaio integrado na cópia com a vida D26 mantida em 0:

| Máximo controlado J26 | Aguentar D41 | Insistir 1 O41 | Insistir 2 Z41 |
|---|---:|---:|---:|
| 23 | 6 | 8 | 12 |
| 40 | 10 | 14 | 15 |

Preparação via API, sem disparar onEdit: a mudança prova a dependência da
fórmula, não simula automaticamente a entrada no estado Morrendo. Para uma
queda cuja referência era 23, os requisitos devem continuar 6/8/12.
Os números atuais são corretos como previsão de uma nova queda; a apresentação
não distingue previsão e requisito registrado da queda atual.

Solução recomendada: separar a previsão do registro da queda e conservar
máximo de referência, escolha, tratamento e janela restantes. Não usar fórmula
circular para congelar valores, nem ampliar silenciosamente o contrato ANALISE.

## Limites

Não foram testados nativamente o menu Aplicar cura com vida zero, a contagem
de rodadas/dano posterior, resgates expressos, estabilização, perda de estado
entre cenas, custom de campanha alterando as frações ou Android. Não há
certificação de todas as mecânicas. Nada foi corrigido silenciosamente nesta
rodada; os dois problemas estão reproduzidos/documentados para implementação.

A cópia deixa J26=40 e D26=0 como entradas controladas de ensaio; não é modelo
para distribuir. Snapshot inicial, respostas nativas e tabela estão fora do Git.
Somente gerador de teste e relatório sanitizado são versionados.

Sol/High para implementação do fluxo; Sol/Medium para revisão focal, conforme AGENTS.md.
