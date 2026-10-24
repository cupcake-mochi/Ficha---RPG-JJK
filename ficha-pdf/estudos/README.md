# Estudos de estilo · ficha em PDF

Três direções visuais para discutir antes de refazer a ficha. São só desenho, sem campos preenchíveis, preenchidos com a Kaori do livro e no Mizuki escuro. Cada uma tem a página 1 (personagem) e uma proposta de página 4 (repertório em cartões).

| estudo | ideia | marcas |
|---|---|---|
| **A · Registro** | o documento oficial da escola | faixa lateral de dossiê com abas, foto com carimbo 呪, código de barras, réguas com marcação nos recursos, pontilhado nas perícias, assinatura do mestre; feitiços como fichas catalográficas com furo e aba numerada |
| **B · Talismã** | ofuda e tinta | pincelada no título, kanji vertical, atributos como selos com o kanji de cada um (力 速 体 知 魂), recursos em ensō, combate em etiquetas penduradas num cordão, respingos; feitiços como talismãs |
| **C · Expansão** | painel de mangá/HUD | cantos cortados com sombra deslocada, retícula e linhas de velocidade, atributos em hexágono, recursos em barra segmentada, Defesa em losango, valores em chips inclinados; feitiços como cartas |

Toda a arte é desenhada por código (reaproveita `arte/gera.py`): carimbo, pincelada, respingo, moldura, ensō, retícula. Nada de arte de terceiro.

```bash
python3 ficha-pdf/estudos/estilos.py
```

Prévias para o celular: `saidas/previa-*.png` (página 1 e página 4 lado a lado).
