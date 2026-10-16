# Trabalhar na B47 sem o PC original

O repositório contém gerador, layout, catálogos, código Apps Script, arte/fontes, decisões, estudos aprovados e referências de teste. A preparação abaixo não precisa de acesso remoto ao PC. A conexão com Google Sheets/Apps Script é uma etapa independente, feita com a conta autorizada no ambiente de nuvem.

## Início em um checkout novo

Selecione o repositório `cupcake-mochi/Ficha---RPG-JJK` e o ramo do seu papel, conforme [PLANO-PARALELO-B47.md](PLANO-PARALELO-B47.md). Não use `main` como base. Caso o serviço gere outro nome de branch, preserve a base e informe o nome ao integrador.

Ambiente de referência: Linux, Python **3.12**, Node **20**, Git. O diagnóstico aceita Python 3.10–3.12 e Node >= 18, mas isso não equivale a testar todas as combinações. Nenhum pacote npm é necessário para as regressões Node existentes. Dependências Python e transitivas estão fixadas em [requirements.txt](requirements.txt).

```bash
bash nuvem-b47/preparar.sh
.venv/bin/python nuvem-b47/conferir.py --smoke
```

Se o Python estiver em outro nome: `PYTHON=python3.12 bash nuvem-b47/preparar.sh`. Ative o ambiente antes de executar os testes antigos que chamam `python3` como subprocesso:

```bash
source .venv/bin/activate
```

Na configuração do ambiente do Work/Claude Code, use o comando de preparação acima como setup. Ele instala as dependências Python e confere entradas; não usa `sudo`, não muda o Google e não executa a bateria pesada. Precisa de rede apenas para obter os pacotes durante a instalação. Depois, diagnóstico, código e testes locais não dependem de sessão de navegador.

Para cálculos locais, instalar **LibreOffice Calc**, não só o launcher. Em Debian/Ubuntu, com permissão de administrador no próprio ambiente:

```bash
sudo apt-get update
sudo apt-get install -y libreoffice-calc fontconfig fonts-noto-cjk
```

Se `venv` estiver ausente, instalar o pacote `python3-venv` correspondente. Se faltar Node, disponibilizar a versão 20 pelo mecanismo do serviço. A ausência dessas dependências é informada; não é tratada como teste aprovado. Num ambiente sem administrador, o chat pode concluir código, auditoria e testes que não precisem de Calc, registrando os demais como impedidos.

## Arquivos conferidos e referências portáveis

| Grupo | Arquivos versionados |
|---|---|
| Entrada do gerador | `ficha-v01/layout.json`, catálogos `*-do-livro.json`, JSON de fórmulas, `catalogo-projeto-m.json`, `decisoes-ficha.json` |
| Regras lidas pelo código | `manual.txt`, `manual-fonte.json`, `livro.py`, decisões vigentes do plano |
| Código e arte | `ficha-v01/`, `ficha/`, `apps-script/`, `arte/`, fontes em `arte/fontes/` |
| Referências mecânicas | `nuvem-b47/fixtures/`, `ficha-v01/progressao-base3a.json.gz`, `analise-v*-preservada.json`, exemplo Kaori DOCX em `repos/` |
| Desenho aprovado e contrato | `referencias-b47/*.html`, estudos custom, planos e `ESQUEMA-ANALISE.md` |
| Consulta atualizada do livro | `referencias-b47/Ciclo-Maldito-R52.txt`, extração textual das 397 páginas do PDF do usuário |
| Estudos antigos | `referencias-b47/manual-historico/`, capítulos exigidos por quatro scripts históricos `mockup/estudo_*.py` |

O [manifesto de referências](nuvem-b47/referencias.json) registra origem, bytes e SHA-256 das fontes/referências adicionadas. O diagnóstico confere os hashes. As fontes já usadas foram copiadas sem modificar e suas licenças OFL estão em `arte/fontes/oswald/` e `arte/fontes/yujisyuku/`. `arte/gera.py` prioriza as fontes do próprio repositório, inclusive com HOME vazio.

`fixtures/original.xlsx` é a referência histórica do comparador, antes ignorada no diretório de entrada; ele a usa quando `ficha-v01/original.xlsx` não existe. As bases de campanha/custom também estão no Git. Esses XLSX são somente referência/calculadora local: **nunca importar no Google**. Referências históricas têm dados de exemplo já usados no desenvolvimento; não são backups atuais de uma ficha jogada.

