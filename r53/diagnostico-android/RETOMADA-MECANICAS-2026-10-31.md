# Retomada da revisão mecânica · 31/10/2026

O usuário pediu salvar tudo no Git para dormir e continuar depois pelo Codex.
Este registro encerra a sessão; não é autorização para aplicar a PR45 nas
oficiais. Não continuar instalações ou ensaios nesta sessão.

## Abrir a versão certa

- Repositório: https://github.com/cupcake-mochi/Ficha---RPG-JJK
- Ramo: `codex/revisao-mecanicas-20261030`.
- PR aberta: https://github.com/cupcake-mochi/Ficha---RPG-JJK/pull/45
- Commit da implementação: `c4f69015194d81bce9f60a54c44971567363d882`.
- Base main conferida: `5ea10b482f638dc767a3aa07af21796007c90487`.
- CI da implementação passou: execução `41164312219` (evento da PR).

Leia `AGENTS.md`, este arquivo, `REVISAO-MECANICAS-2026-10-31.md` e seu JSON.
Confirme o Git remoto antes de editar: há trabalho paralelo na PR31. Ela teve
atualizações externas durante esta sessão; não usar os hashes históricos do
AGENTS como indicação de que a PR31 permaneceu parada. Nenhuma alteração desta
entrega foi enviada para seu ramo. Não mesclar, editar ou rebasear a PR31.

## O que está concluído

O diagnóstico de cura/PV temporários salvos com a função bloqueada ganhou uma
correção no gerador: a intenção vem da versão da Classe ativa e da entrada,
pois os flags efetivos já ficaram falsos pela porta de permissão. Só 244
fórmulas GA mudaram no modelo; outras células, metadados, R53 e ANALISE iguais.

Fontes GS regeneradas, geração `8c38acf72c7e6a33`; pacote conferido. Código e
relatórios estão no Git. Não instalar esse pacote integral em uma oficial ou
ficha preenchida. O pacote regenerado não equivale ao atualmente instalado.

Validação registrada: 276 cenários/2.080 verificações nativas aprovadas; 1.035
rechecagens após o delta; 52 testes Python, 89 casos do motor, 584 verificações
do editor e smoke aprovados. Não confundir esses números com aprovação do
fluxo de recuperação de Amparo, que falhou.

A migração offline `r53/diagnosticos_funcoes.py` exige snapshot atual A:M e GA,
confere ID, layout/entradas e fórmula anterior e gera reversão. Ensaiadas
reversão/reaplicação de três amostras e repetição zero, com 249 atualizadas.
O antigo catálogo de QA saiu de 53018005 (agora R53_EVENTOS) para 53018901.
Não aplicar pedidos antigos de QA sem conferir metadados e criar as abas certas.

O teste antigo de Morrendo não estava errado: usa frações/teto custom de
`regressao-campanha.py`. Seus valores foram mantidos. Os ensaios novos verificam
separadamente a regra padrão do livro.

## Pendência prioritária: recuperação de Amparo

Na cópia da Era, com 36 cartões pessoais preenchidos, a recuperação de campos
`—` ao reabrir Amparo não terminou. Duas execuções reais de `onEdit`, visíveis
no histórico do Apps Script copiado, atingiram 30,561 e 30,454 segundos.
Os valores continuavam guardados na MONTAGENS. O delta de GA não resolve isso.

**Contexto exato para não transformar uma hipótese em certeza:** as matrizes e
os testes de Família foram preparados pela API. Também houve uma reabertura
pela API antes das tentativas nativas de recuperação; essa escrita não dispara
onEdit. As duas tentativas nativas seguintes regravaram `Neutra` em P37, com
campos ainda mascarados, e atingiram o limite. Houve fechamento nativo anterior
concluído. Ainda falta repetir o ciclo inteiro fechar/reabrir somente pela UI
numa cópia nova, sem mudanças de Família pela API entre essas duas ações.
Isso distingue uma falha geral do uso normal de uma falha de recuperação de
estado após alterações externas. Ambas as execuções com timeout são reais.

Locais para investigar, sem editar às cegas:

