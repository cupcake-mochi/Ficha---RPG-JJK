# Entrega da infraestrutura B47

Base recebida: `4187df37640b5e0966cdb342f56f9ee0a0daf16a`, confirmada no
ramo remoto atualizado `codex/b47-infra`; árvore inicial limpa. Implementação
testada: `1f5d62aec4b6c436937de40e67def55e7692485e`. Este relatório e
`VALIDACAO.json` são uma adição documental posterior à validação desse SHA.
Todas as alterações versionadas desta frente estão em `infra-b47/`.

Entregues executor serial com inventário, seleção explícita, recibo de baseline,
logs/exit codes/impedimentos e timeout; manifesto dos `.gs`; preparação offline
de pacote oficial vinculado ao destino; comparação integral de snapshots; onze
testes com fixtures; procedimento de envio/releitura/reversão para o integrador.
Nenhuma otimização ou alteração do núcleo, contrato, `.gs` ou roteiro central.

## Evidência executada

| Comando | Resultado |
|---|---|
| `bash nuvem-b47/preparar.sh` | exit 0; bootstrap existente, sem duplicação |
| `.venv/bin/python nuvem-b47/conferir.py --smoke` | exit 0; diagnóstico/smoke inicial |
| `.venv/bin/python -m unittest discover -s infra-b47 -p 'test_*.py' -v` | exit 0; 11 testes próprios |
| `.venv/bin/python infra-b47/executar.py pecas-estrutura textos --permitir-pesados` | exit 0; exportação única em 17,787 s, estrutura e sete cenários de texto |
| `.venv/bin/python infra-b47/executar.py pecas-estrutura textos` | exit 0; baseline reutilizada por recibo/hashes; sem nova geração |
| `.venv/bin/python infra-b47/executar.py smoke pecas-estrutura textos` | exit 0 no SHA `1f5d62a`, árvore limpa; baseline reutilizada, smoke e dois testes executados |
| `.venv/bin/python infra-b47/apps_script.py manifesto --saida infra-b47/MANIFESTO-BASE.json` | exit 0; 23 arquivos, 9.543.357 bytes, máximo 843.661 bytes em Configuracao.gs |
| `git diff --cached --check` | exit 0 antes do commit de implementação |

O cenário anterior sem autorização de trabalho pesado retornou exit 2 e
registrou baseline/estrutura/textos impedidos, sem convertê-los em aprovação.
Leitor/comparador também foram selecionados nessa verificação de guardas e
ficaram impedidos; não alegar que passaram. Onze fixtures próprias cobrem
preservação do manifesto/HTML, destinos errados (snapshot e pacote), scripts
remotos extras, nomes duplicados, conjunto vazio/symlink, limite UTF-8, conjunto
e conteúdo relido, alteração/obsolescência do cache, exit não zero e timeout.
Os estados de falha usados em fixtures são resultados esperados dos testes.

[VALIDACAO.json](VALIDACAO.json) registra comandos, SHA, tempos, hashes de logs,
impressão/recibo da baseline e limitações. Logs/modelos ficam ignorados em
`infra-b47/saidas/`; diagnóstico do bootstrap em `nuvem-b47/saidas/`. Não foram
versionados modelos grandes, credenciais ou snapshots de conta. Os comandos
do [README](README.md) reproduzem a validação local.

## Limites e integração

Não houve chamada, envio, leitura de projeto ou escrita no Google. O caminho
funcional preparado é a API oficial `getContent` → `updateContent` → novo
`getContent`, com comparação de nomes, tipos, bytes e SHA-256. A especificação
Discovery oficial foi consultada: PUT substitui todos os arquivos e persiste em
HEAD; não publica deployments versionados. O pacote conserva manifesto/HTML e
bloqueia `.gs` remotos desconhecidos. Há janela de concorrência entre guarda e
PUT, descrita no procedimento. Fixtures não provam autenticação/salvamento real.

O ambiente tem `soffice` dev, mas não `libreoffice`; testes que exigem esse nome
ficam impedidos. Não foi feito recálculo nesta frente. A fixture histórica
`original.xlsx` está no Git e passou pelo diagnóstico de hashes: não há esse
impedimento nesta base. Não houve geração integral, comparador, construção
simulada/nativa ou bateria final. Testes focais desta base não validam A futura.

O integrador revisará o diff e aplicará o commit de implementação e os commits
documentais por cherry-pick em `codex/configuracao-b47`. Após A, deve conferir
expectativas/endereço dos testes, regenerar `.gs`/manifesto e validar a
combinação. A receita de envio requer conta com edição, OAuth/consentimento,
API habilitada, acesso à rede e ID explícito confirmado. Primeiro testar em
projeto descartável; migração da planilha exige snapshot atual e guardas.
Não executar `construir()`/`continuar()` na revisão preenchida ou oficial.
Não importar Excel no Google. Oficial, bot e acessos não foram alterados.

Aplicação/reversão detalhadas no [README](README.md). Git: reverter os commits
em ordem inversa; não desfaz operações nativas futuras. Google: restauração
integral do snapshot de código, com nova guarda e releitura pelo integrador;
não desfaz migração ou efeitos de gatilhos já executados. C/D seguem na fila.

## Publicação: bloqueio inicial resolvido

O push normal para `codex/b47-infra` foi tentado após conferir a base remota,
mas o GitHub retornou **HTTP 403, permissão de escrita negada à identidade
disponível no ambiente**. Naquela tentativa nenhum commit foi publicado. Não
foram alteradas credenciais ou permissões pelo agente nem tentado outro destino.

Após o usuário ajustar o acesso e solicitar nova tentativa, o push foi concluído:
`4187df3..cb8b80b` em `codex/b47-infra`. Os commits de implementação e evidências
estão publicados; este registro posterior documenta a resolução do bloqueio.

A entrega alternativa preparada durante o bloqueio inclui um bundle ignorado em
`infra-b47/saidas/b47-infra.bundle`, criado após este registro, com a sequência
desde `4187df3`. Em um clone que já tenha essa base, o integrador pode executar:

```bash
git bundle verify /caminho/b47-infra.bundle
git fetch /caminho/b47-infra.bundle codex/b47-infra:refs/remotes/entrega/b47-infra
git log --oneline 4187df3..refs/remotes/entrega/b47-infra
git diff 4187df3..refs/remotes/entrega/b47-infra -- infra-b47/
# Após revisar e estando no ramo de integração:
git cherry-pick 4187df3..refs/remotes/entrega/b47-infra
```

O bundle contém só os commits desta frente e exige a base indicada; não inclui
venv, saídas temporárias ou credenciais. O bundle representa a entrega até `cb8b80b`; o ramo remoto inclui também o
registro posterior da publicação bem-sucedida.

Próxima ação recomendada: revisão e integração desta infraestrutura após A com
**GPT-6.1 Sol, Medium**, pois as ferramentas são delimitadas e têm fixtures.
Subir para High apenas se houver conflito concreto de contrato ou migração.
