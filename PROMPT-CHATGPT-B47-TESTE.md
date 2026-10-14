Preciso que você teste no Google Sheets a fase 1 do B47 da ficha do Ciclo Maldito: a aba oculta ANALISE, que o bot do Discord vai ler. Responda em português do Brasil, tom direto. Não faça commit nem push. Não mude regra nem desenho: se achar defeito, me descreva (aba, célula, o que esperava e o que viu) e só conserte se for no gerador, com a bateria rodando depois.

## Onde está

- **Worktree:** `/media/mizuki/HD Externo II/Claude/Claude 3/.claude/worktrees/ficha-invocacao-update-a350cb`. O B47 está no `git add`, sem commit; a mensagem pronta está em `mensagem-de-commit.txt`. Rode `git status` e `git diff --cached --stat` primeiro.
- **O que foi feito e o roteiro:** fim do `PENDENCIAS.md`, entrada "B47, andamento de 14/10/2026".
- **O plano e o "contrato" das chaves:** `/media/mizuki/HD Externo II/Claude/Planejamento-ficha/B47-analise-e-configuracao/` (`PLANO.md` e `ESQUEMA-ANALISE.md`).
- **Ficha oficial no Sheets:** https://docs.google.com/spreadsheets/d/1u0zWQFVaRTTc_VlrAJsabgAiJ1D4rTYhzG7QQWof1ro/edit

## O que mudou

- Aba nova **ANALISE**, oculta, com quatro colunas (chave · valor · célula · parte) e 2.650 linhas. Cada valor é uma fórmula que lê a ficha.
- Ela mora num arquivo de script novo, **`apps-script/Analise.gs`**, juntado pelo `juntarAbas_` do `Ficha.gs`. O projeto do Apps Script passa a ter **seis** arquivos: `Codigo.gs`, `Ficha.gs`, `Habilidades.gs`, `Invocacoes.gs`, `Origens.gs` e `Analise.gs`.
- O `Codigo.gs` devolve a fórmula a quem escrever na ANALISE.
- A troca de paleta não passa pela ANALISE (aba oculta).
- Na raiz da worktree, o leitor **`ler-analise.py`**: lê a aba pelo link aberto (CSV da aba) ou da ficha gerada, e responde como o bot.

## Roteiro do teste no Sheets

1. Cole no projeto do Apps Script os **seis** `.gs` da pasta `apps-script/`, incluindo o `Analise.gs` novo, e substitua os que já existem. Rode `construir()` (e `continuar()`/`acabar()` se ele pedir), como nas montagens anteriores. Anote o tempo total.
2. **A aba existe e está oculta:** ela não aparece nas abas de baixo; aparece em Exibir › Abas ocultas (ou no menu ≡ de abas). Linha 1: `chave · valor · célula · parte`. Última linha com dado: 2.651.
3. **Os valores leem a ficha:** confira estas linhas com a ficha em branco:
   - `formato.versao` = 1; `ficha.versao` = 1.0; `ficha.livro` = Ciclo Maldito R51.
   - `origem` = o que estiver no menu ORIGEM da FICHA.
   - `pericia.atletismo.treino` = 0. Marque o treino de Atletismo na FICHA: passa a 1.
   - `sequela.1` = 0. Marque a primeira caixinha das Sequelas na FICHA: passa a 1.
   - `defesa` = o mesmo número da caixa DEFESA da FICHA.
   - `aviso.escolhas_de_pericia` = o mesmo texto da caixa das escolhas de perícia da FICHA.
4. **A conta volta:** reexiba a aba, escreva qualquer coisa numa célula da coluna B e confirme que a fórmula volta, com o aviso no canto. Oculte a aba de novo.
5. **A paleta não pinta a ANALISE:** troque a paleta na CARTEIRA e confira que a ANALISE continua sem cor.
6. **O leitor pelo link:** com a ficha aberta para leitura por link, rode na worktree:
   `python3 ler-analise.py "https://docs.google.com/spreadsheets/d/1u0zWQFVaRTTc_VlrAJsabgAiJ1D4rTYhzG7QQWof1ro/edit"`
   Ele tem de mostrar "2650 chaves" (ou perto disso) e um veredito. Me mande a saída inteira. Se o CSV vier com vírgula decimal ou VERDADEIRO/FALSO, o leitor já normaliza; se aparecer outro formato estranho, anote qual chave e o valor cru.
7. **Nada quebrou:** abra a FICHA, a FICHA PESSOAL, a FICHA AMALDIÇOADA e a INVOCAÇÕES e confira que montaram como antes (B46).

## Regras

- Teste pesado no PC (LibreOffice) um por vez, com teto: `systemd-run --user --scope -q -p MemoryMax=5G -p MemorySwapMax=0 nice -n 15 <comando>`. Para matar processo, use o PID, nunca `pkill -f`.
- Se precisar mexer, conserte no gerador (`ficha-v01/*.py`, `python3 ficha-v01/monta.py`), nunca nos `.gs` gerados (só o `Codigo.gs` é escrito à mão).
- No fim, deixe tudo no `git add -A`, atualize a entrada B47 do `PENDENCIAS.md` com o resultado de cada item do roteiro e me passe o comando de commit (`git commit -F mensagem-de-commit.txt`), sem rodar.

Quando terminar, me mande um resumo curto: o que passou, o que falhou (com aba, célula e valor), o tempo da montagem e a saída do `ler-analise.py` pelo link.
