# Técnica e Famílias · 28/10/2026

Etapa 7 parcial da Carteira viva. PR 31 em rascunho, sem instalação ou liberação
de criação. Nenhuma ficha oficial ou de jogador foi alterada.

## Código e base

Main `ef361ccdf7a0210781176e3c42d318cde147553d` incorporada pelo merge
`a72adc0a7e56b4c4c7862b35e5d69a094108533a`. PRs 41–43 trazem XP manual,
marcas de XP congelado em missões, registro do backup 13 das oficiais e
atualização do smoke. A instalação das oficiais foi feita por outro trabalho.
Não reaplicada aqui. O inicializador financeiro já remove as notas das missões;
duas regressões novas provam a compatibilidade com o XP congelado.

Novos perfis fixos em formacao.gs: 11 entradas de técnica e 19 de Famílias.
Contrato gerado do fonte público com o overlay R53Cartoes1, 84 entradas/guardas
no total. Nove Famílias do livro voltam a Neutra; dez custom recuperam a fórmula
original, preservando as definições da mesa. Campos derivados não são apagados.
Os quatro contratos anteriores e a assinatura financeira v1 permanecem iguais.

## Testes locais

782 cenários aprovados: 101 financeiro, 82 progressão, 78 identidade,
243 pessoal e 278 formação. São 90 cenários adicionais (88 formação e dois
XP congelado). Regressão upstream xp_atualizar.js: 87 verificações aprovadas.
Guardas, variantes exatas, falha antes/depois das escritas, retomada, concorrência,
notas, matriz parcial e hashes fixos dos contratos anteriores estão cobertos.
Nenhuma expectativa antiga foi afrouxada para passar.

## Google Sheets

Leitura delimitada das duas oficiais, depois dos metadados: 84 entradas/guardas
em cada documento, zero divergências. Nenhuma escrita nas oficiais.

Uma cópia privada e descartável da Era recebeu valores/notas fictícios nos
alvos e duas definições de Família: “Família QA *” e “Família QA 1”. O asterisco
não colidiu com o outro nome. A restauração foi uma **projeção dos efeitos pela
Sheets API**, não a execução dos diários Apps Script ou do OAuth das Guias.

Primeiro envio com fórmulas do fonte separadas por vírgula produziu erro de
análise na API. O segundo envio usou a variante exata com ponto e vírgula já
observada nas oficiais e aceita pelo contrato. Não houve mudança de expressão,
referência ou regra para contornar erro. A execução real do perfil via Apps
Script, inclusive a aceitação de fórmulas pelo setValues, permanece pendente.

Resultado final:

- 30 entradas/notas restauradas; nove estados do livro Neutra.
- Duas custom válidas Neutra; oito posições sem definição vazias.
- 2.048 posições inspecionadas, 8.132 comparações de conteúdo/notas/validação/
  formato preservados sem diferença; os 30 alvos só excluídos da comparação
  de conteúdo e nota, nunca de validação/formato.
- Nenhum effectiveValue com erro nas faixas inspecionadas.
- Catálogos e configurações fictícias preservados; conferência visual do bloco.

Faixas: FICHA AMALDIÇOADA D9:T84; CONFIGURAÇÃO C38:H88 e CJ13:CX20;
DADOS_CRIACAO A1:O22. Não é uma comparação integral da ficha, certificação de
criação ou prova de desempenho. Não executa eventos, sincronização de cartões,
amparo ou recuperação. A cópia foi movida para a lixeira ao terminar.
Não salvar snapshots, dados pessoais, tokens ou IDs privados no repositório.

## Continuação

Próximo bloco: inventário/equipamento, com entradas ancoradas no produtor e
preservação dos catálogos. Também faltam campos pessoais restantes da CARTEIRA,
entidades/cartões/MONTAGENS, imagens, caches/recuperações, orquestração e
conferência final, automações/treinos iniciais, novo responsável, caminho
executável com drive.file e ensaio nativo completo dos perfis. Não reiniciar
fases nem apagar diários para contornar mudança de estado.

Criação incondicionalmente bloqueada; protótipos fora do pacote/bot. Sem merge
em main, deploy, Gateway, modelo pago, ampliação de escopo ou acesso novo.
Próxima implementação GPT-6 Astra / Alto; revisão focal Médio.

## Correção do preparo do CI

O run 40681047195 no código a92cba8 passou os 782 cenários, mas falhou em dois
testes recém-incluídos pela main: abertura_salario e missoes_sem_registros.
Ambos usam git show de bases históricas que faltavam no checkout raso.
O workflow passa a buscar somente os dois commits fixos 9536746 e 57117fb,
com SHA completo e depth=1, antes do smoke. Nenhuma expectativa/comparação
foi removida ou alterada. O run duplicado 40681039147 foi cancelado.
