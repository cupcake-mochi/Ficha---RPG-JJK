# Instalação incremental da PR84 nas descartáveis · 07/11/2026

A revisão partiu da PR84 `24a91bd`, aberta, sem conflitos e com
dois checks aprovados. Passaram novamente a matriz local de
Corrói e o teste de transporte e reversão. A correção usa a
Família Mira do próprio cartão, incluindo as entidades.

## Snapshot e aplicação

As duas descartáveis tinham Código.gs da PR83 com SHA-256
`cf8dc5960121fcc4677f4b19288932ee738be39e2d6d2a61a10d1a3f3ef59672`.
O EditorR53 das duas tinha SHA-256
`676337f165f7056db20364e5327f2793e957d2db405199a75009f5f44a163c49`.
Os arquivos foram arquivados antes da aplicação.

Foram guardados snapshots atuais das 251 fórmulas de FX de cada
cópia. O preparador validou esses valores e produziu propostas e
reversões. O Código incremental foi salvo e relido nos dois projetos
com SHA-256 `da89202e8a7af2029855196dc464ef4091d2174393a954860cb5381d8ee5709e`.
Foi substituído somente o bloco dos moldes de recuperação no Código.

As 251 fórmulas foram instaladas em cinco lotes por cópia. Cada lote
teve conferência dos valores anteriores, gravação e releitura.
Encontrou zero erros de fórmula e zero diferenças de nota ou validação.

As fontes integrais continuam versionadas. A aplicação deste ensaio
foi incremental e preservou o restante do Código instalado.

## Recuperação por edição real

As seis fórmulas abaixo foram apagadas pela interface do Sheets.
Voltaram idênticas às propostas da PR84, com as execuções registradas
como concluídas no Apps Script.

| Cópia | Célula | Contexto | Execução de onEdit |
| --- | --- | --- | --- |
| Era | FX2 | Cartão pessoal | 9,260 s |
| Era | FX48 | Especial da primeira entidade | 7,567 s |
| Era | FX252 | Classe 0 adicional | 7,706 s |
| Ciclo | FX2 | Cartão pessoal | 9,565 s |
| Ciclo | FX191 | Especial da última entidade | 12,223 s |
| Ciclo | FX253 | Classe 0 adicional | 8,266 s |

Os tempos são os de execução mostrados pelo Apps Script.

## Controles após a instalação

Passaram 39 controles por cópia. No cartão pessoal, Corrói com
Mira Neutra pediu revisão, Corrói com Mira Livre ficou válido e
Fura com Mira Neutra permaneceu válido. Foram repetidos os mesmos
três controles nas 12 entidades, usando Mira Normal e Livre.
Os preços e os descontos tiveram os resultados esperados.

As 330 entradas temporárias foram repostas em cada cópia. A
comparação com o snapshot anterior à instalação cobriu 5.218
posições por cópia, incluindo 3.647 de MONTAGENS, sem diferenças
ou erros nos intervalos conferidos. DADOS_R53 voltou a ficar oculta.

A PR84 está instalada nas duas descartáveis. O pente-fino seguinte
de aprovação das Liberações Máximas tem registro separado.
Evidências privadas em `nuvem-b47/saidas/instalacao-corroi/`.
