Preciso que você termine uma tarefa que outro agente começou e não fechou: pôr a ficha digital do Ciclo Maldito (Google Sheets gerada por Python + Apps Script) em dia com o livro R51. Responda em português do Brasil, tom direto. Não faça commit nem push: deixe tudo no `git add` e me diga o comando. Antes de decidir qualquer regra nova, me pergunte.

## Onde está tudo

- **Pasta de trabalho (worktree):** `/media/mizuki/HD Externo II/Claude/Claude 3/.claude/worktrees/ficha-invocacao-update-a350cb`, ramo `claude/ficha-invocacao-update-a350cb`. O trabalho está no `git add`, sem commit; a mensagem pronta está em `mensagem-de-commit.txt`. Rode `git status` e `git diff --cached --stat` primeiro.
- **Registro do que foi feito e do que falta:** fim do `PENDENCIAS.md`, entrada "B46, andamento de 14/10/2026". Leia inteira antes de começar. As entradas B45 e B43 do mesmo arquivo mostram o padrão de registro e de roteiro de teste.
- **Livro (fonte das regras):** `/home/mizuki/JJK-v0.341-para-subir/sistema/05-material/livro/ciclo-maldito-r41/LIVRO-COMPLETO.md` (R51). O que mudou: `revisao-de-regras/MUDANCAS-DE-REGRA.md`, seção E (itens 24, 33, 40, 46, 101, 151, 188 a 197).
- **Estudo aprovado pelo Mizuki:** `mockup/origens-estudo.html`.

## Regras de trabalho

1. Os `.gs` em `apps-script/` (`Ficha.gs`, `Invocacoes.gs`, `Habilidades.gs`) são GERADOS: o conserto vai no gerador `ficha-v01/*.py` e se gera com `python3 ficha-v01/monta.py` (demora ~2 min). Só o `apps-script/Codigo.gs` é escrito à mão.
2. O PC tem 15 GB e já reiniciou por falta de RAM. Testes pesados (os que usam LibreOffice) rodam **um por vez**, sempre com teto:
   `systemd-run --user --scope -q -p MemoryMax=5G -p MemorySwapMax=0 nice -n 15 python3 <teste>`
   No fim: `systemd-run --user --scope -q -p MemoryMax=5G -p MemorySwapMax=0 nice -n 15 ./rodar-tudo.sh`
   Antes de rodar, confira com `pgrep -af "soffice|regressao|arnes|conferir"` se não sobrou processo. Para matar, use o PID, nunca `pkill -f`.
3. A cópia da planilha precisa funcionar só de copiar: nada de gatilho instalável nem menu de ativar. Só `onEdit` e `onOpen` simples.
4. A troca de paleta pinta pela cor de fábrica de cada célula (`PALETA_DE_FABRICA_` no `Codigo.gs`). Toda caixa nova tem de usar só essas cores; confira com a `regressao-paleta.js`.
5. Liste todas as falhas de cada teste de uma vez, em vez de parar na primeira.

## Decisões já tomadas pelo Mizuki (não reabrir)

- **Origens (livro R45):** na FICHA PESSOAL, o bloco ORIGEM no lugar dos dois Legados. Três cartas (marcante, menor 1, menor 2), cada uma com menu filtrado pela Origem, cuja primeira opção é "✎ Criada com o mestre" (e aceita nome escrito); texto do livro embaixo; frequência. Com a criada, a caixa de texto é do jogador. Embaixo: Legados de história (texto livre, sem efeito), ofício compatível (só Corpo Amaldiçoado) e Talento de CE4 (só Restrição corporal).
- **Painel retrátil à direita da FICHA** (grupo de colunas fechado): só as escolhas do jogador (marcante, menores, Legados de história). Nada do catálogo.
- **Morrendo (R50/R51):** linha só de leitura embaixo das barras, com Aguentar (1/4 da vida máxima, para cima), Insistir 1ª vez (1/3, até 15 × maior Classe), Insistir 2ª em diante (1/2, mesmo teto) e "PRAZO ATÉ SER DERROTADO" (3 rodadas menos 1 por Sequela), bem explicado. Exemplo do livro: máximo 93, Classe 3 → 24, 31 e 45.
- **Sequelas:** três caixinhas de marcar, como os testes contra a morte do D&D. O descanso longo desmarca.
- **INVOCAÇÕES:** ofício compatível em menu que aceita outro valor; a entidade criada acompanha o nível do invocador até o último nível da Classe em que foi criada; a domada conserva o nível.
- **Pacto:** menu "TAMANHO DO GANHO" (Pequeno, Médio, Grande, Enorme; Promessa sem tamanho). A caixa VAGAS conta só o permanente e o de restrição.

## O que já está feito (não refazer)

