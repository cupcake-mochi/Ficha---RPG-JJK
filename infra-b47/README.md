# Infraestrutura delimitada B47

Ferramentas locais para o integrador, sem rede, login ou envio embutido. Base:
`4187df37640b5e0966cdb342f56f9ee0a0daf16a`, ramo `codex/b47-infra`.
Reutilizam o bootstrap de `nuvem-b47/`. Não geram `.gs`, não alteram núcleo,
contrato ou roteiro central. C/D continuam na fila.

## Execução focal

A partir da raiz do checkout:

```bash
bash nuvem-b47/preparar.sh
source .venv/bin/activate
python infra-b47/executar.py --listar
python infra-b47/executar.py smoke
free -m
cat /sys/fs/cgroup/memory.max
python infra-b47/executar.py pecas-estrutura textos --permitir-pesados
python -m unittest discover -s infra-b47 -p 'test_*.py' -v
```

Sem seleção explícita, o executor apenas mostra erro de uso. `--listar` não
executa testes. O inventário executável informa comando, entradas, ferramentas,
escopo e limitações de cada seleção. [INVENTARIO.md](INVENTARIO.md) cobre também
os testes históricos fora desta seleção focal.

O executor roda em série, impede dois executores focais simultâneos no mesmo
checkout e exige `--permitir-pesados` para geração/cálculo/construção simulada.
Esse sinal exige conferência prévia de recursos; não impõe limite de RAM nem
impede gerações lançadas fora dele. Não executar junto de outros trabalhos
pesados. `NODE_OPTIONS` recebe teto de 1.500 MB se ainda não definido.

Peças/textos compartilham uma exportação em `infra-b47/saidas/baseline/`, feita
pelo exportador existente com `--destino`. O recibo guarda hashes das duas saídas
e uma impressão do conteúdo real dos arquivos rastreados fora das pastas de
infra/revisão, Python e dependências instaladas; inclui fontes Python novas em
`ficha-v01/`. Mudança na fonte, dependências ou saída invalida o recibo. Mudanças
apenas de documentação podem invalidá-lo conservadoramente. Um recibo válido
permite repetir estrutura/textos sem `--permitir-pesados` e sem gerar de novo.
O estado `reutilizado` não é execução nova. Para forçar geração, remover apenas
`infra-b47/saidas/baseline/recibo.json`. Arquivos externos não rastreados, salvo os
Python citados, não compõem a impressão; manter as entradas do núcleo no Git.
Recibos com JSON de estrutura inválida ou nomes de saída inesperados invalidam
o cache e não interrompem o executor.

Cada execução cria pasta única ignorada, logs e `relatorio.json`, com SHA,
estado inicial do Git, comandos, tempo, exit codes reais e motivos. Estados:
`executado` (exit 0), `falhou` (exit diferente de 0 ou timeout), `impedido`
(entrada/ferramenta/autorização de trabalho pesado ausente), `reutilizado`.
Exit do executor: 0 sem falhas/impedimentos; 1 havendo falha; 2 havendo apenas
impedimentos ou erro de uso. Timeout padrão 900 s por tarefa, ajustável com
`--timeout`; encerra o grupo de processos e registra a falha. PATH da `.venv`
também é passado aos subprocessos antigos que chamam `python3`.

Não converter as expectativas históricas em verde automaticamente. O executor
registra o exit do teste; não interpreta avisos como validação mecânica adicional.
`leitor` e `comparador` exigem workbook atual, que **não é gerado aqui**. Seu
frescor é responsabilidade do integrador. `original.xlsx` está disponível como
fixture histórica; sua ausência no caminho antigo não impede o comparador se a
fixture existir. Nunca importar XLSX no Google. Simulação não é teste nativo.

Integração proposta com o roteiro central: após A, o integrador pode inserir
`python infra-b47/executar.py pecas-estrutura textos --permitir-pesados` na etapa
focal pertinente. Não substituir a bateria final por esse comando. Nenhum patch
do roteiro ou otimização do núcleo foi aplicado nesta frente.

## Manifesto dos `.gs`

```bash
python infra-b47/apps_script.py manifesto --saida infra-b47/saidas/manifesto.json
```

