# Instalação incremental da PR83 nas descartáveis · 07/11/2026

A revisão partiu da PR83 `02a7fc1`, aberta, sem conflitos e com
dois checks aprovados. Passaram novamente os testes locais de
Forma e função, transporte protegido, reversão e recuperação
simulada das montagens.

Era e Ciclo tinham o Código da PR82 com SHA-256
`ec0bbd157b7b3bf10b8aee6252896971d0332ae1788f4d7a3b2f13d6928acc75`.
O EditorR53 das duas cópias tinha SHA-256
`676337f165f7056db20364e5327f2793e957d2db405199a75009f5f44a163c49`.
Os arquivos foram arquivados antes da aplicação.

O preparador conferiu snapshots novos das 251 fórmulas de FX por
cópia e gerou os pedidos de aplicação e reversão. Código.gs foi
salvo e relido nas duas cópias com SHA-256
`cf8dc5960121fcc4677f4b19288932ee738be39e2d6d2a61a10d1a3f3ef59672`.
O preparador substitui somente o bloco dos moldes de recuperação.

Foram instaladas 251 fórmulas em 21 lotes por cópia, com releitura
de cada lote, zero erros e zero diferenças de nota ou validação.
As fontes GS integrais estão versionadas. O ensaio aplicou a
atualização incremental.

## Recuperação por edição real

As células foram selecionadas e apagadas pela interface do Sheets.
Cada uma voltou idêntica ao retrato da fórmula esperada.

| Cópia | Célula | Contexto | Execução de onEdit |
| --- | --- | --- | --- |
| Era | FX2 | Cartão comum | 12,059 s, concluída |
| Era | FX252 | Classe 0 adicional | 10,690 s, concluída |
| Era | CK2 | Devolução herdada | 12,358 s, concluída |
| Ciclo | FX41 | Classe 0 existente | 15,172 s, concluída |
| Ciclo | FX253 | Classe 0 adicional | 13,521 s, concluída |
| Ciclo | CZ2 | Crédito total herdado | 13,591 s, concluída |

Os tempos são os de execução registrados pelo Apps Script.

## Controles e preservação

Passaram seis controles por cópia com a PR83 instalada.
Escolher em Projétil, Perseguir em Cone, Reserva sem cura e Sugar
com 0d8 após Toca a Alma pediram revisão com o aviso específico.
Reserva com cura e Sugar com dano restante ficaram válidos.

Os testes adicionais de Família ficaram registrados na auditoria
de Mira. As 18 entradas temporárias foram repostas em cada cópia.
A comparação com o snapshot anterior à instalação cobriu 861
posições por cópia, incluindo 539 de MONTAGENS. Encontrou zero
diferenças e zero erros nos intervalos conferidos. DADOS_R53
voltou a ficar oculta. A PR83 permanece instalada nas descartáveis.

Evidências privadas em
`nuvem-b47/saidas/instalacao-forma-funcao/`.