Fonte no R51; `ficha-v01/extrair_origens.py` → `origens-do-livro.json`; arquivo de dados (`catalogo-projeto-m.json`) com as Origens novas e sem Legados com tipo; `conferir-catalogo.py` reescrito (passa); `ficha_pessoal.py` (bloco ORIGEM, espelho e contas do Morrendo); `estado_do_personagem.py` e `linhas_novas.py` (16 linhas novas na FICHA); `indice_ficha.py` (índice `sequela 1..3`, `morrendo *`, `marcante`, `menor 1`, `menor 2`); `painel_origem.py` (novo, ligado no `monta.py`); `ficha_invocacoes.py`; `ficha_amaldicoada.py` (tamanho do ganho); `extrair_tecnica.py` (régua do pacto, teto da Cortina); `extrair_invocacao.py` (criada até o fim da Classe); `Codigo.gs` (notas novas, descanso com as caixinhas, `textoDaCapacidade_`).

Passaram: conferir-catalogo, conferir-kaori, conferir-progressao, regressao-exemplos, arnes, revisao-cetica, conferir-decisoes, arnes-decisoes e os cinco `--confere` dos extratores.

## O que falta, em ordem

1. **`conferir-ficha-xlsx.py`:** a última rodada terminou com só duas falhas (as checagens novas do B46 passaram todas):
   - "a CARTEIRA acaba na mesma coluna da FICHA" (`{'FICHA': 50, 'CARTEIRA': 47}`): o painel novo aumentou as colunas da FICHA. Ajuste a checagem para ignorar o grupo de colunas do painel, sem mexer na CARTEIRA.
   - "o arquivo cabe no Apps Script (928 KB, o limite é ~1 MB)": veja qual `.gs` passou do limite que o teste usa (provavelmente o `Ficha.gs`, que cresceu com os textos das Origens na DADOS). Se for preciso, leve a tabela `origem_cap` (textos das capacidades) para um `.gs` à parte, no molde do `Habilidades.gs`, ou meça e me diga antes de escolher.
   Rode de novo até o fim e confirme "A FICHA CONFERE".
2. **Regressões que ainda cobram o desenho antigo** (Legado, Sequela como número 0–3, Feto, "corpo pela técnica", "sem energia" minúsculo, 11 linhas novas): `regressao-ficha-pessoal.py`, `regressao-construir.js`, `regressao-pessoal.js`, `regressao-amaldicoada.py` (linhas 545–552 e 846 usam "Feto · Sem Técnica" e "Restrição Celestial · sem energia"; os nomes novos são "Híbrido · Sem Técnica" e "Restrição Celestial · Sem Energia"), `regressao-kaori-na-ficha.py`, `comparar-ficha-01.py` (o painel acrescentou as colunas AV a AX na FICHA), `arnes-pessoal.py`, `arnes-amaldicoada.py`, `arnes-invocacoes.py`, `regressao-invocacoes.py` (o nível da criada mudou: com nível fixo 6 e invocador no 11, ela fica no 8), `regressao-delta.js` e `arnes-delta.py`. Atualize cada um para o desenho novo; não afrouxe checagem que pega defeito real.
3. **Pintura das partes novas:** `node regressao-paleta.js` e `node regressao-arte.js`. Se o painel ou as caixinhas não forem pintados, conserte no gerador.
4. **`./rodar-tudo.sh` inteiro**, com o teto da regra 2. Ele tem de terminar em "OS DEZENOVE PASSARAM".
5. **Ver a aba montada contra o estudo:** `python3 medidas/ver-aba.py` desenha a aba a partir do `Ficha.gs`. Compare com `mockup/origens-estudo.html` e me liste o que bate e o que difere.
6. **Registro final:** troque a entrada "B46, andamento" do `PENDENCIAS.md` por uma entrada B46 fechada, com:
   - o que mudou, item por item do livro;
   - os testes que passaram;
   - um roteiro de teste no Sheets que nomeie a aba, a caixa e o valor esperado, com a conta até o número. Exemplos:
     - FICHA, vida máxima 93 e CLASSE MÁXIMA 3: AGUENTAR 24, INSISTIR 1ª 31, INSISTIR 2ª 45, PRAZO "3 rodadas".
     - Marque duas caixinhas: PRAZO "1 rodada". Descanso "Longo · fora": as três desmarcam.
     - FICHA PESSOAL, Origem Descendente, marcante Zenin: o menu das menores mostra Cofre da Família, mas não Ensaio Partilhado.
     - Menor com "✎ Criada com o mestre": a caixa fica vazia e aceita texto. Volte a uma do livro: o texto do livro volta.
     - INVOCAÇÕES, aquisição Criação, nível fixo 6, invocador no 11: NÍVEL 8.
     - Pacto: o menu TAMANHO DO GANHO tem cinco opções.
     - A planilha copiada funciona sem ativar nada.

   Atualize também o `mensagem-de-commit.txt` (um parágrafo longo, sem acento, terminando com a linha `Co-Authored-By`), dê `git add -A` e me passe o comando de commit. Não rode o commit.

Quando terminar, me mande um resumo curto: o que mudou, o que passou, o que não rodou e o que ficou para eu decidir.
