# Roteiro no PC: trecho do salário no Codigo das oficiais · 16/11/2026

O que falta do conserto das datas do salário (PR #128). A fórmula nova do `DADOS_SALARIOS!Q2` já está nas duas oficiais
(PR #129) e resolve o defeito sozinha. Falta só o texto dentro do Codigo, para um `salarioPrepararFormulas_` ou um
`construir()` não devolver a fórmula antiga.

**Por que precisa do Mizuki no PC.** Com a janela do app escondida, o editor do Apps Script abre em somente leitura no
navegador do app: o botão Implantar some e o Ctrl+S não grava. Tentado duas vezes em 16/11, no Ciclo; o Codigo ficou
idêntico (`a7f6f33050c3`). Com o painel do navegador aberto (Ctrl+Shift+B), deve gravar. A causa não foi confirmada: se
continuar em somente leitura com o painel aberto, é permissão da conta naquele navegador.

Os links das duas oficiais e dos projetos estão no `r53/OFICIAIS.md`.

## Em cada oficial (Ciclo Maldito primeiro, depois Era da Revolução)

1. **Abrir o projeto do Apps Script** na conta dona das fichas e conferir, no console, o hash do arquivo que tem o
   `function salarioCongelar_(`:
   - Ciclo, lido em 16/11: `a7f6f33050c3`. Era: não foi lido; anotar o que aparecer.
   - Se o hash do Ciclo for outro, alguém mexeu depois: parar e ler o que mudou.
2. **Backup nativo:** Implantar → Nova implantação → tipo Biblioteca, descrição
   "Antes das datas do salário sem hora (16/11/2026)". Anotar o número da versão.
3. **Gerar e colar o trecho:**
   `node r53/diagnostico-android/preparar_salario_datas.js > trecho.js`, colar no console do editor.
   - Resposta esperada: `{"antes":"…","depois":"…","trechos":2}`. No Ciclo, `a7f6f33050c3` → `a52ed1f343d4`
     (conferido em 16/11, na tela, sem gravar).
   - `ERRO: … encontrado 0 vez(es)` quer dizer Codigo diferente do esperado: não insistir.
4. **Salvar:** clicar dentro do editor, Ctrl+S, esperar "Salvo no Google Drive".
5. **Conferir:** recarregar a página e ler o hash de novo. Tem de ser o `depois` do passo 3, com
   `MAX(INT(ult);em)` uma vez e `salarioData_(Math.floor(l[1]))` uma vez. Se voltou o hash de antes, não gravou.
6. **Planilha:** reler `DADOS_SALARIOS!Q2` pela API. Tem de continuar com `MAX(INT(ult);em)`.

## Depois das duas

- Registrar no `r53/OFICIAIS.md`: os hashes de antes e depois, o número da versão de backup de cada projeto, e tirar
  o "Não aplicado: o trecho no Codigo" da entrada "Salário: início do período sem hora".
- Para voltar: `node r53/diagnostico-android/preparar_salario_datas.js --reverter`, que devolve o Codigo idêntico ao de
  antes (conferir pelo hash), ou restaurar o arquivo da versão de backup.

## O que este roteiro não cobre

- Nenhum fechamento de salário de verdade foi rodado no Sheets com o conserto. A validação é a do
  `r53/testes/salario_datas.js` (planilha de mentira). Um ensaio numa cópia, com a emissão num dia passado e o
  intervalo em 1 dia, fecha essa ponta.
- Fichas já copiadas por jogadores continuam com a fórmula e o código antigos.
- Planilha em fuso diferente de Brasília: o `salarioDia_` lê as datas da planilha no fuso de São Paulo. Num fuso a
  leste, uma data sem hora pode ser lida como o dia anterior. É anterior a este conserto e não foi mexido.
