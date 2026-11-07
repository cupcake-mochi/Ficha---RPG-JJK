# Forma e função de cinco Melhorias de feitiço · 06/11/2026

Base PR82 `b11c46a`. Os dez casos foram reproduzidos em
`AUDITORIA-FORMA-FUNCAO-2026-11-06.md`. A regra de referência é
a R66 de `JJK---Project@e3058ad29180fdec2efec75b512446c49bf87b3d`.

| Melhoria | Requisito validado | Casos corrigidos |
| --- | --- | --- |
| Escolher | Forma de área | Projétil e Toque |
| Contorno | Forma de área | Projétil e Toque |
| Perseguir | Alvo individual | Cone e Explosão |
| Reserva | Dados efetivos de cura | Só dano e só PV temporários |
| Sugar | Dano inicial efetivo | Só cura e 1d8 reduzido a zero por Toca a Alma |

A validação lê as quatro vagas, informa o requisito no aviso do
cartão e conserva as escolhas, os custos e os créditos de outras
regras. Os 2 pontos próprios da Forma Toque permanecem quando
Escolher ou Contorno está incompatível.

## Entrega incremental

Geração `258490d8ac01ff61`. A comparação de 280.001 posições e
dos metadados de 26 abas encontrou mudanças somente nas 251
fórmulas de FX, em DADOS_R53. EditorR53 e MONTAGENS permanecem
idênticos à PR82.

`preparar_forma_funcao.js` confere a versão do Código e as
fórmulas anteriores em pt_BR e en_US. O plano altera apenas
`userEnteredValue` em FX, substitui somente o bloco dos moldes
de recuperação no Código e fornece a reversão. A aplicação exige
um snapshot atualizado da cópia de destino.

O pacote mantém as cinco partes reservadas, com 4.240.196 bytes
em Base64 e margem de 9.804 bytes. Quando a compactação padrão
ultrapassa a capacidade, o gerador tenta gzip com blocos menores.
O teste do pacote verificou o conteúdo descompactado e sua
integridade.

## Ensaio no Google Sheets

Passaram 18 cenários em cada descartável, Era e Ciclo. Os dez
casos ficaram em REVISAR com o aviso específico. Seis controles
compatíveis ficaram VÁLIDOS, incluindo Sugar com 1d8 restante
após Toca a Alma. Os avisos existentes de Maior fora de área e
da combinação de Concentrada com Duradoura também apareceram.
As duas combinações inválidas com Toque preservaram seu crédito.

As duas fórmulas focais, FX2 e FX41, e as 15 entradas usadas
foram repostas por cópia. A releitura comparou 624 células por
cópia, incluindo 539 posições de MONTAGENS, sem diferenças nem
erros. Ambas voltaram à PR82. Evidências privadas em
`nuvem-b47/saidas/correcao-forma-funcao/`.

Passaram o smoke local, o transporte protegido, a reversão
e a recuperação simulada. A instalação integral e a recuperação
por edição real ficam para o ensaio de instalação desta geração.
