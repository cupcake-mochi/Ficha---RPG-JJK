# B47 — migração Sheets na descartável · 16/10/2026

**Resultado parcial.** A planilha da descartável passou nas conferências abaixo;
o código Apps Script vinculado não foi inspecionado, atualizado ou executado.
A revisão original continua em ANALISE 9, confirmada novamente por leitura.
Esta prova **não libera a migração da revisão**: seu `resultado` é `PARCIAL`,
com `revisao_liberada: false`, em [VALIDACAO-NATIVA-PARCIAL.json](VALIDACAO-NATIVA-PARCIAL.json).
Não houve importação de Excel, execução de construir/continuar ou alteração na
oficial, bot, permissões ou main. C/D continuam fora desta entrega.

## Destinos e fonte

| Papel | ID nativo |
|---|---|
| Revisão, somente leitura nesta retomada | `1EdEXzFRL8n21dLb60lxE2wbP4PFxFUiBdw7BiTTkNg0` |
| Backup integral nativo da revisão | `1Qf5O2BbE5FZDYz2o-F7Xt0YOyb9S1s7bB82MLbabVVU` |
| Descartável copiada do backup, único destino de escrita | `1hBogVNW0vqeLYwa0PNl04Y2Nel9-7nrCoODWq1FKsb4` |

