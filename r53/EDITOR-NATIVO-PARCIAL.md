# Editor pelo cartão — prova nativa parcial,19/10/2026

Somente o primeiro cartão sintético está integrado na cópia de trabalho. A ficha inteira NÃO está concluída. A oficial não foi alterada.

- Cópia: https://docs.google.com/spreadsheets/d/1SHJ4Ms6f8ZmiLzBsvEFfq6iQrcp1zHKXq5sunZfbqJo/edit
- Backup anterior ao editor: https://docs.google.com/spreadsheets/d/1bMWVYnkTqb9oyQFCoJyegIAvnQiKEtgsd1pSxPlVXAU/edit
- AppsScript DA CÓPIA: https://script.google.com/u/0/home/projects/114eAaf8bNcri0J4CdRTcU2BkF8Q2lWYt7Q5lG0MGrveSvxuCtCVUsZ1t/edit

Código.gs recebeu somente as duas ligações para r53Editar_/r53Menu_, comparadas exatamente ao snapshot anterior. EditorR53.gs reduzido28183bytes foi salvo e relido igual. Foi atualizado depois para retorno no cabeçalho e navegação sem corte; versão mais recente28572bytes também relida igual. Arquivos privados em saidas/.

Painel na própria FICHA AMALDIÇOADA: X4:AE38, Voltar=Z7, classe=AE4, funções=Z9:Z11, pontos=AC9:AC11. Cabeçalho/estado na linha4; todos os campos ficam antes das linhas39:51 que a ficha já recolhe. A revisão anterior escondia o Voltar na linha40; foi corrigida. Notas/listas/caixas nativas. O restante das abas mantém o desenho original.

Provas no Google:
- H80 abriu o editor e carregou a versão4,4/2.
- Alterar para3/2 gravou MONTAGENS E10=3 e o resumo virou3d8+2d8, com1 ponto sem uso.
- Trocar Classe para3 recuperou2/2 e9PE no cartão.
- Voltar à Classe4 recuperou3/2 e12PE; Classe3 permaneceu2/2.
- Classe4 foi restituída a4/2,12PE e saldo livre0.
- O primeiro teste de gravação falhou por uma validação antiga da Forma em MONTAGENS E8. As29 regras do armazenamento foram atualizadas para os novos catálogos e a repetição passou. Essa correção foi incluída no preparador; não omiti-la na aplicação integral.

Abertura/edição levam segundos no gatilho simples (abertura18,683s; a falha de validação8,262s). A interfaceSalvar do AppsScript pode ficar visualmente presa mesmo após o arquivo ter sido gravado; conferência em segunda abertura leu o conteúdo correto. Não pedirCtrlS ao usuário só pelo indicador.

Prova final: Voltar no cabeçalho retornou a E64:F64 e recolheu as colunas. Reabrir seleciona AE4 e mostra o painel inteiro, sem corte. MONTAGENS foi ocultada depois desse ciclo. A versão final do piloto foi relida do Apps Script e comparada exatamente à fonte local. Capturas privadas: saidas/editor-no-cartao-final.png e saidas/retorno-ao-cartao.png.

Pendentes: reabertura/cópia funcional do documento, entidades/compactos/máximas, integração de todos os cartões, ponte de Formas custom, migração conservadora, exportação e revisão integral. Os201 contextos atuais omitem36 Liberações e12 Técnicas Máximas de entidades; esses48 cartões precisam de integração própria, com dados e preços da modalidade. A geração de transporte ainda é local: uniformiza estados de Famílias, separa avisos e reutiliza a cópia de linhas. Fonte r53/preparar_nativo.py antiga não é um migrador completo; não recriar as abas já existentes.

Recomendação para seguir: GPT-6.1 Sol/High, pela integração e revisão mecânica. Sem commit/push/publicação.
