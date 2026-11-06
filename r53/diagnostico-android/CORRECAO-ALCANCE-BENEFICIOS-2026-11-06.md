# Alcance de Guarda, Impulso e Firmeza · 06/11/2026

Base PR73 em `868ebb8`. O diagnóstico está em
`AUDITORIA-BENEFICIOS-ALCANCE-2026-11-06.md`. A regra de alcance
vem da R66 em `JJK---Project@e3058ad29180fdec2efec75b512446c49bf87b3d`,
seções Formas e Alcance e área.

Os 36 cartões comuns identificam Guarda, Impulso e Firmeza em
qualquer uma das quatro vagas, pelo nome normalizado do catálogo.
O resumo usa o alcance de benefício que o núcleo já calcula.
Quando o feitiço também causa dano e as distâncias são diferentes,
o cartão separa “Dano” de “Apoio”. Cura e PV temporários podem
compartilhar a medida de apoio. Com Toque ou Aura, a medida
compartilhada aparece uma vez.

O ajuste preserva os dados de MONTAGENS, a conta de PE, a validade
do feitiço, os avisos e os cálculos de origem e área.

## Ensaio nativo

Dez cenários por descartável, Era e Ciclo, todos aprovados:

- Guarda na primeira vaga, Impulso na segunda e Firmeza na
  terceira exibiram 9 m na Classe 3 com Projétil.
- Firmeza na quarta vaga com dano mostrou 18 m de dano e 9 m
  de apoio. Guarda com Longe mostrou 36 m de dano e 18 m de apoio.
- Dano, cura, PV temporários e Guarda compartilharam o resumo.
  No estágio 2 de Integridade, o custo exibido foi 12 PE.
- Cura isolada mostrou 9 m e Empurrão com dano mostrou 18 m.
  Aura preservou a origem no conjurador e raio de 3 m.
  Toque mostrou 1,5 m.

Código e Editor foram salvos, reabertos e relidos nas duas cópias.
Ao apagar `FICHA AMALDIÇOADA!D81` pela interface, o Apps Script
restaurou a nova fórmula e os dois alcances em ambas.

Foram repostas 13 entradas de ensaio. A releitura de 359 células
por cópia, incluindo 259 posições de MONTAGENS, mostrou apenas as
36 alterações previstas, com notas e validações preservadas e sem
erros nos intervalos. Evidência privada em
`nuvem-b47/saidas/correcao-alcance-beneficios/`.

## Preparação incremental

Geração `79a9235ee3d37edc`. A comparação do pacote integral conferiu
280.001 posições e os metadados de 26 abas, com apenas as 36
fórmulas previstas alteradas. O plano da PR73 continua disponível
como etapa anterior. `preparar_alcance_beneficios.js` exige os
arquivos de Código e Editor ensaiados na PR73 e um snapshot
atualizado das 36 fórmulas. Produz apenas alterações de
`userEnteredValue` e dispõe de plano reverso. A recuperação
conserva os 251 contextos e atualiza só os 36 resumos e a assinatura
do Editor. Uma eventual promoção deve repetir o preflight em cópia
a partir da versão encontrada.

Hashes SHA-256 relidos nas duas descartáveis:

- Código `2005362b35c236dc17f241ace10d5bb075f61ec7662a1fe234fa1b5216a83e9b`.
- Editor `2ed5d1e18726708fcf4d08daa9a674d9996ccf7477bcedcbcfad0c54887fe928`.
