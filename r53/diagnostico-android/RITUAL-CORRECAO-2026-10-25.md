# Ritual — falso alerta de Técnica Inata · 25/10/2026

A leitura nativa do exemplo confirmou requisitos de nível e Inteligência suficientes e rota estruturada igual a 1 (Fundamento/Técnica). O único aviso de aquisição era “Conferir Técnica Inata”. A fórmula antiga testa apenas a identidade Ritual, sem consultar técnica ou origem. Por isso o aviso pode aparecer também em origens do livro: não é uma incompatibilidade específica da origem custom.

`usos.py` agora usa, como padrão, a rota resolvida de `fam["ROTA"]`. Essa fonte já incorpora as escolhas de origem custom e distingue Técnica, Sem Técnica, Marcial e Marcial sem energia. Uma verificação explícita fornecida pelo integrador continua tendo precedência. As condições de nível, Inteligência, aprendizado das outras aptidões, duplicação e consumo continuam emitidas.

A mudança foi conferida nas doze vagas com fixture focal, sem montar a ficha inteira. Três testes novos do emissor e os 50 testes existentes do motor passaram. QA nativa sintética passou 12 cenários/24 verificações: origem do livro e custom elegíveis, identidade herdada, rotas incompatíveis, requisitos mínimos e insuficientes, outra aptidão, rota inválida e vazio. A QA das demais condições serve de controle; nível/atributo não foram alterados por este patch.

## Fichas existentes

A ficha fornecida pelo usuário foi apenas lida. Nenhuma alteração foi aplicada nela ou na definitiva. O pacote GS também não foi regenerado.

`preparar_correcao_ritual.py` prepara um incremento somente nas 12 fórmulas auxiliares de DADOS_AM que contêm o alerta incondicional. Ele exige todas as vagas, recusa fórmulas divergentes, escreve apenas `userEnteredValue` e guarda o valor anterior para recuperação. Os alvos, leituras e lote preparado ficam em `nuvem-b47/saidas/ritual-20261025/`, ignorada pelo Git.

Para aplicar em uma ficha preenchida: autorização para editar o alvo, snapshot atual, releitura de todas as fórmulas anteriores, ensaio em cópia e conferência posterior dos avisos/requisitos. Não executar construir/continuar nem importar Office. Conferir também o comportamento da restauração automática, pois o código gerado anteriormente ainda contém o estado antigo.

A investigação de Ritual é independente das pendências de abertura/salário. Cores estão resolvidas no estado atual do repositório e não foram reabertas.

Próxima aplicação integrada: Sol/High para snapshot, ensaio e validação. Conferência focal: Sol/Medium. Configurações não foram alteradas.
