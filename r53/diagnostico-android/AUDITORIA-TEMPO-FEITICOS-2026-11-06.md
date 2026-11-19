# Revisão da PR74 e auditoria de Tempo · 06/11/2026

PR74 `758c571` sem conflitos com a PR73, com os dois checks
aprovados. Passaram os testes locais de alcance de benefícios,
alcance de cura, Prática Cotidiana (1.000 verificações) e replay
privado da instalação incremental. Nenhum bloqueio encontrado no
escopo da PR74.

A auditoria usou Era e Ciclo com a PR74 e a R66 em
`JJK---Project@e3058ad29180fdec2efec75b512446c49bf87b3d`, nas entradas
Rápido, Reação, Armado, Concentrada/Duradoura, Atrasar e Carregar.

## Achados

- **Carregar e Armado nos feitiços comuns.** Na Classe 3, o resumo
  `FICHA AMALDIÇOADA!D81` mostra só “Ação Padrão · 9 PE · 18 m”
  com Carregar. Com Carregar e Rápido, mostra só “Ação Bônus ·
  9 PE · 18 m”. A primeira etapa de Carregar exige Ação Padrão e
  pagamento de PE, e a ação do cartão vale no turno seguinte.
  Com Armado, a Padrão e o PE valem ao armar, e o gatilho resolve
  sem Reação. A montagem válida de Armado mostra somente a
  Padrão no resumo. `DADOS_R53!FD2` também não descreve esses
  procedimentos para o personagem. O problema é de apresentação.
- **Prazo de Guarda.** Em ambas as montagens válidas, a saída interna
  `DADOS_R53!FD2` diz que Guarda dura até o fim do próximo turno
  e acrescenta uma orientação genérica de prazo prolongado. Com
  Guarda como único estado prolongado, a R66 prevê 10 minutos para
  Concentrada e 1 minuto para Duradoura. O resumo dos efeitos não
  indica esses valores. O campo visível de avisos permaneceu vazio
  nos dois casos válidos.

## Controles

Rápido mostrou Bônus, Reação mostrou Reação, e Atrasar mostrou
Completa. Rápido com Atrasar, Armado com Carregar e Concentrada
com Duradoura foram rejeitados com os avisos esperados. O preço
base foi 9 PE em todos os cenários de Classe 3.

Foram 12 cenários por cópia. O conector aplicou entradas temporárias
e um marcador de preparação para conferir o cálculo. O ensaio
não executou a conjuração, o gatilho ou o avanço dos turnos. As
11 entradas de ensaio foram repostas e 320 células foram relidas
por cópia, incluindo 259 posições de MONTAGENS, sem divergências
e sem erros nos intervalos. Evidência privada em
`nuvem-b47/saidas/auditoria-tempo-feiticos/`.
