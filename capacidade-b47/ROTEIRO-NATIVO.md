# Roteiro nativo e recuperação B47

A+B foram concluídos no PC em 16/10/2026. Estado e incidentes em
[RETOMADA-PC.md](RETOMADA-PC.md), prova conjunta da descartável em
[VALIDACAO-NATIVA-PC.json](VALIDACAO-NATIVA-PC.json) e revisão migrada em
[REVISAO-NATIVA-PC.json](REVISAO-NATIVA-PC.json). A revisão já está em
ANALISE 10, com 20 GS/manifesto relidos iguais. Não reaplicar os planos
concluídos da descartável ou da revisão; as sequências não são idempotentes.

O procedimento abaixo registra as condições para uma aplicação v9→v10 em
outro estado autorizado, não uma ordem de executar novamente. Confirmar
versão/destino antes de tudo e obter backup/snapshot novos. Nesta retomada,
Drive/Sheets e editor Apps Script no navegador integrado foram usados com
autenticação oficial; os tokens não foram copiados. Os 20 GS seguem f1ff7a6.
C/D, oficial, bot, main e acessos ficaram fora desta entrega.

1. Confirmar destino e projeto vinculado a **cada** planilha com ferramentas
   oficiais. A revisão é **1EdEXzFRL8n21dLb60lxE2wbP4PFxFUiBdw7BiTTkNg0**,
   projeto **1wdZc903PPK6EoGxFG4KcuPNx_plElCBsWxa4lEBgLUlFBD4OrbZPHYnf**.
   A descartável migrada usa o projeto
   `1_SBUy-sPZ7oH4DtmHuV6JqNediJYeE4xxVIiCb0iAxNs0K6wjsoJX6Ks`.
   **Não usar o ID de projeto da revisão ao validar a descartável.**
   Não copiar tokens do PC.
2. Estabelecer janela sem edições, do snapshot final até a releitura conjunta
   de código e planilha. Código salvo e migração não formam uma transação; só
   reabrir a edição depois da validação combinada. Criar backup nativo integral
   da revisão e uma cópia nativa descartável do
   mesmo estado. Guardar IDs, data e metadados. Nunca importar XLSX.
3. Exportar o modelo v9 do commit 4187df3 em checkout isolado e o modelo v10
   do SHA a aplicar. Obter faixas necessárias com:
   `.venv/bin/python capacidade-b47/migracao.py --base <modelo9> --alvo <modelo10> --metadata <metadata.json> --saida <faixas.json>`.
4. Ler todas as faixas em blocos limitados com `userEnteredValue,note` e
   metadados (incluindo grupos, mesclagens e dimensões), preservando os vazios
   cobertos. Formato de snapshot no docstring de `migracao.py`. Registrar o
   backup nativo integral distinto e `captured_at` UTC. Não versionar entradas
   pessoais. Planejar com `--snapshot <snapshot.json>`; o planejador aceita
   descartável por padrão e bloqueia revisão/oficial indevidas.
   `snapshot.py` fatia leituras limitadas à grade existente e normaliza respostas
   CellData tipadas, notas e vazios cobertos, verificando identidade e cobertura.
5. Revisar o manifesto de fontes/chaves e resolver qualquer bloqueio de
   conteúdo preenchido. Não mudar expectativas/guardas para obter aprovação.
   Reler o snapshot imediatamente antes de aplicar; qualquer mudança invalida
   os lotes. Não executar `construir()`/`continuar()` nessa migração.
6. Gerar lotes sem rede em diretório novo:
   `.venv/bin/python capacidade-b47/lotes.py --base <modelo9> --alvo <modelo10> --snapshot <snapshot.json> --saida <diretorio-novo>`.
   O snapshot deve incluir `metadata.spreadsheetId` e `metadata.sheets` com
   `properties`, `rowGroups` e `merges` explícitos; também ler apenas a interseção com a grade nativa existente (colunas auxiliares novas
   são comprovadamente vazias pelos metadados) e cobrir a cauda nativa
   além da última linha do gerador. Conferir os hashes do manifesto antes de
   cada envio. Aplicar primeiro na descartável os lotes pontuais: recolocar cartões na
   geometria reduzida, fórmulas, menus, notas, alturas, grupos e tabelas ocultas;
   preservar todas as entradas/notas mapeadas e o cache CB2:CC10 da progressão.
   Reconstruir ANALISE em quatro colunas e remover reservas excedentes depois
   de auditar referências. Não apagar as abas de estudo nesta entrega.
7. Enviar os **20 .gs** do manifesto correspondente ao SHA testado e remover
   `PecasAnalise2`, `PecasAnalise3`, `PecasAnalise4` do projeto. Conferir hashes
   por releitura integral posterior. Cada .gs deve ter menos de 900.000 bytes.
   O mecanismo integrado `infra-b47/apps_script.py` exige ID explícito,
   snapshot remoto e retirada nominal com `--remover PecasAnalise2 --remover
   PecasAnalise3 --remover PecasAnalise4`. Usar autenticação oficial e releitura
   posterior; não editar o pacote à mão para contornar a guarda. Na retomada,
   começar pelo projeto da descartável já migrada e confirmar novamente o
   estado da planilha/código antes de escrever. Não há necessidade de repetir
   os lotes de planilha já confirmados; sua repetição não é idempotente.
