# Sequência dos perfis

28/10/2026 · PR 31 · protótipo fora do pacote/bot. Não instalado.
Main produtor ef361cc e bot main de42447 reconferidas sem novidade.
Criação continua bloqueada, inclusive após percorrer todas as fases.

## Problema tratado

Retomar sempre do financeiro é incorreto: a progressão muda o nível que a
conferência financeira inicial protegia. A mesma operação deve continuar no
filho pendente ou na próxima fase, sem refazer fases já concluídas. Não foi
relaxada a guarda financeira para permitir recomeçar do zero.

`sequencia.gs` fornece `r53NovaFichaSequenciaPrevia/Aplicar`. É código interno
do produtor, sem menu, endpoint, emissão, criação de arquivo ou integração de
escrita com a Carteira. Contexto vem de integrador confiável; flags e checksum
não autenticam o navegador nem comprovam que o destino é uma cópia nova.
A futura integração ainda precisa provar alvo/modelo/código/responsável.

## Ordem fixa

601 fases, mais as recuperações conhecidas presentes no início (máximo 32):

1. Inventário de imagens antes; foto/espelho.
2. Financeiro, progressão e identidade textual.
3. Escolhas, dez perfis de formação e condições.
4. 73 perfis de entidades.
5. 249 cartões em MONTAGENS, depois 249 cartões visíveis.
6. 11 grupos de memórias e recuperações capturadas no início.
7. Recursos atuais e inventário de imagens depois.

São 599 perfis de escrita e duas inspeções. Não recebe listas de endereços,
ordem, IDs de perfis ou planos do navegador. Configuração/catálogos da mesa
continuam fora dos alvos; modelo do servidor é a ficha do sistema com essas
configurações, não personagem pronto para herdar.

Fotos precedem as guardas de identidade/entidades. Memórias ficam após cartões
e MONTAGENS para não ressuscitar versões anteriores. Recursos só são ligados
aos máximos depois das escolhas; cálculo real e notas vivas ainda exigem
ativação/conferência posterior. A lista de recuperações fica no diário mesmo
depois de serem apagadas, sem perder fases na retomada. Recuperação nova ou
memória com nome desconhecido interrompe, sem exclusão heurística.

## Retomada e limites

Uma chamada prepara a prévia de um único filho OU aplica esse filho, nunca
as duas leituras caras juntas. Assinatura do filho é salva antes da aplicação.
Somente após o filho concluir o cursor avança. Queda depois do filho e antes
do cursor retoma o mesmo filho com sua assinatura; seu diário/recibo confirma
o estado sem repetir a limpeza. Queda após o cursor não volta ao filho.

A trava do documento cobre leitura do coordenador, filho e atualização do
cursor. Extraiu-se apenas o miolo dos executores financeiro e de imagens para
uso sob a trava já obtida; os wrappers públicos continuam adquirindo/soltando
a mesma trava. Formatos, assinaturas, guardas e orçamento inicial dos perfis
anteriores foram preservados. Cache volátil é invalidado antes/depois.

Cada aplicação de filho conserva até quatro passos de escrita (não quatro
chamadas Google totais), orçamento de 210 s/180 s para imagens e quota anterior.
A preparação usa uma chamada separada; não há garantia de prazo do serviço
Google nem medição nativa desta sequência. Não executa todas as fases numa
chamada e não recomeça pelo primeiro domínio a cada tentativa.

O coordenador guarda vínculo em hash, versões/contratos, assinatura da inspeção
inicial, cursor, assinatura ativa e IDs técnicos das recuperações. Não guarda
valores, notas, URLs, nomes pessoais ou nome privado de modelo. Recuperações
são identificadores internos; nunca vão ao retorno público. Criação recusa
qualquer diário de inicialização preexistente, inclusive outro formato, em vez
de adotar fases avulsas como prova. Não apagar registros para reiniciar.

O contexto e contratos são reconferidos em cada chamada. Mudanças de estrutura
antes do primeiro inventário invalidam a prévia. Se mudar semântica do executor
sem alterar contratos, subir a versão da sequência antes de retomar código de
outra geração; a futura instalação também precisa conferir a revisão do código.

As inspeções interrompem a sequência em caso de imagens fora das fotos,
objetos indeterminados, decoração ausente, sobreposição ou desenho; a inspeção
final também exige não restar imagem nas caixas de foto. Isso não autentica
pixels de decoração marcada nem torna a leitura um snapshot consistente.
Sem limpeza automática de decoração custom ou imagens fora das âncoras.

## Validação e o que não está pronto

67 cenários novos locais passaram; maior coordenador 1.553 bytes com 32
recuperações. Consultar o CI completo no fechamento.
A bateria usa serviços simulados e cobre os 601 slots do protocolo com perfis
pequenos, quedas antes/depois de cada gravação, assinatura ativa, cursor,
limites, prazo, recuperação, quota, privacidade e travamento de arte. Um teste
separado instancia os 599 perfis reais para conferir o manifesto/IDs/diários.
Outro usa os perfis reais financeiro e progressão: nível 29 vira 10/base 3.700,
retomada não refaz financeiro e sua guarda antiga continua recusando o novo nível.

Os 601 slots sintéticos não são uma inicialização dos 599 perfis reais sobre
uma mesma ficha, nem prova de quota/latência Google. O retorno terminal diz
`fasesPercorridas=true`, `conferenciaConjuntaConcluida=false`,
`criacaoDisponivel=false` e lista pendências. Não chama o arquivo de pronto.

Ainda falta conferir o conjunto atual, incluindo alterações em fases anteriores,
resolver consistência temporal/arte, medir orçamento global, executar automações
conhecidas/treinos/notas vivas, atribuir novo responsável e integrar/provar criação
com drive.file numa descartável. A sequência não verifica novamente todos os
filhos ao terminar: o fechamento conjunto é uma fase posterior obrigatória.
Não executar editor/abrir ao jogador entre fases; trava não impede edição humana.

Sem leitura/escrita Google nesta rodada, modelo pago, merge, deploy, Gateway,
acesso novo ou alteração em oficial/jogador. Consumidor PR84 recebe só docs.
GPT-6.1 Sol / Alto para integração; Médio para revisão focal.