- `r53/runtime_direto.gs`, `r53SincronizarFamilias_`, `r53Porta_`, `r53Ativa_`.
- `r53/editor_lazy.js`, transporte do editor e cache do controlador.
- `r53/empacotar_script.py`, encadeamento de onEdit entre editor e módulo.
- O sincronizador lê matrizes, pode reler Classe por célula ao recuperar cada
  função, agrupa escritas e só atualiza a propriedade ao final. Esses pontos
  merecem medição; não foi provado qual custo domina nem se o tempo esgota
  dentro do sincronizador ou na continuação do evento.

Não tratar a otimização de r53AtivaNaFoto_ já existente na fonte como se ela
estivesse instalada em todos os caminhos do runtime otimizado da oficial.
Não apagar versões ou trocar `—` por zero para esconder a falha. Preservar
Classe, pontos, caixas de modalidade fixa e escolhas salvas ao fechar/reabrir.

## Retomar sem as evidências privadas

Os recibos, módulos salvos e capturas estão apenas no computador desta sessão,
em `nuvem-b47/saidas/revisao-mecanicas-20261030/` e, para a base instalada,
`nuvem-b47/saidas/origens-oficiais-20261030/`. São ignorados; não subir snapshots,
credenciais ou dados pessoais no Git. O relatório público é autossuficiente
quanto aos resultados e limites, mas não substitui esses recibos brutos.

As duas cópias desta revisão foram movidas à lixeira recuperável. Não reutilizar
seus IDs nem presumir que abas/conexões do navegador anterior ainda existem.
Criar cópias nativas novas das oficiais identificadas em `r53/OFICIAIS.md`.
A ficha do jogador não faz parte dos alvos de teste.

Para recriar geometria e plano de 36 cartões sem o modelo privado:

```sh
python3 ficha-v01/monta.py --exportar-r53 /caminho/privado/modelo-qa.json
python3 r53/testes/revisao_mecanicas.py --modelo /caminho/privado/modelo-qa.json --limites --saida /caminho/privado/plano-limites.json
```

O primeiro comando exporta o modelo sem montar arquivo Office; ainda exige
conferir memória antes da geração. O segundo só prepara pedidos offline.
Conferir os sheetIds/títulos do alvo descartável antes de qualquer escrita.
Para ensaio nativo das automações, usar edições reais pela UI e observar as
execuções: preenchimento pela API não valida onEdit. Inicializar/conferir o
estado de uma cópia nova antes de atribuir resultados a uma transição.

O modelo dessa exportação já contém o diagnóstico novo. Para migrar uma base
antiga, o `--modelo-base` da ferramenta de diagnóstico precisa corresponder à
base antiga, não à proposta nova. Se o modelo antigo privado estiver ausente,
gerá-lo em checkout isolado da base correta, sem mudar o ramo de trabalho da
PR31 ou reconstruir a planilha. Não dispensar guardas para contornar divergência.

## Instalação futura e limites

Oficiais: Era `1MQqhHbIzzyoMQY5zLKOciiT5k9Y6AMI4MCSrPhu8V_k` e Ciclo
`1pgLDZOYpUJrqTcwomaQl8Bjn-AuAcu_Aowd30G7YiJw`; projetos em `r53/OFICIAIS.md`.
Nenhuma recebeu esta correção. Os hashes arquivados na última conferência eram
Codigo `52302778…`, EditorR53 `c3d31096…`, módulo `9dc3480a…`; são referência
histórica, não substituem releitura do código atual antes de preparar incremento.

Antes de promoção: corrigir/ensaiar a recuperação, conferir a PR45 e eventuais
mudanças remotas, obter autorização para o incremento concreto e os alvos,
fazer backups nativos atualizados, aplicar somente o delta necessário e reler.
Preservar todos os incrementos já instalados, inclusive salários/cores. Nunca
`construir()`/`continuar()` em oficial ou ficha preenchida. Não tocar no jogador,
PR31, contratos ANALISE12/esquema2, 249 contextos, 12 entidades ou nove Famílias.
Sem novos agentes, acionadores, acessos, Office ou experimentos de paleta.

Recomendação do AGENTS: Sol/High para implementação e ensaio integrado;
Medium para revisão focal. Não alterar configurações automaticamente.
