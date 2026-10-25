# Pente-fino nativo — 25/10/2026

**Correções incrementais aplicadas e relidas nas duas oficiais de [OFICIAIS.md](../OFICIAIS.md).** Esta rodada complementa as revisões de Ritual e carga; não substitui o pacote integral nem reconstrói fichas preenchidas.

## Defeitos adicionais encontrados e corrigidos

1. **Troca de Classe interrompida.** Um evento simples terminou em 30,707 s, deixando os pontos da Classe anterior visíveis. O editor agora lê as versões juntas, reaproveita o cartão lido e prepara regras antes de gravar. A proteção de edição pendente continua preservando os pontos na Classe de origem.
2. **Validação de função bloqueada.** Na Máxima da última entidade, o Google recusou o traço de bloqueio enquanto a célula ainda tinha validação estrita de checkbox. A regra de destino passa a ser aplicada antes do valor. A reprodução nativa voltou a passar. A edição de pontos/checkboxes também prepara o evento em memória antes de escrever, evitando leituras após cada alteração.
3. **Missões excediam o prazo do evento simples.** Registro salarial e atualização pessoal provocavam recálculos sucessivos e carregavam os catálogos completos. O fluxo limitado ao painel de missões conserva o evento, as 292 fórmulas de XP e a curva/índices da campanha, sem carregar o pacote de combate. A conferência salarial prepara suas leituras e grava depois da atualização de XP/nível, sob o bloqueio existente. Edições que ultrapassam os limites do painel continuam no caminho original.

O caminho de XP conserva subida sem redução automática de nível e o limiar de feito. As 292 fórmulas da fonte foram comparadas integralmente aos moldes instalados antes da aplicação. Nenhuma regra salarial, peso, data de personagem, valor de campanha, posição de Família ou fórmula de combate foi substituída nesta rodada.

## Aplicação e recuperação

- Dois snapshots nativos novos foram criados imediatamente antes da aplicação final. Seus endereços e as cópias integrais dos códigos ficam somente na pasta privada ignorada pelo Git.
- Antes de escrever, os códigos oficiais foram copiados e comparados às bases conhecidas. Alterados somente `Codigo.gs` e `EditorR53.gs` em cada projeto.
- Depois de salvar, ambos os projetos foram recarregados e os quatro arquivos copiados integralmente de volta. Comparação exata aprovada.
- `Codigo.gs`: SHA-256 final `618e7882babc6f00c51907d0ee818523604842bcac5e5b462a8301d7e85c8c4e` (base `1609a8890f23c496b4c1d56525badb568b19d611d73713d673523e47a12fbeaf`).
- `EditorR53.gs`: SHA-256 final `6cb49d97c49fe93591967b86c79c0435f74c1bf0b34c4a62d004ebb3ec887f81` (base `c0e10c50ca33f551819f3e3004726cba98bd633d23f359c368099480e06f403f`).
- O preparador de missões recusa âncoras divergentes e reaplicação. Para rollback, usar os arquivos anteriores do snapshot correspondente, sem executar construir/continuar.
- As entradas de ensaio foram restauradas nas cópias e relidas sem divergências; os marcadores temporários foram alinhados ao estado restaurado.
- Nenhum acionador, acesso, agente ou importação Office foi criado. Cores não foram reensaiadas. Ficha do amigo e documentos históricos intactos.

## Cobertura adicional desta rodada

| Frente | Evidência aprovada |
|---|---|
| Custom e campanha | 22 cenários nativos, 62 verificações: equipamentos, origem custom, capacidades, colisões/entradas inválidas, volumes fracionários, atributos, treino, deslocamento, Morrendo, sequelas, XP alternativo, vida rolada e override zero. |
| Estrutura nativa | 2.453 verificações dos 249 contextos, limites de grade, versões e posições de armazenamento. |
| Cartões nativos | Classes independentes, edição pendente/atrasada, negativos e fórmulas inválidas, recuperação de fórmula, Classe zero, liberação e Máxima da última entidade. |
| Interface real | Troca de Classe, preservação de edição pendente, rejeição de negativo, fórmula sobrescrita e colagem de três campos; releitura confirmou conteúdo visível e armazenamento. |
| Missões | Nove verificações nativas: registro, chave textual, subida de nível 1→2, identidade/data após renomear, fórmula de XP restaurada e retirada da missão. Evento simples real confirmado em execução concluída. |
| Salários | Oito verificações nativas de três períodos vencidos e reexecução: total 337.500, três créditos, nenhum pagamento duplicado e saldo estável após congelar. |
| Dinheiro e emissão | Cinco verificações de ganho/gasto/inválido e datas; sete de emissão, repetição, recusa de retroação/futuro e recuperação do painel. |
| Barras | Três SPARKLINE conferidas visualmente com recursos positivos de 20%, 50% e 80%; entradas de ensaio restauradas. |
| Regressão local | 562 verificações do editor; 2.709 da integração de missões/curva de nível; 112 do motor salarial legado; 95 casos do lote salarial. Os testes locais não medem o Google. |
| Transporte | Pacote de nove arquivos, 25 abas e 249 contextos aprovado; geração de dados `7f85d740f71c4cb6`. Pacote integral **não instalado**. |

As rodadas anteriores continuam válidas e são descritas em [revisão de Ritual](REVISAO-2026-10-25.md) e [revisão nativa ampliada](REVISAO-NATIVA-2026-10-25.md): 596 verificações de Ritual, 89 cenários/285 condições da R53, 33 cenários pessoais/118 grupos, 288 combinações de XP, 2.016 comparações de Famílias e 36 totais de carga. As 58 abas haviam sido varridas sem erros de cálculo retornados; não repetimos essa leitura extensa após alterações restritas aos scripts.

## Tempos observados e limites

Eventos simples reais concluídos: troca para nova Classe 23,896 s; edição pendente 22,163 s; recuperação de fórmula 13,494 s; colagem final 19,531 s; missão final 27,781 s. Na versão final, os quatro eventos de missão chamados pelo ensaio nativo levaram aproximadamente 23,1–27,4 s; essas chamadas manuais têm limite diferente do evento simples. A última Máxima passou em aproximadamente 22,7–24,3 s. São observações no Google, não benchmarks de Android ou garantias de prazo.

Foram preservadas as tentativas que falharam: bateria inicial longa interrompida pelo limite de seis minutos; versões intermediárias que ainda excediam 30 s; e uma comparação de fórmula que estranhou a remoção de aspas opcionais pelo Google. Essa última foi distinguida de erro de cálculo, normalizada e conferida também por restauração real na interface. Os `#N/A` provocados por regra inválida/rolagem ausente foram diagnósticos esperados, não falhas ignoradas.

Os testes abrangem cenários representativos, limites e regressões reproduzíveis; não demonstram ausência absoluta de defeitos, todas as combinações possíveis, falhas de rede ou desempenho em todos os celulares. O tempo do Google ainda varia e alguns eventos têm margem pequena até 30 s. Não foi feita nova medição de RAM ou latência Android.

Evidências completas, baselines e capturas: `nuvem-b47/saidas/pente-fino-20261025/`, fora do Git. O harness versionado exige informar explicitamente o ID da cópia descartável e recusa qualquer outro documento. Para nova manutenção integrada: Sol/High; para conferir esta entrega: Medium, sem alteração automática de configuração.
