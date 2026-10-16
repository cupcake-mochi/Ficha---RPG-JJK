# Aplicação pendente da capacidade B47

Esta rodada confirmou leitura real do Sheets pelo conector em 16/10/2026.
Leu os quatro catálogos crus da revisão: nenhum campo diferente dos padrões
vazios. Não é snapshot integral nem autorização para reutilizar essa leitura
numa sessão futura. Nenhuma escrita nativa foi realizada.

A sessão não expõe ferramenta Apps Script (leitura, atualização ou execução),
credenciais OAuth de CLI nem navegador. Acesso ao Drive/Sheets não garante
acesso ao projeto Apps Script. Sem salvar/reler código, não atualizar a revisão:
o gatilho antigo conservaria as geometrias e o contrato anteriores.

1. Confirmar destino **1EdEXzFRL8n21dLb60lxE2wbP4PFxFUiBdw7BiTTkNg0**,
   projeto **1wdZc903PPK6EoGxFG4KcuPNx_plElCBsWxa4lEBgLUlFBD4OrbZPHYnf** e
   ferramentas oficiais disponíveis; não copiar tokens do PC.
2. Criar backup nativo integral da revisão e uma cópia nativa descartável do
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
   O mecanismo de envio preparado por `infra-b47/`, quando recebido/revisado,
   deve exigir ID explícito, autenticação oficial e verificação posterior.
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

As provas locais de migração são sintéticas; não comprovam os passos 2–10.
Recomendação para a aplicação: GPT-6.1 Sol, High, por envolver identidade de
campos, preservação da revisão e conferência nativa.

## Interrupção ou falha parcial

Cada batchUpdate é atômico isoladamente; a sequência de lotes não é. A limpeza
de CONFIGURAÇÃO acontece antes da restauração das entradas mapeadas. Portanto,
qualquer falha/timeout deixa a cópia marcada como **migração parcial**, nunca
pronta para uso. Registrar destino, manifesto/hashes, índice do último lote com
resposta confirmada, pedidos enviados e erro sem credenciais. Em timeout, ler
o estado atual para descobrir se o lote foi aplicado antes de repetir algo.

Não pular para o próximo lote nem reaplicar cegamente os anteriores: remoção de
linhas e grupos não é idempotente. Na descartável, recomeçar de uma nova cópia
nativa do backup integral e gerar outro snapshot/plano/lotes. Na revisão, parar
a edição, obter snapshot do estado parcial e verificar ausência de edições
posteriores desconhecidas. Restaurar a região afetada a partir do backup integral
com guarda e releitura de **todas** as entradas/notas antes de planejar outra
tentativa; nunca sobrescrever alterações concorrentes silenciosamente. Se houver
editação concorrente, reconciliar primeiro. A cópia parcialmente migrada não é
evidência de migração aprovada. O manifesto registra expressamente a ausência de
atomicidade entre lotes. Nenhuma falha parcial ocorreu nesta rodada, que não
executou escritas nativas.
