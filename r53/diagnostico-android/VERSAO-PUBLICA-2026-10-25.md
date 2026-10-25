# Versão pública 1.0 · 25/10/2026

O usuário autorizou integrar o ramo Android na `main` e pediu que a ficha deixasse de exibir a revisão do livro. As duas oficiais de [OFICIAIS.md](../OFICIAIS.md) agora mostram `Ciclo Maldito · v1.0` em `FICHA!H4` e usam `1.0` em `CARTEIRA!AH2`, conservando o sufixo derivado do nome.

O aviso “em dia / a atual é...” saiu desse cabeçalho. A revisão técnica do catálogo continua em DADOS e ANALISE, com os mesmos endereços, valores e contrato. Esta mudança de apresentação não afirma incorporação das regras de uma edição posterior do livro.

## Aplicação

- Snapshots nativos novos precederam a alteração. Códigos anteriores e evidências completas ficam em `nuvem-b47/saidas/versao-publica-20261025/`, ignorada pelo Git.
- Em cada oficial, somente duas fórmulas foram atualizadas, junto com o helper de restauração no `Codigo.gs`. Os dois códigos salvos foram recarregados e relidos integralmente iguais à proposta.
- SHA-256 do `Codigo.gs` instalado: `f664e70a66063fba8fe966506d3e9446ba68e2ed0e0a4b45cc09e49ce7a2d66f`. O `EditorR53.gs` do pente-fino permanece igual.
- A restauração desses dois rótulos agora ocorre diretamente, sem carregar os catálogos pesados. O caminho antigo excedeu 30 s no ensaio do cabeçalho; o reparo direto concluiu e a releitura confirmou a fórmula em 1.0. A carteira também foi sobrescrita na cópia e voltou à fórmula correta. Nenhuma sobrescrita de teste foi feita nas oficiais.
- Fórmulas e valores finais relidos nas duas oficiais. Os blocos de metadados de DADOS e ANALISE foram comparados antes/depois e permaneceram iguais.
- Sem reconstrução, importação Office, acionadores ou ampliação de acesso. O pacote integral novo não foi instalado.

## Fontes e conferência

`ficha-v01/versao_publica.py` centraliza `1.0` para as próximas gerações. Cabeçalho, gerador da carteira e as duas fórmulas correspondentes em `apps-script/Ficha.gs` foram ajustados. Comparação integral desse arquivo confirmou somente essas duas substituições. A geração-base continua `7f85d740f71c4cb6`, acrescida desse delta de apresentação.

Preparador incremental e helper versionados; recusam bases/moldes divergentes e reaplicação. A validação de todos os moldes precede qualquer mutação. Os testes cobrem idempotência, recusa atômica, reparo dos dois campos mesclados e preservação do caminho original para colagens que abrangem outras células.

O teste do pacote passou com nove arquivos, 25 abas e 249 contextos. A regressão de missões passou em 2.709 verificações. Os testes de missões e versão pública foram incluídos no smoke da integração contínua. A bateria nativa extensa do [pente-fino](PENTE-FINO-FINAL-2026-10-25.md) já estava aprovada; não foi repetida integralmente por uma alteração de rótulos.
