# Medição de desempenho no Google · 25/10/2026 (Claude)

Cópia descartável da Ciclo Maldito oficial, criada pelo Drive:
`1ZJLQzIDCv5BaD_QvNo_jne_B2YSEDTbYFDj1tCaWfGs` ("TESTE desempenho — pode apagar"),
projeto `1Ane40rqYgeEB-brWEfkzqN2kpT7g7Dnr8VnEIcGDbaT4pCM50z4RdHv3`. As oficiais
não foram tocadas. O código instalado na cópia é o das oficiais **antes** da
correção da corrida (`d92f846e…`). As funções de medição estão em
`medir_carga.gs`, coladas no arquivo vazio `AnaliseFontes.gs` da cópia.

## Edições pelo acionador simples (registro de Execuções)

| Edição | Duração | Status |
|---|---:|---|
| Caminho Emanador (personagem novo, caminho leve) | 19,1 s | concluído |
| Trilha Ressonante (caminho leve) | 15,8 s | concluído |
| XP 3000 (caminho geral, abre o módulo) | 30,8 s | **tempo limite** |
| ± da vida −3 (caminho geral, abre o módulo) | 30,6 s | **tempo limite** |
| Clique (`onSelectionChange`) | 1,7–2,4 s | concluído |
| Abrir a planilha (`onOpen`) | 22,2 s | concluído |

## As mesmas edições pelo editor (sem o corte de 30 s)

`medirEdicoes` grava a célula e chama o `onEdit`. A 1ª edição abre o módulo; a
2ª já o encontra aberto (cada gatilho real é uma execução nova e sempre o abre).

| Rodada | XP 1ª | XP 2ª | vida 1ª | vida 2ª |
|---|---:|---:|---:|---:|
| com ANALISE (1) | 33,2 s | 30,5 s | 17,3 s | 17,0 s |
| com ANALISE (2) | 40,8 s | 27,2 s | 17,6 s | 18,9 s |
| sem ANALISE | 36,8 s | 29,6 s | 16,7 s | 15,6 s |

## Abrir o módulo (`medirModulo`, uma execução)

| Etapa | Inteiro (21,4 MB) | Sem a montagem (8,3 MB, 31 tabelas) |
|---|---:|---:|
| descompactar | 3.331 ms | não medido (proporcional: ~1,3 s) |
| hash | 423 ms | não medido (~0,2 s) |
| correções de texto (`r53Correcao*`) | 4.472 ms | não medido (~1,7 s) |
| compilar | 618 ms | 242 ms |
| rodar escopo global | 1.546 ms | 194 ms |

## Operações básicas (`medirLeituras`)

| Operação | com ANALISE (2 amostras) | sem ANALISE |
|---|---:|---:|
| primeira leitura de uma célula | 3,1 / 2,4 s | 1,7 s |
| leitura seguinte, nada pendente | 2 ms | 2 ms |
| ler a DADOS inteira | 7,0 / 7,5 s | 7,0 s |
| ler a FICHA inteira | 6,6 / 7,6 s | 6,8 s |
| gravar célula solta e ler | 4,8 / 5,3 s | 4,7 s |
| gravar XP e ler | 4,5 / 5,2 s | 3,3 s |
| gravar Caminho e ler (ida/volta) | 5,6 · 4,8 / 4,9 · 5,1 s | 4,0 · 5,5 s |
| apagar e `flush` | 2,5 / 2,4 s | 2,5 s |

## Leitura dos números

- Gravar e depois ler custa ~5 s mesmo numa célula que nada usa: o custo é da
  planilha inteira, não das fórmulas que dependem da célula.
- Ler a DADOS ou a FICHA inteiras custa ~7 s cada. O caminho geral do XP lê a
  DADOS duas vezes (`onEdit` e `nivelPelaXP_`).
- Tirar a ANALISE muda pouco (de 0 a ~1,5 s, dentro da variação entre rodadas).
- Abrir o módulo custa ~10 s e é pago em toda edição que não seja Caminho,
  Trilha ou treino; as correções de texto aplicadas por cima do pacote são a
  maior fatia (4,5 s).

## Depois: opção 1 e pacote leve (segunda cópia)

Cópia nova da oficial, com a ANALISE: `1kQuSggqnX1C6hu07HlTRXd_UYyyBGLJdHDgdM4Oyovg`
("TESTE pacote leve — pode apagar"), projeto
`1Sl3XTWIfZTb8o1EVfnhy46TJ0dFCXDqgPWmlMbFSrMDCPkB6-6vdd3iY`. Medido antes e depois
de rodar `instalar_pacote_leve.js` no editor dela. O módulo gerado no navegador
tem o mesmo SHA-256 do testado no node:
`2667ef41d84e44f565228bae47d7a6b9cf08bb7bfef8c60f2467383075aaee53`.

