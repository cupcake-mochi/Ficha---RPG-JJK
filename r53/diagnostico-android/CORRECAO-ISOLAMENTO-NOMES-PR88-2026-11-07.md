# PR88 · isolamento dos erros dos nomes · 07/11/2026

## Resultado

R88-01 corrigido e ensaiado nas duas descartáveis Era/Ciclo. A contagem
filtra os nomes das especiais normais da própria entidade antes de avaliar
LEN. Erros numa básica, num extra ou noutra entidade não contaminam a
conta; erro numa especial da própria entidade continua visível. Não há
IFERROR global devolvendo zero. Números, zero, booleanos, textos e fórmulas
numéricas ocupam vaga; célula vazia e fórmula que retorna vazio não ocupam.

A retomada partiu de `0358517`, checkpoint separado da PR88 `4d22fb7`.
Somente 24 fórmulas mudam: `DADOS_INVOC!IE2:IE13` e `JJ2:JJ13`. Notas,
validações, entradas, versões e compras mantêm seus lugares e conteúdos.
As demais regras de aquisição e os avisos legítimos continuam ativos.

## Preparação e instalação

O código dos dois projetos foi copiado integralmente pela interface,
antes da escrita. Após normalizar apenas CRLF do clipboard para LF, ambos
corresponderam ao SHA-256 esperado da primeira PR88:
`8935211c6e87cd4515b0df860bd0d71524f316d08e42013f86cc9fa6b1d53bea`.
Foram feitos snapshots novos das fórmulas, das 160 entradas temporárias,
das montagens envolvidas e dos metadados. Os snapshots truncados do Linux
não foram usados como backup ou base de aplicação.

O preparador estrito produziu exatamente a proposta salva no checkpoint:
`36ca73efd1eca6809fd8ddfa1be324eebaad2f5aef0830d4c25c6aaeaaaff3bc`.
As rotas PR87 e primeira PR88 produziram o mesmo código. Foram conferidos
snapshot, reversão, localidades pt_BR/en_US, recuperação direta/mista,
preservação dos moldes e carregamento das cinco partes Android antigas.

Somente esse incremento foi salvo nos dois projetos e relido integralmente
após reabrir os editores: as duas releituras são iguais à proposta. As 24
fórmulas foram conferidas novamente imediatamente antes da aplicação.
Os 12 moldes IF inalterados e o escape das origens da ANALISE permanecem.
O pacote integral foi regenerado, mas não instalado.

## Ajustes necessários no Windows

O gzip do Node grava o sistema operacional no cabeçalho. No Windows, isso
fazia a âncora do preparador divergir, embora o conteúdo descompactado e o
fluxo comprimido fossem iguais. `expansao_domada_runtime.js` agora fixa o
byte de SO em 3, reproduzindo exatamente a âncora e o hash já ensaiados no
Linux; a guarda do hash não foi afrouxada. Um teste cobre o cabeçalho.

A primeira tentativa de empacotamento recusou o EditorR53 gerado com CRLF.
`editor_lazy.js` normaliza CRLF antes de reconhecer o catálogo. O teste
confere que as fontes LF e CRLF produzem o mesmo transporte. Após os ajustes,
o empacotamento e o smoke final terminaram com saída zero. As tentativas
intermediárias não são apresentadas como aprovações.

## Ensaios nativos

A matriz de contagem repetiu as 12 configurações da PR88 nas 12 entidades
de cada cópia: **288 casos aprovados**. Conferiu contagem, domínio 0/3,
capacidade 4, aviso de espaços e tipos dos nomes efetivamente armazenados.
Inclui textos, números, zero, FALSE/TRUE, números em texto, fórmulas
numéricas/textuais, mistura, fórmula vazia, equação literal, limite e
ausência de domínio. Nível próprio 14 e invocador 30 eram fixtures
temporárias; nenhuma compra ou versão foi alterada para obter aprovação.