Lista nomes de arquivo/API, bytes UTF-8 e SHA-256, além do total. Rejeita conjunto
vazio, symlinks e arquivos com **900.000 bytes ou mais**, seguindo a guarda
estrita do bootstrap. `MANIFESTO-BASE.json` é a conferência desta base, não da
redução futura. Regenerar o manifesto após A; só o integrador regenera os `.gs`.
Os comandos rejeitam uma saída que coincida com snapshot, pacote ou `.gs` de
entrada, inclusive por link simbólico/hard link. Isso preserva os arquivos
necessários à comparação e à reversão. O erro retorna exit 2 sem gravar a saída.

## Envio oficial: procedimento exclusivo do integrador

Escolha: API REST oficial Apps Script, `projects.getContent` e
`projects.updateContent`. Não exige montar plataforma de deploy nem depender do
editor de navegador. A especificação oficial confirma que PUT substitui **todos**
os arquivos, salva em **HEAD** e exige `appsscript` do tipo `JSON`. A ferramenta
vincula o pacote ao `scriptId` explícito, preserva manifesto e HTML da leitura atual, substitui os `.gs` locais e bloqueia
`.gs` remotos sem correspondente local. O integrador deve investigar helpers ou
arquivos extras antes de qualquer remoção, sem simplesmente descartar a guarda.

Pré-requisitos reais: conta humana com edição no projeto, OAuth de usuário com
`https://www.googleapis.com/auth/script.projects`, API Apps Script habilitada no
projeto Cloud do cliente OAuth e permissão de acesso à API nas configurações do
Apps Script da conta. Pode haver consentimento, política de organização e
restrições do cliente OAuth. GET também aceita `script.projects.readonly`, mas
esse escopo não autoriza PUT. Apps Script API não oferece suporte a service
accounts. Acesso ao Git ou conector de Sheets não fornece esse OAuth.

Nesta sessão não há identidade/segredo Google configurado nem ferramenta direta
de Apps Script. Não foi feito login, sondagem de projeto ou chamada à API. O
snapshot de política de rede não lista `script.googleapis.com` nem hosts OAuth;
o estado observado da política é `unknown`. O integrador precisa confirmar
acesso compatível no próprio ambiente, sem contornar a política. Não transportar
tokens do PC nem iniciar autenticação para esta frente local.

Os comandos abaixo são uma receita **a ser executada só pelo integrador**, após
revisar commits, destino e diff; não são executados pelo Python. `SCRIPT_ID`
deve ser o ID **do projeto Apps Script**, nunca o ID da planilha ou deployment.
Destino de revisão documentado no plano:
`1wdZc903PPK6EoGxFG4KcuPNx_plElCBsWxa4lEBgLUlFBD4OrbZPHYnf`.
Confirmar vínculo e conta por leitura atual. Primeiro testar em projeto
descartável com ID próprio confirmado; não presumir que o script da revisão
seja vinculado à planilha descartável. Não usar a ficha oficial.

`APPS_SCRIPT_CURL_CONFIG` aponta para um arquivo privado **fora do checkout**,
provisionado pelo fluxo OAuth autorizado do integrador. Deve fornecer somente
o header `Authorization: Bearer ...`, sem URL, método ou dados. Permissão 0600;
não imprimir, versionar ou usar `set -x`. Não há segredo no pacote local.