A R52 textual é consulta, com separação de páginas preservada por form feed. Não substitui silenciosamente `manual.txt` R51 usado pelos parsers. A correção de Marcantes foi decidida no plano e prevalece sobre a redação antiga. Texto extraído não prova diagramação nem reproduz imagens do PDF. O PDF de 59 MB não precisa ser clonado para as tarefas de código; o manifesto registra seu hash de origem. Capítulos de `manual-historico/` servem para reproduzir estudos antigos e não são regras vigentes.

## Gerar e verificar sem Google

Leia [nuvem-b47/TESTES.md](nuvem-b47/TESTES.md) antes de escolher a regressão. Trabalho pesado deve ser serial e limitado aos recursos do ambiente.

```bash
# Pacote atual, derivado do código, e referência histórica anterior à 3c:
python nuvem-b47/exportar-baseline.py
# Regressão focal do estado atual (as expectativas precisarão mudar em A):
python regressao-pecas.py --modelo nuvem-b47/saidas/pecas-modelo.json --anterior nuvem-b47/saidas/pecas-modelo-anterior.json --estrutura
node regressao-textos-custom.js nuvem-b47/saidas/pecas-modelo.json
```

Para gerar XLSX de cálculo local e os `.gs`: `python ficha-v01/monta.py`. Isso pode atualizar arquivos versionados de saída; inspecione o diff. Para exportar apenas o contrato: `python ficha-v01/monta.py --exportar-analise nuvem-b47/saidas/analise.json`. Os comandos não escrevem no Google. O primeiro é pesado; não executar junto com outras gerações. Não reutilizar resultados antigos como se tivessem sido produzidos pelo código alterado.

Para prévia local, há `medidas/ver-aba.py`, por exemplo `python medidas/ver-aba.py --aba CONFIGURAÇÃO --saida nuvem-b47/saidas/configuracao.html --vazia`. A prévia e a calculadora local não substituem teste visual/mecânico no Sheets. O HTML pode solicitar fontes ao Google Fonts; os arquivos de fonte necessários à geração de arte já estão no repositório.

## Google sem acesso remoto

Somente o integrador realiza alterações nativas. Os links e destinos estão no plano principal. Acesso ao Git não cria conexão ao Drive, não autentica Apps Script e não concede consentimento à conta. Utilizar conector/API oficial disponível no ambiente, com autorização do usuário; a frente de infraestrutura prepara um envio reprodutível quando houver acesso compatível. Não depender do Brave, extensão ou janela do PC.

Antes de migrar: leitura atual da cópia, snapshot integral, guardas e teste em descartável. Construção integral apenas em descartável. Se o chat não tiver acesso direto aos serviços, entregar código, arquivos de envio, migração reprodutível e checklist de aplicação pendente; não declarar aplicação/validação nativa concluída. Não copiar tokens de máquina ou registrar credenciais no Git.

Os helpers antigos `medidas/preparar-*-nativa.*`, `preparar-familias7.py`, `preparar-autonomia9.py`, `conferir-pecas-revisao.py` e `preparar-revisao-grupo7.js` conservam caminhos para snapshots e IDs da sessão passada. São receitas históricas, não comandos de retomada. Não executá-los contra o Google nem copiar seus lotes sem adaptar à leitura atual. Relatórios/snapshots da sessão antiga não precisam ser incluídos para continuar; novos snapshots devem ser obtidos da planilha atual.

`medidas/daltonismo.py` é uma ferramenta opcional de análise de cores e requer NumPy, fora do conjunto necessário à geração/regressões da ficha. Não é parte do smoke.

`repo-conserto/` e `medidas/arnes-regua-da-morte.py` são ferramentas históricas de outro repositório do sistema; não integram o fluxo de geração/teste da ficha. Não é necessário clonar outro projeto para trabalhar na B47 com as referências fornecidas.

## Três chats e continuidade

Use os [prompts atualizados](PROMPT-WORK-B47.md). Todos leem `AGENTS.md` e este guia, conferem a preparação e trabalham em ramos próprios. O chat 3 continua responsável pelo envio/testes de B; não deve reconstruir este bootstrap. Chat 1 continua dono do núcleo e do Google.

A CI em `.github/workflows/nuvem.yml` executa só preparação e smoke, sem segredos ou conta Google. Disponibilidade/execução do GitHub Actions depende do repositório. Uma CI verde não substitui a bateria completa nem a auditoria nativa final.

## Evidência desta preparação

[VALIDACAO.json](nuvem-b47/VALIDACAO.json) registra instalação/checagem numa cópia só do índice Git, exportação atual, 54 verificações mecânicas, sete cenários de texto, compactação de 20 abas/fixtures e geração completa. Os 23 `.gs` regenerados coincidiram byte a byte com os versionados. Isso comprova a preparação desta base, não a redução futura ou aplicação no Google.