Mais **16 configurações globais de isolamento**, oito por cópia, conferiram
os 12 cabeçalhos e os 12 requisitos: **384 resultados observados**.
As origens foram Básica 1, extra da Trilha, especial da primeira entidade
e especial da última, cada uma com `=1/0` e `=NA()`. O erro permaneceu na
origem; nas especiais próprias, permaneceu também no orçamento pertinente.
As outras entidades conservaram o consumo 2+3 de 4 e o aviso legítimo 5/4.
Essas variações não são 384 defeitos ou cenários independentes.

Separadamente, **dez edições reais** pela interface do Sheets passaram:

| Faixa apagada | Por cópia | Resultado |
| --- | ---: | --- |
| IE2:IE13 | 12 fórmulas | Contagem das 12 entidades recuperada |
| JH2:JJ13 | 36 fórmulas | PE, Acerto e requisitos recuperados |
| IE2:IF3 | 4 fórmulas | Bloco misto inicial recuperado |
| IE12:IF13 | 4 fórmulas | Bloco misto final recuperado |
| IE2:IF3, com P71 =1/0 | 4 fórmulas | Erro próprio preservado; outras 11 entidades íntegras |

As dez execuções onEdit constam como **Concluído** no histórico nativo.
As leituras só foram aceitas após conterem todas as fórmulas do bloco;
resposta vazia durante a execução foi relida, sem outra edição. As matrizes
de valores usaram a API e não são apresentadas como eventos onEdit.

## Restauração e preservação

As 160 entradas por cópia foram restauradas, incluindo os nomes com erros
temporários. DADOS_INVOC voltou a ficar oculta. A comparação final por cópia
cobriu **53.554 posições**:

- 53.334 de MONTAGENS, A1715:I7640, incluindo caudas vazias implícitas;
- 160 entradas temporárias;
- 60 fórmulas dos blocos envolvidos, incluindo as vizinhas inalteradas.

Resultado: somente as 24 fórmulas previstas diferem; zero diferenças
inesperadas, zero diferenças nas montagens ou entradas restauradas e
resultados calculados iguais aos iniciais nos blocos comparados. Foram
conferidos valores digitados/calculados, tipos, notas e validações nos
campos retornados. Formatação não foi escrita nem certificada por essa
comparação delimitada. Os metadados de arquivo/abas retornados pelo
conector ficaram iguais aos snapshots iniciais. A conferência visual
nativa do estado restaurado passou nas duas fichas.

## Geração e checks

Geração **e4537f58af975d8c**. Comparação de **280.056 posições e 26 abas**
contra as fontes anteriores da PR88: exatamente 24 alterações, metadados
preservados e nenhum outro delta mecânico. Pacote Windows: cinco partes,
3.858.920 bytes Base64, fonte SHA-256
`381569d51d1405e9729e90e899e79028b606d0a422d8782b957d9ec152b5757e`.

Smoke final: **122 checks aprovados**, saída zero. Python focal de Expansão:
três testes aprovados. Transporte focal também passou com os insumos
privados anteriores. Os testes opcionais que o smoke declara pulados por
ausência de fixture não equivalem a cobertura executada. LibreOffice não
foi executado; a validação de cálculo desta entrega é a nativa descrita.
Ambiente: Windows, Python 3.12.12, Node 26.13.0; referências do projeto
continuam Python 3.12/Node 20. Não há nova dependência do produto.

Evidência sanitizada: `isolamento_nomes_validacao_2026-11-07.json`.
Snapshots, código instalado, leituras completas, logs e capturas ficam
somente em `nuvem-b47/saidas/isolamento-windows/`, ignorado pelo Git.

## Limites e continuidade

Somente as duas descartáveis foram alteradas. Oficiais, jogador e PR31
ficaram intactos; PR31 continua em `765e3b24fb49a1ca8c6fd4cfaf16aa6fa6bad943`.
Sem merge, force push, acionadores novos, ampliação de acesso, importação
Office ou execução de construir()/continuar() em ficha preenchida.

A entrega cobre as faixas e cenários descritos; não certifica toda colagem
arbitrária do editor legado nem latência Android. Aplicação futura em outro
destino exige autorização específica, backup/snapshot novo e base exata.
Próxima ação recomendada: revisão com **Sol/Medium**; implementação ou ensaio
adicional com **Sol/High**, sem alterar configurações automaticamente.
