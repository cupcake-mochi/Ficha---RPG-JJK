# Inventário e equipamento · 28/10/2026

Etapa 7 parcial da Carteira viva. PR 31 em rascunho; protótipos fora do pacote
e do bot, com criação incondicionalmente bloqueada. Nenhuma oficial ou ficha
de jogador foi alterada. Base reconferida: main ef361cc, incorporada anteriormente
por a72adc0. Runtime do bot permanece 26ec106; consumidor PR 84 só documentado.

## Cobertura

Três perfis do executor existente, com prévia, diário, trava e retomada:

| Perfil | Campos da FICHA PESSOAL | Comportamento |
|---|---|---|
| Equipados | D64, S64, AH64, L86, AN86 | Soco, mão livre (—), Traje 1, bônus de carga 0 e situação do Traje vazia |
| Equipáveis guardados | D/K/M/S/U/W/AE/AG/AI/AK/AQ, linhas 92–99 | 88 campos: nomes/quantidades vazios, fórmulas originais restauradas |
| Itens guardados | D/T/V/Z/AP/AR, linhas 104–109 | 36 campos: nomes/quantidades vazios, fórmulas de Volume restauradas |

São 129 campos de conteúdo/notas. Mais quatro operações **somente de notas**
em D66, S66, D86 e AF86 removem avisos herdados sem escrever no conteúdo
calculado. As fórmulas dessas quatro células continuam protegidas. As notas
vivas deverão ser regeneradas na fase de automações após a inicialização geral;
esvaziá-las não é prova de que toda a nova ficha cumpre os requisitos.

As duas últimas linhas de equipáveis são livres; seus valores manuais pessoais
saem, mas suas notas de instrução voltam. Estigma, Desgaste, Grau e Volume
sobrescritos voltam às fórmulas do modelo, sem herdar resultados numéricos.
Não concede estoque, dinheiro ou treinos; não altera catálogo, regra de mesa,
mesclas, formatos, validações ou equipamento das entidades. Os seis contratos
anteriores e a assinatura financeira v1 permanecem iguais.

## Variante decimal e recusa

A leitura das duas oficiais encontrou as 12 fórmulas de Volume dos itens com
ponto e vírgula e decimal `0,1`. O contrato reconhece essa representação exata
da fórmula original com `0.1`. A variante só é gerada para os Volumes de itens;
não normaliza fórmulas arbitrárias nem muda os contratos anteriores.
Trocar o número por 0,2, a linha da quantidade ou o limite do catálogo continua
causando recusa antes de escrever. Fórmula pessoal desconhecida também recusa;
a rotina não tenta adivinhar se uma expressão diferente é equivalente.

## Validação

417 cenários direcionados de formação/técnica/Famílias/inventário passaram
(139 adicionais aos 278 anteriores), mais 101 financeiros. Falhas antes/depois
de cada escrita, retomada, concorrência, notas, preservação e contrato contra
a montagem pública completa estão cobertos. A coleção de inicialização soma
921 cenários (101/82/78/243/417), confirmados pelo CI desta entrega.
A VM não calcula fórmulas Google nem mede sua latência.

Google: metadados e FICHA PESSOAL D61:AT109 das duas oficiais, só leitura.
161 entradas/guardas por oficial; zero diferenças depois da variante decimal.
Nenhuma escrita nas oficiais ou em arquivo de jogador.

Ensaio numa cópia privada e descartável do Ciclo, **por projeção dos efeitos
via Sheets API**, não execução dos diários Apps Script ou do OAuth das Guias:

- 133 notas fictícias e 22 valores fictícios, incluindo Bastão/quantidade,
  duas linhas livres, Estigma/Desgaste, itens dos dois lados, Volume manual
  e bônus de carga; leitura confirmou os dados antes de restaurar.
- 129 campos/notas restaurados e quatro notas isoladas limpas; fórmulas
  devolvidas na variante nativa aceita. Nenhum erro nas faixas inspecionadas.
- 2.678 posições inspecionadas; 10.450 comparações de conteúdo/notas/validação/
  formato que deveriam permanecer iguais, sem diferenças. Excluídos apenas
  conteúdo/notas dos alvos autorizados; formato/validação sempre comparados.
- Soco, mão livre e Traje 1 preservam o padrão do modelo. Carga voltou a
  `0,3 de 5`, igual ao retrato inicial: o Traje 1 conta Volume, mesmo com
  o estoque vazio. Não substituir esse resultado por zero.
- Cópia enviada à lixeira ao terminar e aba temporária fechada.

Faixas comparadas: FICHA PESSOAL D61:AT109; CONFIGURAÇÃO C38:H88;
DADOS_CUSTOM AA2:AK10, AU2:AX12, BM2:BU10; DADOS CZ6:CZ46.
Não é conferência integral do arquivo nem prova de execução/falha/retomada
nativa do inicializador. Nenhum novo escopo, permissão, acionador ou instalação.
Não guardar IDs privados, snapshots ou credenciais no Git.

## Continuação

Próximo: campos pessoais restantes da CARTEIRA e inventário de propriedades
que podem restaurar o personagem anterior; depois entidades/cartões/MONTAGENS.
Ainda faltam fotos/arte, caches/recuperações, orquestração/conferência conjunta,
automações/notas vivas/treinos iniciais, novo responsável, integração executável
com drive.file e prova nativa completa antes de liberar criação. Não reiniciar
fases apagando diários. Não mudar o endpoint bloqueado do bot.

Sem merge em main, deploy na Discloud, Gateway ou chamada paga. Próxima
implementação GPT-6 Astra / Alto; revisão focal Médio.

## CI

CI Linux aprovado no código `86410bee3fc70fa81f124a695253e032688c3ebe` em
28/10/2026 às 08:56:07 Brasília: [40683614201](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/40683614201).
921 cenários confirmados (101/82/78/243/417), pacote de nove arquivos, sintaxe
277 Python/220 JS-GS, catálogo/progressão/Kaori e demais regressões aprovados.
Run duplicado 40683604255 cancelado. Fechamento apenas documental com
`[skip ci]`; sem repetir suíte ou publicar pacote.