```bash
# Executar no checkout; preencher ID e config somente no ambiente autorizado.
set -euo pipefail
: "${SCRIPT_ID:?Defina explicitamente o projeto Apps Script revisado}"
: "${APPS_SCRIPT_CURL_CONFIG:?Config OAuth privada fora do Git}"
mkdir -p infra-b47/saidas/google
curl --fail-with-body --silent --show-error --config "$APPS_SCRIPT_CURL_CONFIG" \
  "https://script.googleapis.com/v1/projects/${SCRIPT_ID}/content" \
  --output infra-b47/saidas/google/antes.json
python infra-b47/apps_script.py preparar --script-id "$SCRIPT_ID" \
  --snapshot infra-b47/saidas/google/antes.json \
  --saida infra-b47/saidas/google/pacote.json

# Revisar pacote/diff e snapshot integral antes de continuar.
# Nova leitura imediatamente antes do PUT: detectar edições concorrentes.
curl --fail-with-body --silent --show-error --config "$APPS_SCRIPT_CURL_CONFIG" \
  "https://script.googleapis.com/v1/projects/${SCRIPT_ID}/content" \
  --output infra-b47/saidas/google/preflight.json
python infra-b47/apps_script.py conferir --script-id "$SCRIPT_ID" \
  --pacote infra-b47/saidas/google/antes.json \
  --snapshot infra-b47/saidas/google/preflight.json \
  --saida infra-b47/saidas/google/guarda.json

# ESCRITA EXPLÍCITA: somente após revisão do integrador; não é dry-run.
curl --fail-with-body --silent --show-error --config "$APPS_SCRIPT_CURL_CONFIG" \
  --request PUT --header 'Content-Type: application/json' \
  --data-binary @infra-b47/saidas/google/pacote.json \
  "https://script.googleapis.com/v1/projects/${SCRIPT_ID}/content" \
  --output infra-b47/saidas/google/resposta-put.json

# Nova requisição GET independente, HEAD, sem versionNumber.
curl --fail-with-body --silent --show-error --config "$APPS_SCRIPT_CURL_CONFIG" \
  "https://script.googleapis.com/v1/projects/${SCRIPT_ID}/content" \
  --output infra-b47/saidas/google/depois.json
python infra-b47/apps_script.py conferir --script-id "$SCRIPT_ID" \
  --pacote infra-b47/saidas/google/pacote.json \
  --snapshot infra-b47/saidas/google/depois.json \
  --saida infra-b47/saidas/google/conferencia.json
```

Separar os blocos na operação real: primeiro leitura/preparação/revisão, depois
guarda/escrita/releitura. A API não expõe precondição de revisão em updateContent;
há janela entre GET e PUT. Combinar exclusividade de edição com o integrador,
não prometer controle transacional. HTTP 2xx do PUT sozinho não comprova a
releitura: exigir conjunto de nomes/tipos, bytes e hashes iguais. Ordem dos
arquivos e metadados de função/horário não participam da comparação; conteúdo,
acentos e quebras de linha participam integralmente. Normalização remota de
texto será divergência a investigar, não aprovação automática.

HEAD persistido não cria versão imutável nem atualiza deployments versionados.
O código salvo pode afetar gatilhos existentes; não executar funções como parte
do upload. A ferramenta não cria gatilhos, não chama `construir()`/`continuar()`
e não valida visual/mecânica no Sheets. Antes de migração de planilha: snapshot
integral atual de entradas, guardas e validação em descartável pelo integrador.
O backup de código não substitui esse snapshot.

Falha HTTP/OAuth ou timeout: interromper e registrar código/mensagem sem token.
Em timeout de PUT, fazer GET para diagnosticar o estado antes de tentar de novo.
Sem repetição automática. Reversão de código: revisar o snapshot `antes.json`,
nova leitura/guarda do estado atual e restaurar seu conjunto integral `files`
por updateContent, seguido de GET/conferência; não restaurar sobre edições
posteriores desconhecidas. Reversão não desfaz efeitos já executados por gatilhos
ou migrações da planilha. Snapshots e logs locais permanecem ignorados e sob
controle do integrador; não versionar dados da conta.

Referências oficiais:

- [getContent](https://developers.google.com/apps-script/api/reference/rest/v1/projects/getContent)
- [updateContent](https://developers.google.com/apps-script/api/reference/rest/v1/projects/updateContent)
- [Habilitar e usar a API](https://developers.google.com/apps-script/api/how-tos/enable)
- [Autenticação](https://developers.google.com/apps-script/api/concepts/auth)
- [Discovery oficial consultado](https://github.com/googleapis/google-api-python-client/blob/main/googleapiclient/discovery_cache/documents/script.v1.json)

## Aplicação e reversão dos commits

O integrador revisa os SHAs do relatório, aplica por cherry-pick em
`codex/configuracao-b47` e executa os testes próprios/focais na combinação após
A. Para reverter a integração, usar `git revert` dos commits desta frente em
ordem inversa; nenhuma alteração Google é revertida por Git. Não houve merge em
ramo compartilhado. Recomenda-se GPT-6.1 Sol, Medium para revisar e integrar esta
infraestrutura; subir para High apenas diante de conflito concreto de contrato
ou migração.