[Abrir a descartável](https://docs.google.com/spreadsheets/d/1hBogVNW0vqeLYwa0PNl04Y2Nel9-7nrCoODWq1FKsb4/edit).
Ela está nomeada **TESTE DESCARTÁVEL B47 — PLANILHA v10 — SCRIPT PENDENTE — 2026-10-16**.
Os arquivos foram copiados na pasta de origem, sem alterar compartilhamento.
As 21 abas, incluindo estudos, permanecem.

Retomada Git em `f3a3fbd8cb1893fed048f266b8df7b6f80ae262f`.
Ferramentas de migração/snapshot corrigidas em `186e84460b43fe211f39d9106965d8871c1b4622`.
Auditor e contraprovas em `6a226c3`. Os 20 `.gs` e as fórmulas de produção
continuam os de `f1ff7a6785f179df78a91a619bbd60388acd4bc1`, já reproduzidos no
fechamento local. Alvo JSON SHA-256:
`1964dc4c9a89427c5a516ec887290b59458435ad85662c193ad5f973cd5b4875`.

## Snapshot, aplicação e preservação

O snapshot contém metadados nativos com dimensões, mesclagens e grupos, além
de valores tipados e notas de todas as faixas exigidas, incluindo caudas.
91 blocos foram lidos duas vezes. A confirmação é de **16:56:08 UTC**;
o modifiedTime da descartável permaneceu igual nas duas leituras. O primeiro
envio começou às **16:57:14.972 UTC**. A janela estava dentro da guarda de 15
minutos. Snapshot normalizado SHA-256:
`9833d6649eacc24650ece486735c78e87fd4f26c2c8d02a640eecdb0a761804c`.

Os **102 lotes / 20.058 pedidos / 9.551.506 bytes** receberam resposta
confirmada, até **17:08:20.949 UTC**. Há intenção e recibo por lote, com
destino, índice, hash, quantidade e UTC. Não ocorreu falha parcial. Os
**665,977 segundos** medem essa sequência de envio/conferência pela API,
incluindo o cliente; não são latência de Apps Script ou carregamento do Sheets.

| Grade nativa depois | Linhas × colunas |
|---|---:|
| CONFIGURAÇÃO | 1.731 × 16 |
| ANALISE | 7.357 × 12; quatro colunas usadas |
| DADOS_CUSTOM | 173 × 287 |
| DADOS_PROGRESSAO | 61 × 81 |
| DADOS_CRIACAO | 20 × 15 |
| DADOS_MELHORIAS | 115 × 69 |
| DADOS_RESTRICOES | 56 × 22 |

Conferência final, após a restauração dos cenários:

- 118.493 células retornadas de 11 abas afetadas: **zero erros de fórmula**.
- 12.876 valores/fórmulas planejados ainda na grade: **zero divergências**.
- 509 entradas/notas mapeadas: **zero divergências**.
- 54.600 posições retornadas nos blocos de preservação, em seis abas:
  valores/notas conferidos, incluindo cache CB2:CC10 e entradas do personagem.
  As 69 mudanças de fórmula coincidem com o modelo: 68 consumidores de treino
  e CONFIGURAÇÃO!G160. Esta última foi ajustada automaticamente pelo Sheets,
  de H2:H328 para H2:H20, ao apagar a cauda de DADOS_CRIACAO.
- 582 células de validação de CONFIGURAÇÃO conferidas. Listas históricas
  anteriores à linha 733 permanecem iguais à leitura anterior; regras novas
  correspondem ao modelo, reconhecendo a normalização nativa de A2:A2 para A2.
- ANALISE: **7.356 chaves únicas, ordenadas**, fórmulas, fontes e partes
  correspondentes ao alvo, formato 10. O leitor reprova somente o aviso
  esperado da ficha sem escolhas suficientes de Perícia/Ofício.

## Cenários nativos e contraprovas

Quatro cenários, 13 verificações de cálculo, realizados por escrita e leitura
Sheets, sem executar gatilhos Apps Script:

- primeiras/décimas Perícias e Ofícios, atributos e pools; nomes `* ? ~`
  literais, com Rito* e Ritox distintos;
- primeira/décima Família e primeira/trigésima Melhoria/Restrição;
- herança do livro e criação de Melhoria/Restrição do zero;
- mesma Família custom na nona posição das 12 invocações, exportada 12 vezes;
- tipo incorreto colado, duplicata literal e TIPO apagado em cartão vazio.

As **48 entradas temporárias foram restauradas e relidas**, sem diferenças.
A primeira asserção ad hoc de preço da Melhoria Leve em Família Livre esperava
2 incorretamente. A fórmula existente é `Q + 3 × Livre`: `1 + 3 × 1 = 4`.
A leitura nativa já retornava 4. Corrigido apenas o oráculo, sem alterar
produção nem refazer dados para obter aprovação; o resultado inicial foi
preservado localmente em `cenarios-verificacao-primeira.json`.

O auditor consolidado passou **22 checagens**, incluindo as 13 acima.
Nove contraprovas offline sobre as leituras reais confirmaram recusa de
alterações de entrada, nota mapeada, fórmula, chave, fonte, menu e erro de
fórmula; a prova permanece parcial mesmo quando tudo isso passa. Uma
contraprova encontrou acesso direto à chave de versão ausente no auditor;
ele agora registra falha, sem interromper a geração do relatório por KeyError.

## Ajustes de B e revisão recebida

Google remove aspas opcionais de nomes ASCII de abas. A guarda inicialmente
recusou CONFIGURAÇÃO!B773; `canonical()` agora reconhece essa representação,
preservando textos literais, aspas escapadas, tipos e diferenças de condições.
Seis testes focais dessa normalização e nove testes do normalizador de
snapshot passaram; os 19 testes de migração foram repetidos e passaram.

A geração de lotes deixava 95.967 limpezas redundantes em linhas removidas
ao final. Elas foram suprimidas somente na cauda das seis abas compactadas,
depois de provar que o plano bloqueia conteúdo não preservado ali. Comparação
offline sobre o snapshot nativo: **estado final equivalente**, ações de
estrutura/estilo/menu/notas/restauração idênticas. Uma contraprova unitária
também rejeita a retirada de uma alteração em linha retida.

| Pacote local de pedidos REST | Antes | Depois |
|---|---:|---:|
| Pedidos | 116.025 | 20.058 |
| Lotes | 260 | 102 |
| Bytes dos payloads | 24.226.270 | 9.551.506 |

São medidas do pacote, sem ensaio nativo comparativo do pacote antigo.
Não houve mudança nos 20 `.gs`, regras ou desenhos nessa otimização.

Novo commit de revisão `efd8dd8459f4aa42c85bd0ac71c01323149ceaee`, encontrado
por `ls-remote`, examinado e integrado em **3323803**. O revisor auditou o
núcleo em 8276ca6; isso não audita automaticamente os helpers novos de 186e844
ou 6a226c3. O merge trouxe somente relatório e ajustes do teste de envio;
as demais adaptações já coincidiam com a árvore do integrador.
Teste da combinação: `test_infra_envio.py --perfil b47-v10 --ref HEAD
--com-patch-infra`, **10/10**, offline, com construção simulada. Smoke final
também passou. Não repetimos a bateria inteira de 23/26 etapas nem os
cenários mecânicos históricos completos após alterações apenas nas ferramentas.

## Acesso separado ao Apps Script e próximo passo

Drive/Sheets funcionaram pelo conector. Não foi encontrada ferramenta de
leitura/salvamento/execução Apps Script, navegador controlável ou sessão
Sheets no Document Control. O ambiente de execução consultado informa rede
restrita a hosts de pacotes e ausência de secrets/runtime variables/outbound
identities para Apps Script. Não se tentou contornar a política ou reaproveitar
credenciais do PC. A conta estar conectada ao Drive não comprova esse outro acesso.

Ainda faltam: localizar o **projeto vinculado à nova descartável**, salvar e
reler os 20 `.gs` e remover explicitamente os três fragmentos obsoletos;
testar menus pela interface, gatilhos, textos longos/alturas/limpeza, 23/11
escolhas do personagem, cópia funcional e medidas nativas. Medir construção
somente na descartável própria documentada. Depois gerar prova conjunta do
mesmo modelo/código, renovar backup/snapshot e só então migrar a revisão.
**O ID de projeto da revisão não é o ID do projeto da descartável.**

Os snapshots, entradas e respostas completas ficam somente no diretório
ignorado `nuvem-b47/saidas/nativo-v10-20261016/`. O Git recebe contagens,
coordenadas de testes sintéticos, hashes e IDs dos artefatos, sem conteúdo
pessoal ou credenciais. Para conferir as leituras locais já coletadas:

```bash
.venv/bin/python capacidade-b47/conferir-nativo.py \
  --leituras nuvem-b47/saidas/nativo-v10-20261016 \
  --modelo nuvem-b47/saidas/focal/pecas-modelo.json \
  --saida nuvem-b47/saidas/conferencia-nativa.json
.venv/bin/python capacidade-b47/testar-conferencia-nativa.py \
  --leituras nuvem-b47/saidas/nativo-v10-20261016 \
  --modelo nuvem-b47/saidas/focal/pecas-modelo.json
```

Sem esses artefatos privados, os comandos ficam impedidos; não recriam
leituras nem comprovam um estado futuro da planilha. O JSON público agrega
também os recibos e resultados dos testes executados nesta retomada.

Próxima ação/modelo: **GPT-6.1 Sol, High**, para conferir o código vinculado e
os testes nativos restantes antes de migrar a revisão com entradas preservadas.