8. Testar nativamente: primeira/última vaga dos cinco grupos; livro/base e
   criação do zero; duplicatas/nomes `* ? ~`; categoria incorreta colada;
   reutilização do mesmo cadastro nas 12 entidades; nove Famílias/autonomia;
   23/11 escolhas do personagem; textos longos nos pares e no último cartão;
   limpeza/restauração das entradas, notas e alturas; ausência de erros;
   igualdade das 7.356 chaves e fontes; cópia funcional sem ativação.
9. Medir carregamento, edição, salvar/reler e construção completa **somente**
   na descartável de construção **12iTELP65DYjBjAY-PiAZ-JvVIyrK7ragsYKRX-vXYsc**
   (conferir novamente o ID). Separar esses tempos dos números em VM/Calc.
10. Só com prova descartável do mesmo modelo/código, snapshot renovado e guardas
    repetir a migração pontual na revisão. O gerador de lotes exige então
    `--prova-descartavel <prova.json>` com resultado OK, destino descartável
    distinto da revisão/oficial e `alvo_sha256` igual ao modelo testado. Reler entradas/ANALISE/scripts e
    registrar diferenças zero e restauração dos cenários. Oficial e bot ficam
    fora desta rodada.

As provas locais em VALIDACAO.json são sintéticas. A antiga
VALIDACAO-NATIVA-PARCIAL.json conserva seu resultado parcial histórico;
a prova conjunta e a aplicação da revisão estão nos arquivos novos acima.
O auditor `conferir-nativo.py` é específico da descartável e nunca promove
seu resultado superior para OK nem valida sozinho código/gatilhos/visual.

O gerador atual evita repetir a formatação da âncora sobre toda a mescla:
controles nativos simples e multilinha mostraram valores, formatos de entrada
e efetivos iguais, também visualmente. Para um primeiro lote com centenas de
merges, `fracionar-inicio.py --origem <lotes> --saida <novo> --limite 50`
isola o cabeçalho e fraciona as mesclagens, verificando todos os hashes e a
sequência integral. Só usar sobre plano novo e guardado do estado intacto.
`coalescer-formatos.py` serve à continuação comprovada de planos antigos:
exige `--a-partir`, não reautoriza o prefixo e só omite repeatCell idêntico ao
updateCells imediatamente anterior, na âncora de uma mescla já declarada.
Os demais pedidos e a ordem são conservados. Não otimizar estado desconhecido.

Recomendação: **GPT-6.1 Sol, High**, para revisão cuidadosa de identidade,
preservação e leitura nativa; nenhuma próxima etapa é iniciada automaticamente.

## Interrupção ou falha parcial

Cada batchUpdate é atômico isoladamente; a sequência não é. A limpeza de
CONFIGURAÇÃO precede a restauração das entradas mapeadas. Uma migração
interrompida permanece parcial até a conferência final; não liberar edição.
Registrar destino, manifesto/hashes, prefixo confirmado, pedidos enviados,
timestamps e erro sem credenciais. Timeout não informa se houve aplicação.

A primeira ação é reler o estado, sem repetir o lote. Se a leitura comprovar
inequivocamente todo o estado pós-lote, registrar confirmação por releitura,
com suas normalizações explícitas, e continuar do seguinte. Se comprovar o
estado anterior, reconstruído do snapshot + prefixo confirmado, registrar a
não aplicação e resolver o gargalo com fracionamento/equivalência previamente
testada. Não inferir sucesso/falha só do retorno ausente nem misturar uma nova
migração desde zero ao prefixo existente. Valores/notas/validações e formatos
das âncoras devem coincidir; interiores de mesclas omitidos pelo Sheets não
são formatos independentes. Registrar a evidência bruta e seu escopo.

Se o estado continuar inconclusivo, houver edição concorrente ou divergência,
parar. Na descartável, usar uma nova cópia nativa do backup e novo snapshot.
Na revisão, guardar o estado parcial e reconciliar alterações antes de
restaurar a região afetada a partir do backup, com guarda e releitura de todas
as entradas/notas. Não sobrescrever trabalho posterior silenciosamente.
Remoções de linhas/grupos nunca devem ser repetidas cegamente.

Na retomada PC, o lote inicial sem efeito foi substituído por plano guardado
fracionado; o 0046 foi confirmado por releitura sem repetição. O 0047, ainda
no estado anterior, teve só formatos redundantes coalescidos após contraprova
nativa; a continuação terminou e recebeu auditoria integral. Ver diário e
limites no checkpoint. Os antigos 102 lotes da descartável não foram reaplicados.
