# C+D B47 — primeira entrega de conteúdos comuns

> Relatório histórico da primeira entrega. O estado atual das três frentes,
> correções e distinção entre prova local/nativa estão em
> [INTEGRACAO-CD.md](INTEGRACAO-CD.md). A combinação local tem 8.190 chaves.

Base comum `0d4d64e2847dfea29b0e3804ab6f0853c52ea6fd`; contrato publicado em
`ae16895`. Integrador em `codex/b47-capacidade`, integração em
`codex/configuracao-b47`. Personagem e entidades ainda não integrados neste
checkpoint; o commit Claude `50bcc00` apareceu no Git e está em revisão.

## Implementação

`ficha-v01/custom_danos.py` acrescenta dez tipos de dano compartilhados em
CONFIGURAÇÃO, pelo molde aprovado. `DADOS_DANOS` mantém os 15 nomes do livro
e acrescenta custom válido, sem executar descrições. O pool existente da 3a
é alimentado por esse catálogo, preservando os consumidores que o referem por
INDIRECT; os 156 menus de dano das invocações apontam para o catálogo unido.
A entrada livre do tipo de dano da técnica conserva a digitação autorizada.

`ficha-v01/custom_condicoes.py` permite modalidade Condição nos mesmos 30
cartões de Melhoria. Reutiliza campos, consumidores e orçamento. Base de
Condição limitada às condições publicadas; sem base, peso é obrigatório e
Família vazia usa Controle. Família explícita permanece editável conforme o
molde aprovado. Condição sempre exige TR; um Não explícito gera aviso e
exclui o cadastro. Não há mecanismo adicional de Condições nem automação por
prosa. A modalidade Melhoria conserva o comportamento anterior.

Integração nas fontes do gerador e leitor, formato 11 inicial/7.436 chaves;
as 7.356 chaves anteriores conservadas, exceto o valor da versão. Novos
transportes Danos/DanosPainel registrados no emissor e carregador. Geração
canônica concluída: 22 GS, maior 816.375 bytes, soma 5.728.676 bytes,
geração `7adee586c04accf6`. Escrita dos GS usa LF também no Windows.

## Verificações executadas

- Smoke Windows com `PYTHONUTF8=1` passou; Calc permanece indisponível.
- Exportação atual do modelo de comuns concluída. Dez testes em
  `testar-comuns.py` passaram: preservação das quatro colunas da ANALISE,
  chaves/capacidade, 156 menus, livro, entradas antigas, Condições nas mesmas
  vagas, mesclagens novas sem sobreposição, sintaxe e texto literal no leitor.
- Nova cópia nativa, distinta de construção/revisão/oficial:
  `1BzVzrqjKsarh6DCAu6FGZ_yOxy0aBzttfX4n1JH2QFI`. Preparador offline guardado
  pelo ID; 899 pedidos em 31 lotes confirmados. Não reaplicar esses lotes.
- **48 asserções nativas** passaram: primeira/última vaga, `*?~` literal,
  duplicatas excluídas de ambos os registros, colisão com livro, nome numérico
  inválido, texto `  123  ` e `=1+2` preservado, Condição do zero e herdada de
  Atordoado, peso herdado, TR obrigatório, base/modalidade inválidas,
  Melhoria normal, Família explícita em Condição e pool de dano da 3a
  alimentado pelo novo catálogo, com campo/pool restaurados depois.
- **12 seleções de reutilização** passaram, uma por invocação; valor relido e
  validação apontando para DADOS_DANOS. Isso não equivale a testar todas as
  interações de orçamento/cartões da futura combinação.
- **29 campos de cenários restaurados** (17 em CONFIGURAÇÃO e 12 nas
  invocações), com releitura; 40 avisos de cadastros vazios sem erro.
- Releitura final de **968 células delimitadas**, sem erros de fórmula.
  Exportação de 80 campos testada em aba técnica CD_TESTE_ANALISE; ANALISE
  principal da cópia não foi migrada neste ensaio.
- Visual nativo dos pares de dano 1/2 e 9/10 conferido, campos restaurados;
  capturas privadas. Não é auditoria final de todas as abas.
- Pacote gerado: 12 checagens de carregamento em VM, incluindo oito ordens,
  ausência dos dois novos arquivos e rejeição de geração divergente antes de
  acessar Google. Junção de 18 abas e 7.436 chaves preservada.
- Compactação/reexpansão Python/JS passou nas 18 abas mais três fixtures de
  notas; sete cenários de texto passaram, com 76 grupos e quatro leituras
  delimitadas por edição. Isso não é prova de gatilhos nativos da versão nova.

Comando local focal:

```text
python conteudos-b47/comum/testar-comuns.py --modelo nuvem-b47/saidas/cd/comuns-modelo.json --base nuvem-b47/saidas/pecas-modelo.json
```

Os modelos/logs ficam ignorados em `nuvem-b47/saidas/cd/`. Evidências nativas
completas e imagens em `D:\JJK - Project\B47\evidencias\2026-10-16\cd`.
Os hashes públicos identificam fontes/modelo testados em VALIDACAO.json.
Exportações interrompidas durante desenvolvimento foram corrigidas antes da
exportação válida; não contam como aprovadas. A primeira asserção local de
versão esperava inteiro, corrigida para texto conforme o contrato existente.

## Limites e próxima ação

Nenhuma migração C na revisão preenchida, escrita na oficial/bot/main ou
alteração de acesso. Os GS vinculados da cópia de ensaio continuam v10;
esse teste comprova fórmulas/menus da frente comum, não código nativo novo,
gatilhos/autoaltura/cópia funcional ou construção completa de C+D.

Integrar frentes após revisão de seus SHAs e relatórios, gerar/conferir o
pacote, validar a combinação nativamente e executar D. A prova de A+B não
substitui essas etapas. Recomendação: GPT-6.1 Sol, High, para preservar
herança, endereços e dados durante integração.
