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

## Misto (escolhido para seguir)

Página 1 do **C · Expansão** com o repertório em fichas catalográficas do **A · Registro**. `saidas/estudo-misto.pdf` e `saidas/previa-misto.png`.

Estrutura proposta, seis páginas:

1. **Personagem** · atributos, recursos, combate, perícias e TRs.
2. **A técnica** · Fundamento, régua de espaços do repertório (conta feitiços, talentos, expansão e entidade contra o limite do nível), 5 Talentos pagos + a linha do CE 4, 12 Aptidões só pelo nome, Classe 0 com as vagas que abrem nos níveis 5, 11 e 17.
3. e 4. **Repertório** · 12 fichas de feitiço, Manejo ou Kata.
5. **Poderes avançados** · Expansão de Domínio (degrau, Acerto, Efeito; abertura, raio, duração, desconto, barreira e dados do Acerto calculados), três Liberações Máximas (níveis 10, 20 e 30) e a Técnica Máxima (dados, pontos e PE pela faixa de nível).
6. **Quem é** · história, Origem e equipamento.

O que ainda não abriu pelo nível fica **SELADO** com o carimbo 封, e o selo some sozinho quando o nível chega lá.
