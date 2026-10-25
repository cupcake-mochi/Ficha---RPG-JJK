# Revisão nativa ampliada · 25/10/2026

**Erro confirmado e corrigido nas duas oficiais:** a carga de equipamento das invocações 2–6 e 8–12 somava linhas anteriores à expansão da ficha. Um volume preenchido podia deixar o total em zero e ocultar o aviso de excesso. Não produzia `errorValue`, por isso uma varredura de erros de fórmula não detectava o problema.

Os alvos continuam sendo os dois modelos em [OFICIAIS.md](../OFICIAIS.md). A ficha do amigo e os documentos históricos não foram alterados.

## Correção aplicada

- `extensoes_custom.formula` agora acompanha intervalos com a aba repetida nas duas pontas, como `'INVOCAÇÕES'!Y231:'INVOCAÇÕES'!Y233`, em ambas as transformações de linhas.
- Em cada oficial, foram corrigidas somente dez fórmulas: `DADOS_INVOC!EI3:EI7` e `EI9:EI13`.
- O helper incremental de carga foi instalado no `Codigo.gs`, preservando Ritual, salário, paleta e Android. Valida todos os moldes antes de alterar, aceita repetição sem mudanças e recusa bases divergentes.
- Dois snapshots nativos atualizados foram criados antes da aplicação. As fórmulas foram relidas iguais ao delta; os códigos salvos foram recarregados e copiados integralmente de volta, iguais ao proposto.
- SHA-256 do código instalado nas duas: `1609a8890f23c496b4c1d56525badb568b19d611d73713d673523e47a12fbeaf`.

Fontes GS regeneradas: **7f85d740f71c4cb6**. Comparação dos valores das 25 abas com o commit-base `4744f68`: exatamente as dez fórmulas de carga mudaram. O pacote integral foi conferido, mas **não instalado**. O módulo nativo permanece na geração-base `e142593fdc5be157` com os incrementos publicados.

`verificarPacoteR53` executou na Era da Revolução depois do ajuste: 25 abas, 249 contextos, `sobras: []`, execução concluída. A execução manual no Ciclo não foi repetida, pois já havia solicitado autorização na rodada anterior; seu código foi salvo e relido integralmente igual ao da Era.

## Testes desta rodada

Todos os preenchimentos de ensaio ocorreram em uma cópia nativa nova, sem importação Office nem reconstrução.

| Frente | Cobertura e resultado |
|---|---|
| Equipamento e estado | 33 cenários, 118 grupos de assertivas aprovados: armas, escudos, uniformes, treino, requisitos de Força, Defesa, carga, buffs/debuffs, exaustão, sequelas, Morrendo, menus e nível. |
| XP | 288 combinações de tipo de missão, adicional e desconto; total dos quatro blocos e espelho da FICHA conferidos. |
| Famílias | 12 cenários nas 12 entidades; todas as 108 vagas, contagem, duplicatas, autonomia e limites. 2.016 comparações aprovadas. |
| Carga das entidades | Defeito reproduzido nos dez lugares. Depois da correção: 36 totais conferidos, incluindo dois ensaios com os 108 campos preenchidos, inteiros e fracionários. Aviso visual “7 de 5 · acima do limite” conferido na segunda invocação. |
| Releitura das oficiais | INVOCAÇÕES e DADOS_INVOC completas em cada uma: quatro abas, 280.326 posições, nenhum `errorValue` retornado. |
| Fonte e transporte | 30 testes Python aprovados; teste do helper sobre o módulo realmente instalado, idempotência e recusa atômica; pacote com nove arquivos, 25 abas e 249 contextos aprovado. |

A ficha pessoal foi lida em `FICHA!A1:AX120`, `FICHA PESSOAL!A1:BT110` e `DADOS!A1:EG100` a cada cenário. Não houve erros de cálculo retornados nessas leituras. Os oráculos usam regras independentes do gerador; a preparação agora pode ler a baseline nativa para não depender de coordenadas/constantes de um XLSX histórico.

O leitor inicial de evidências de Famílias tratava incorretamente células vazias omitidas pela API. Foi corrigido; os cenários sem recibo completo foram retomados e a conferência final usa todos os 12 recibos. Isso foi um problema do teste, não da ficha.

## Salário e limites da conferência

A primeira execução do oráculo histórico da ficha pessoal acusou 32 divergências, todas restritas ao campo salarial: esperava texto monetário e atualização imediata ao mudar Grau. A instalação atual usa número e a rotina salarial. Escritas de API **não disparam onEdit**. O campo legado foi explicitamente excluído com `--sem-salario-legado`; a evidência bruta foi preservada. Não contar essa exclusão como aprovação do salário atual.

O novo projeto QA solicitou autorização. O usuário respondeu que autorizaria e avisaria; a conclusão ainda não foi confirmada. Continuam pendentes os ensaios adicionais de troca/restauração de Classe, colagens/entradas inválidas pela interface e salário por eventos. Não instalar acionadores para suprir essa falta. Nenhuma medição Android foi feita nesta rodada.

A cópia QA recebeu as fórmulas corrigidas e teve as entradas de teste restauradas. Seu código ainda antecede o helper de carga; instalar o mesmo delta nela antes de certificar recuperação automática. Não confundir a cópia de QA com as oficiais, onde o helper já foi salvo e relido.

## Retomada

1. Confirmar a autorização do projeto QA `1EpXc1nVK2p_qvdI3Rq79x7gsCwTpszk3D_R2QflUw556az09usmmqG4J` e ler o estado antes de editar. A planilha QA é `1_GoTkwA1r0EFs9rT9NLKEB_2jZ0knwek7isf8iqJj3s`.
2. Instalar nela o helper de carga por âncora estrita e conferir o código salvo. Testar edição nativa, troca de Classe, recuperação e entradas inválidas; salários em cópia, sem criar acionadores.
3. Não reaplicar a correção nas oficiais. Não importar Office, executar construir/continuar, abrir agentes ou mesclar main.

Evidências privadas: `nuvem-b47/saidas/revisao-nativa-20261025/`, ignoradas pelo Git. Incluem snapshots, recibos completos, logs, código antes/depois e captura visual. Resultado sanitizado em `REVISAO-NATIVA-2026-10-25.json`.

Modelo recomendado: **Sol/High** para a continuação dos ensaios integrados; **Medium** para conferir este relatório. Nenhuma configuração foi alterada automaticamente.
