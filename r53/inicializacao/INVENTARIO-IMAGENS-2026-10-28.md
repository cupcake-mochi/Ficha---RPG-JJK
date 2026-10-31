# Inventário de imagens

28/10/2026 · PR 31, protótipo fora do pacote. Criação continua bloqueada.
Main produtor ef361cc e bot de42447 reconferidas sem novidade.

## Leitura por páginas

`inventario_imagens.gs` percorre a grade física de todas as abas, inclusive
ocultas. Não usa a última linha preenchida para cortar a leitura. Limites:
50 abas, três milhões de células e 4.096 páginas; exceder qualquer limite
recusa a operação, sem truncar a grade. Até quatro páginas por chamada, com
até 4.096 células cada e orçamento de três minutos entre páginas.

As rodadas fixas `antes` e `depois` têm contexto confiável, assinatura de grade,
IDs, dimensões e quantidades de objetos; diário pequeno, integridade e quota
compartilhada. Cada página só avança após persistir o resultado. Queda antes
ou depois da gravação não pula nem soma a página duas vezes. Não apagar diário
para reiniciar na mesma cópia. Rodada concluída retorna seu resultado histórico.

Classifica fotos conhecidas, decorações com marcador conhecido, decorações
ausentes, imagens em outras células, objetos indeterminados e fórmulas IMAGE,
inclusive dentro de outras funções. Texto literal e nome de aba entre aspas
não contam como chamada IMAGE. Imagens sobrepostas e desenhos são apenas
contados, sem remoção, leitura de URL ou tentativa de identificá-los pelo título.
A recusa desses objetos na limpeza de fotos continua igual.

Não escreve células nem imagens. Só o progresso vai a DocumentProperties.
Guarda contagens, hashes de classificação e até oito endereços numéricos de
problemas; não persiste nomes de abas, conteúdo, fórmula, URL ou alt text.
O maior checkpoint dos testes foi 1.109 bytes: duas rodadas acrescentam no
máximo 2.218 bytes nesse ensaio, além do orçamento anterior. Não é medição de
quota total nativa nem garantia para qualquer conjunto de propriedades.

## O que esta leitura não certifica

Não há snapshot consistente entre páginas. Uma imagem inserida depois de uma
página ser lida pode escapar daquela rodada; a regressão demonstra isso e uma
segunda rodada nova a encontra. Mudanças de estrutura/contagem de objetos
recusam a retomada, mas não detectam toda edição de conteúdo concorrente.

`PM-ARTE:` é só marcador, não prova de pixels/origem. A contagem é chamada
`decoracoesMarcadas`; nunca autoriza apagar ou aprovar uma decoração. Retornos
mantêm `consistenciaTemporalVerificada`, `autenticidadeDecoracaoVerificada` e
`criacaoDisponivel` falsos. Ainda falta resolver a conferência conjunta antes
de integrar qualquer selo de criação.

## Testes offline

79 cenários novos passaram: grade inteira/oculta/última célula, limites,
retomada e falhas antes/depois de cada checkpoint, páginas incompletas,
privacidade, amostra limitada sem truncar contagens, contexto, quota,
integridade, antes/depois, fórmulas, objetos, tempo e edição concorrente.
A correção feita no teste de renomear aba reconhece a recusa de âncora ausente:
essa guarda é anterior à comparação de assinatura, e deve continuar recusando.

Comando: `node r53/testes/inicializacao_inventario_imagens.js`.
Incluído em `nuvem-b47/conferir.py --smoke`. CI completo
[40713143485](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/40713143485)
aprovado no código `b35436ecd67dd20366be547000a8382a2b337b71`, em 28/10 às
12:13:10 Brasília: 2.826 cenários de inicialização (2.747 anteriores + 79),
zero falhas. Pacote nove arquivos, sintaxe 277 Python/245 JS-GS e demais
regressões passaram. Duplicado 40713131601 cancelado. Fechamento posterior
somente documental [skip ci], sem nova suíte ou publicação.

## Ensaio real no Google

Planilha técnica nova, privada, vazia e descartável; não é uma ficha oficial,
de jogador ou cópia preenchida. Sonda `probe_imagens.gs`, `@OnlyCurrentDoc`,
ID e nome exatos validados localmente. Sem Drive/UrlFetch/acionadores/publicação,
permissões de compartilhamento ou escopos amplos novos. Só logotipo público
fictício em A1, espelho `=A1` em B1 e relatório de indicadores sem URL.
O editor foi relido pela área de transferência e comparado ao código proposto.
O seletor de funções não respondeu; para medir/limpar, a função já selecionada
foi transformada em wrapper da função correspondente, sem preparar de novo.

Horários de Brasília, 28/10/2026:

- Preparação: 11:59:44–11:59:48.
- Primeira medição: 12:06:18–12:06:22, miolo 2.291 ms.
- Segunda medição: 12:06:53–12:06:55, miolo 892 ms.
- Limpeza: 12:07:28–12:07:30.

Nas duas medições: CellImage reconhecida em `getValue` e `getValues`, espelho
também CellImage, URL legível e igual nas leituras da mesma execução.
Na segunda execução, o hash da URL também coincidiu com o anterior. Só o hash
foi guardado. Isso comprova duas execuções próximas, não estabilidade após
horas, expiração, outra conta ou cópia. A recusa de identificação divergente
na limpeza continua obrigatória.

Ao trocar A1 por FOTO: texto confirmado, fórmula B1 preservada e resultado B1
igual a FOTO. Releitura nativa de A1:H12 confirmou todos os indicadores e a
fórmula. A descartável foi movida à lixeira e as duas abas do ensaio fechadas.
Evidências privadas em `nuvem-b47/saidas/inventario-imagens-20261028/`, ignoradas.

Esse ensaio caracteriza a API; não executou o inventário completo, a limpeza de
fotos do protótipo, inicialização geral ou criação por drive.file numa ficha.

## Próxima etapa

Conferência de arte/consistência temporal e orquestração dos domínios, orçamento
conjunto, automações/treinos/notas, novo responsável e integração/prova nativa
com drive.file. Não ativar criação, instalar pacote integral, mesclar ou publicar.
GPT-6.1 Sol / Alto para implementar; Médio para revisão focal.
