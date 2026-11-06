# Instalação da PR77 e auditoria de Restrições · 06/11/2026

## PR77 nas descartáveis

A PR77 `fa2acaa` está sem conflitos e com os dois checks aprovados.
O Código anterior foi guardado em arquivo privado e conferido por
hash com os dois projetos. As 753 fórmulas da PR76 de cada cópia
passaram pela guarda do preparador antes da aplicação.

O Código.gs foi salvo e relido integralmente nas duas descartáveis.
O EditorR53 manteve o hash anterior. SHA-256 do Código instalado
`cc5b05bf9de303804a1726d583934526162b1eece43e255ddc126fd6f3ba28cd`.

Foram instaladas e relidas 753 fórmulas por cópia, em 21 lotes nas
colunas CK, CP e FX de DADOS_R53. A releitura encontrou zero erros
de fórmula e nenhuma diferença de nota ou validação.

| Cópia | Recuperações em cartões comuns | Recuperação em Classe 0 |
| --- | --- | --- |
| Era | CK2 e FX2 | CP252 |
| Ciclo | CP2 e CK2 | FX253 |

As seis fórmulas foram apagadas na interface e voltaram idênticas
à proposta. As seis execuções do acionador simples `onEdit` foram
registradas como concluídas. DADOS_R53 voltou a ficar oculta e
a célula temporária de transporte voltou ao vazio. A releitura
de 595 células por cópia, incluindo 532 posições de MONTAGENS,
encontrou zero diferenças fora do lote.

## Pente-fino

A referência usada foi a R66 de
`JJK---Project@e3058ad29180fdec2efec75b512446c49bf87b3d`.
Os casos foram reproduzidos na Era e no Ciclo com a PR77 instalada.

- **Sem Volta com efeito garantido.** Três montagens Classe 3
  permaneceram VÁLIDAS, sem aviso, e receberam 3 pontos de crédito.
  As montagens eram cura automática em aliado disposto, 6 PV
  temporários automáticos e dano por ataque com 1d8 de cura
  explicitamente independente. A R66 exige possibilidade de
  falha completa. A rota direta dispensa o aviso de Sem Volta,
  que só consultava o modo explícito de resolução do dano, e
  a devolução permanece disponível. No controle de ataque único,
  o crédito foi 2, limitado ao preço pago pela única Melhoria.
- **Restrições inválidas ainda financiam Classe 0.** Em Projétil
  com Precisão, Sobrecusto e Queima-Roupa foram rejeitados pelo
  aviso de Classe 0, mas cada um devolveu 1 ponto e o cartão
  mostrou 6d8, ante 5d8 sem Restrição. Sobrecusto ainda mostrou
  0 PE, logo não havia adicional a pagar. Queima-Roupa em
  Projétil tem peso Médio e fica indisponível em Classe 0.
  Barulho, Restrição Leve válida, devolveu 1 ponto e mostrou 6d8
  como controle. O retorno de Classe 0 é definido antes do
  aviso de peso, e a rota direta fixa a confirmação da Restrição.

Também passaram Carregar em cura automática, Inescapável em
Projétil de dano e as duas regressões focais de Frágil e Fica.
Os dois grupos de divergências já existiam nas regras da PR76
e ficaram registrados separadamente da correção da PR77.

Foram 12 cenários por cópia. As 21 entradas temporárias foram
repostas. A releitura de 620 células por cópia, incluindo 539
posições de MONTAGENS, encontrou zero diferenças e zero erros.
A PR77 permanece instalada apenas nas duas descartáveis ensaiadas.
Evidências privadas em `nuvem-b47/saidas/instalacao-fragil-fica/`.
