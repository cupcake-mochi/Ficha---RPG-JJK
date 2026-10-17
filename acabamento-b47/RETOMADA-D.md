# D — checkpoint de continuação · 16/10/2026

O usuário autorizou iniciar D após o fechamento de C e pediu checkpoints frequentes porque restam 2% de uso semanal. Se necessário, continuará no Claude amanhã às 9h. Não há agendamento nem autorização para novos chats/agentes.

## Base preservada

- C concluída e publicada: `21f162076c9b49fab053ce809d418ce00117ed10`, nos ramos `codex/b47-capacidade` e `codex/configuracao-b47`.
- Leia `conteudos-b47/comum/FECHAMENTO-C.md` e suas provas. Não repetir a migração C nem os lotes v10→11.
- Revisão autorizada: `1EdEXzFRL8n21dLb60lxE2wbP4PFxFUiBdw7BiTTkNg0`.
- Apps Script da revisão: `1wdZc903PPK6EoGxFG4KcuPNx_plElCBsWxa4lEBgLUlFBD4OrbZPHYnf` (35 GS e manifesto persistidos e relidos iguais).
- Nova cópia descartável para D: `1j16g_UYCO-SURTioAxZJ0H65SxP1NhMMKjnJdfPlgxE`, criada da revisão após C; 26 abas esperadas. Não foi modificada após a cópia neste checkpoint.
- Evidência privada de abertura: `D:/JJK - Project/B47/evidencias/2026-10-16/d/abertura.json`. Dados do personagem e credenciais não entram no Git.

## Checkpoint: auditoria dos estudos concluída

`AUDITORIA-ESTUDOS.json` e `auditar-estudos.py` registram a auditoria da cópia D: 76 blocos nativos, 26 abas, 63.954 fórmulas, 5.192 validações e 5.342 notas, sem referências entrantes aos quatro estudos e sem erros de fórmula. Referências indiretas foram resolvidas conservadoramente: somente `INDIRECT(SWITCH(...))` cujos resultados/default são faixas literais em abas preservadas. Os 35 scripts canônicos não mencionam os estudos. Os três intervalos nomeados pertencem à carteira. O único `getSheets()` genérico de Codigo.gs percorre proteções, sem depender de uma posição ou estudo.

As leituras completas, com dados privados, estão em `D:/JJK - Project/B47/evidencias/2026-10-16/d/antes/`; plano e metadados na pasta pai. Foram lidas fórmulas, valores efetivos, notas, validações, hyperlinks e textFormatRuns, além dos metadados integrais. Não houve remoção nem alteração de conteúdo. A obtenção dos metadados integrais usou uma atualização idempotente do título existente na cópia.

Próxima ação exata: backup nativo da cópia D, releitura para confirmar o snapshot, remoção apenas dos quatro estudos na cópia D, comparação integral de fórmulas/entradas/notas/validações e resultados preservados, ANALISE com 8.190 chaves. Não remover estudos da revisão antes desse ensaio. Sol/Médio é suficiente para esse procedimento delimitado.

## Próximos blocos

1. Auditar dependências das quatro abas temporárias: `ESTUDO CAMPANHA`, `ESTUDO CUSTOM`, `ESTUDO 3B`, `ESTUDO 3C`. Confirmar nomes/IDs nativamente; procurar fórmulas, validações, intervalos nomeados, gráficos, regras e scripts. A geração canônica de C já produz 22 abas sem estudos; isso sozinho não prova a ausência de dependências na revisão preenchida.
2. Ensaiar a retirada na cópia D e comparar resultados, notas, validações e ANALISE (formato 11, 8.190 chaves). Só então preparar aplicação na revisão, com backup e snapshot/releitura novos.
3. Conferir acabamento nos moldes aprovados: CONFIGURAÇÃO e cadastros, carteira/foto/paleta, grupos, menus, textos longos, recolhimento e 12 entidades. Investigar o fundo/fonte padrão nos espaços novos de CONFIGURAÇÃO, comparando a construção canônica antes de corrigir.
4. Validar cópia funcional, gatilhos, persistência do código e bateria pertinente à versão final. Calc não está instalado neste Windows e `fcntl` não existe aqui: registrar impedimentos reais; não declarar bateria integral aprovada por smoke.
5. Publicar fechamento com provas e pendências explícitas.

## Limites

Preservar escolhas, resultados e endereços das entradas. Não importar XLSX no Google. Nunca executar `construir()`/`continuar()` na revisão preenchida ou oficial. Sem main, force push, bot, ficha oficial, alterações de acesso ou agentes extras. Fontes sincronizadas do projeto são somente leitura. Trabalhos pesados em série, após conferir memória. Novo desenho exige estudo/aprovação; conservar o desenho aprovado evita essa ampliação.

Trabalhar em `codex/b47-capacidade`, publicar checkpoints verificáveis e reunir em `codex/configuracao-b47` somente após conferir a base. Atualizar este arquivo a cada bloco: realizado, prova, próximo passo e estado nativo. Recomendação para a próxima ação: Sol/Médio, pois a auditoria inicial é delimitada e preserva os moldes aprovados.
