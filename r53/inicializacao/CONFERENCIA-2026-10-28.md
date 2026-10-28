# Leitura conjunta dos perfis

28/10/2026 · PR31 · protótipo fora do pacote/bot. Main produtor ef361cc e bot
main de42447 reconferidas. Criação continua bloqueada; não instalado no Google.

## Interseções e defeito corrigido

`mapear_intersecoes.js` enumera endereços de escrita e guardas declaradas das
fontes públicas; `INTERSECOES-2026-10-28.json` guarda o resultado reproduzível.
São 599 perfis, 10.178 operações celulares e 17.316 registros de guardas,
com as faixas financeiras medidas até o limite físico permitido de 5.000 linhas.
Não avalia contas: nível/Amparo são resultados controlados só para enumerar
endereços, que não variam com esses resultados.

Não encontrou escritas cruzadas entre perfis na mesma camada (conteúdo, nota
ou validação). Encontrou 83 interseções diretas entre escritas e guardas:

- 2: fotos/espelho lidos pela identidade.
- 72: fotos lidas pelos seis grupos de cada uma das 12 entidades.
- 1: progressão escreve o nível protegido originalmente pelo financeiro.
- 8: quatro pares de campos dos cartões Classe 0 compartilham a linha seguinte.

As duas primeiras exigem fotos antes desses perfis. O nível muda de propósito,
mas não permite afrouxar a conferência financeira antiga. A última revelou um
defeito real na sequência: Classe 0.1 podia recusar os dados preenchidos de
Classe 0.2, e assim por diante. A sequência passa a trabalhar esses cinco
cartões de baixo para cima, mantendo as guardas e contratos dos cartões iguais.
O uso avulso de um cartão mantém sua dependência do vizinho; não há bypass.

A regressão preenche os cinco cartões e reproduz a recusa na ordem antiga.
A ordem nova inicializa todos e a leitura posterior confere seus recibos e
valores, sem escrever novamente. Os testes individuais anteriores deixavam
vizinhos nos defaults e não representavam esse conjunto preenchido.

O mapa é direto e parcial: não enumera toda leitura dinâmica, propriedades,
validações ou dependências indiretas das fórmulas/eventos. Não certifica todas
as configurações nem ausência de outras interações. A regressão fixa contagens,
resultado e ordem; mudanças no fonte exigem revisar o mapa, não mudar expectativa
só para passar. Reproduzir com `node r53/inicializacao/mapear_intersecoes.js`.

## Sequência v2

O coordenador usa nova chave `r53_nova_ficha_sequencia_v2`, versão 2. Não adota,
migra ou apaga diários de sequência v1/fases avulsas: usar outra cópia nova.
Nenhuma sequência v1 foi executada nativamente por esta tarefa.
Os formatos/assinaturas dos perfis individuais continuam iguais.

Antes da prévia financeira, salva um hash adicional das mesmas fórmulas e
regra de campanha protegidas, excluindo somente o nível que a progressão vai
alterar. A guarda v1 completa continua incluindo o nível e recusando a mudança.
`r53NovaFinGuardas_` apenas extrai a lista anterior; `r53NovaFinPreservados_`
continua retornando o hash exato dessa lista. A projeção não cria exceções a
fórmulas desconhecidas, regras diferentes ou pós-estados numéricos errados.

Cada filho concluído também entra numa cadeia de hashes do registro exato,
com contador próprio, no mesmo checkpoint que avança a fase. Queda antes/depois
do checkpoint não conta o filho duas vezes. As chaves são fixadas pelo produtor
e conferidas contra as fábricas dos 599 perfis. Nunca aceita uma lista de chaves
ou endereços enviada pelo navegador.

No fechamento da sequência, a cadeia completa é reconstruída e comparada.
Só então se salva o hash de um retrato ordenado dos registros exatos. A leitura
usa esse retrato: detecta mudanças sem reconstruir centenas de elos a cada
perfil. O retrato não contém nem retorna o conteúdo dos registros.