| Medida | Antes | Depois |
|---|---:|---:|
| Pacote de dados (base64) | 3,6 MB em 5 arquivos | 1,9 MB em 3 arquivos |
| Módulo descompactado | 21,4 MB | 8,3 MB |
| Abrir o módulo (`medirAbrirModulo`) | 11,4 s | 1,8 s |
| XP pelo editor, 1ª / 2ª | 29,9 / 27,2 s | 22,2 / 17,9 s |
| ± da vida pelo editor, 1ª / 2ª | 17,2 / 17,6 s | 9,3 / 9,0 s |

Pelo acionador simples, na planilha, depois do pacote leve (todas concluídas e
conferidas na tela):

| Edição | Duração | Resultado |
|---|---:|---|
| Caminho Emanador | 10,2 s | concluído |
| Trilha Ressonante | 10,5 s | concluído |
| Vida atual = 20 (edição comum) | 10,6 s | concluído |
| ± da vida −3 | 11,5 s | vida 20 → 17, caixa limpa |
| Vida temporária 100 | 12,0 s | cortada para 25 (metade da máxima 50) |
| Abrir a planilha (`onOpen`) | 2,1 s | concluído (era 17,9 s) |
| Clique (`onSelectionChange`) | 1,6–3,2 s | concluído |

O XP pelo editor continua alto porque a caixa de XP é uma conta: escrever nela
devolve a fórmula (gravar e reler, ~5 s) antes de subir o nível. O jogador sobe
XP pelas missões da FICHA PESSOAL, que já têm caminho próprio.

## As quatro opções

1. **Ler uma vez e gravar no fim, nas edições comuns** — feita no `Codigo.gs`: o
   índice sai do molde (`indiceEstatico_`, igual ao do caminho leve nas 89 chaves),
   a DADOS só é lida quando a edição precisa (Caminho e XP) e por faixa fixa
   (`faixaDoMolde_`), e ±, temporária e descanso leem numa ida só (`lerCelulas_`).
   No contador do node: ± da vida 8 → 1 leitura, temporária 6 → 1, XP 11 → 4,
   célula comum 4 → 0.
2. **Escopo global preguiçoso** — não precisou de mudança à parte: sem as tabelas
   da montagem, rodar o escopo global caiu de 1,5 s para 0,2 s (medido).
3. **Pacote leve** — feita. Sai o que só serve para montar (DADOS_R53, MONTAGENS,
   catálogo e as tabelas da ANALISE) e os remendos `r53Correcao*` passam a vir
   embutidos. `construir`, `continuar` e `acabar` recusam com aviso: a montagem
   precisa do pacote completo, que continua no repositório.
4. **Aliviar a ANALISE** — não aplicada na planilha. Apagar a aba inteira mudou de
   0 a 1,5 s (dentro da variação) e ela é o contrato do bot. O molde dela já saiu
   do módulo de edição na opção 3; só deixa de existir a volta automática da
   fórmula quando alguém escreve na ANALISE oculta.

## O que ainda falha, com o pacote leve (mesma cópia)

| Edição pelo acionador simples | Duração | Status |
|---|---:|---|
| CARTEIRA, célula qualquer (A1) e o desfazer | 30,7 s e 30,6 s | tempo limite |
| FICHA AMALDIÇOADA, célula livre (B500) | 30,6 s | tempo limite |
| FICHA PESSOAL, arma na mão principal (D64) | 30,6 s | tempo limite |
| CARTEIRA, troca de paleta | 14,9 s (cor visível em ~10 s) | concluído |

- **Sincronização das Famílias em cópia nova.** `r53SincronizarFamilias_` compara o
  amparo atual com `r53_amparo_direto` das propriedades do documento, que não vão
  na cópia da planilha. Sem estado anterior, toda edição em CARTEIRA, FICHA
  AMALDIÇOADA, INVOCAÇÕES e CONFIGURAÇÃO tenta acertar os 249 cartões (81 idas no
  contador do node), estoura e não grava o estado: repete em toda edição.
- **FICHA PESSOAL.** `textoDaCapacidade_` e `pessoalEditada_` releem o índice
  pessoal da DADOS em toda edição da aba, e o caminho das notas faz `flush`, lê a
  DADOS inteira pelo `getDataRange` e reescreve as notas vivas (12 idas no node).
- **Força e atributos.** `fichaMexeNaPessoal_` lê a DADOS inteira e refaz as notas
  vivas (8 idas).