Isso vincula os registros à execução que os concluiu; não transforma checksum
em autenticação. Alvo/modelo/código/responsável e isolamento da cópia continuam
obrigações do integrador confiável. A cadeia cobre perfis de escrita, não os
inventários históricos de imagens.

## Conferência sem limpeza

`conferencia.gs` fornece `r53NovaFichaConferenciaPrevia` e
`r53NovaFichaConferenciaLer`, exigindo contexto confiável e assinatura da sequência
v2 concluída. Trabalha em um perfil por chamada, sob a trava do documento.
Não chama Aplicar, não limpa células/imagens/propriedades e não executa eventos.
Só grava o próprio checkpoint de leitura, usando a quota compartilhada anterior.

Antes e depois da leitura, reconfere o coordenador e o retrato dos registros,
com uma leitura em bloco de DocumentProperties, sem retornar seu conteúdo.
Registro removido, alterado, de outra operação, excessivo, incompleto ou com
integridade/layout incompatíveis é recusado. Memórias/recuperações reaparecidas
também impedem a conferência, inclusive em uma repetição terminal.

A leitura do perfil confere diário detalhado ou recibo, guardas atuais e todos
os pós-estados. Compara também o estado de fábrica calculado pela operação,
não somente o resultado gravado no recibo. Um recibo não justifica preservar
conteúdo herdado. Valores, fórmulas, notas e validações são conferidos conforme
o tipo original; equivalências exatas anteriores continuam em vigor.

Para o financeiro, usa a projeção capturada e confere os pós-estados financeiros;
a progressão confere nível/base contra a regra atual protegida e seu diário.
Não reexecuta financeiro depois de mudar nível. Não altera a guarda antiga para
fazer a leitura passar. Os outros perfis conservam a comparação integral das
suas próprias guardas e a verificação antes/depois da leitura.

Falha de leitura ou checkpoint não avança para outro perfil. Prazo esgotado
retorna pendente sem registrar a página como lida. Checkpoint contém somente
hashes e contadores, sem valores/notas/URLs/nomes pessoais. Repetição terminal
retorna o resultado histórico; não recomeça nem revalida todas as células.

## Validação e limites

Comandos locais:

```
node r53/testes/inicializacao_financeiro.js
node r53/testes/inicializacao_sequencia.js
node r53/testes/inicializacao_conferencia.js
```

101 cenários financeiros e 67 da sequência passaram localmente. Sequência v2:
maior coordenador 1.773 bytes com 32 recuperações. 43 cenários novos da leitura
passaram, incluindo os 599 slots; maior checkpoint 354 bytes. CI completo em
fechamento; total previsto de inicialização 2.936 (2.893 anteriores + 43). A bateria inclui
599 slots de leitura com perfis pequenos controlados e registro real do
executor; isso não é aplicação dos 599 perfis reais sobre uma mesma ficha.
Há casos separados de financeiro/progressão e dos cinco Classe 0 usando os
perfis reais, sem simular que a VM calcula fórmulas do Sheets.

O limite temporal continua explícito: uma célula editada após sua página ser
lida pode escapar da rodada. O teste demonstra isso e exige os indicadores
`consistenciaTemporalVerificada`, `imagensAtuaisConferidas`,
`conferenciaConjuntaConcluida` e `criacaoDisponivel` falsos, mesmo ao terminar.
Alteração posterior de registro é detectável pela cadeia; alteração posterior
da célula sem mexer no registro ainda exige uma solução de consistência temporal.
A trava não impede edição humana; o integrador ainda precisa isolar o destino.

Este é um leitor dos pós-estados conhecidos, não um selo final da ficha toda.
Faltam imagens atuais/consistência/arte, conferência de preservação global,
orçamento conjunto nativo, automações/treinos/notas vivas, novo responsável e
integração/prova completa drive.file. Não liberar cadastro por causa de um CI verde.
Sem Google/Discord, oficial/jogador, acesso novo, modelo pago, merge/deploy/Gateway.
Consumidor PR84 só documentação. Sol Alto para integrar; revisão Médio.
