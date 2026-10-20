# Extensão vigente · emissão e salários · 20/10/2026

Terceira rodada: a abertura simples não revisa notas/paleta nem apura salários. O novo `salarioAposAbrir` chama `revisarAbertura` com orçamento instalável; o diário e a edição são mantidos. A reemissão só muda o ciclo aberto, sem varrer missões ou tocar nos créditos. A previsão por fórmula compara `INT` das datas para incluir missões do próprio dia. `salarios/corrigir_abertura.js` atualiza o carregador antigo por âncoras estritas após validar o hash original; os cinco catálogos não são regravados. A fonte integral já contém as mesmas correções. Leia os tempos e a evidência vigente em `salarios/VALIDACAO.json`; as falhas de abertura da rodada anterior são históricas.

Leia `salarios/README.md` e `salarios/VALIDACAO.json`. A extensão salarial usa CONFIGURAÇÃO K35:Q95, com histórico recente em K78:Q95 e checkbox de emissão em CARTEIRA!AT3. SALÁRIOS e DADOS_SALARIOS ficam ocultas. O86 continua livre para gastos/fórmulas; W86 soma os créditos do histórico. A publicação incremental anexa Salarios.gs ao Codigo.gs antigo, preservando o pacote R53; a geração integral publica Salarios.gs separado. Nunca instalar nas duas posições ao mesmo tempo.

O instalador no Google deu timeout após criar as duas abas ainda vazias. A retomada de 132 pedidos foi validada em segunda cópia e aplicada na oficial, reutilizando as abas. Não repetir o lote `salarios/saidas/retomada-pedidos.json`. Mudanças futuras exigem snapshot novo e ensaio em cópia. Acionadores diário e de edição estão vinculados à oficial; cópias precisam de ativação própria. Não abrir agentes extras nem mesclar em main sem autorização específica. Para manutenção, Sol/High; conferência focal, Medium.

# Estado vigente R53 · publicação de 19/10/2026

A autorização mais recente do usuário incluiu publicar a R53 na ficha oficial e salvar o projeto no Git. Essa aplicação está concluída; leia `r53/ENTREGA.md` e `r53/testes/evidencias/PUBLICACAO-OFICIAL-R53.json`. O ramo de entrega é `codex/publicacao-r53`, derivado de `ccbd053`. Os planos paralelos B47 abaixo são históricos e não reabrem trabalho.

Não repetir os 45 blocos de promoção nem as inserções: INVOCAÇÕES já tem 1394 linhas. Nunca executar construir()/continuar() na oficial/revisão preenchida, nem importar Excel/Office. Fazer snapshot e validar em cópia para nova migração. Não abrir agentes/chats extras. Sem ampliar acesso ou versionar snapshots/credenciais. Não mesclar em main sem autorização específica. Modelo recomendado para manutenção integrada: Sol/High; conferência focal: Medium.

## Histórico B47

# Trabalho em nuvem — Ciclo Maldito B47

## Divisão vigente de C+D

A+B estão concluídos em `dce00ab8a244f53218c978293d10c5c1894b1ef8`. Para a continuação, leia [PLANO-PARALELO-CD-B47.md](PLANO-PARALELO-CD-B47.md) e use os novos prompts em `prompts-b47/cd/`, listados em [PROMPT-WORK-B47.md](PROMPT-WORK-B47.md). A publicação do planejamento não inicia C/D; o uso de cada prompt autoriza a frente correspondente.

- Integrador: conteúdos comuns (Tipos de dano/Condições), núcleo, contrato, integração, Google e D. Ramo de tarefa `codex/b47-capacidade`; integração em `codex/configuracao-b47`.
- Outro Codex: Formas (personagem e entidades), Aptidões/Bênçãos e Talentos do personagem. Edição direta somente em `conteudos-b47/personagem/`; mudanças no núcleo são patches nessa pasta.
- Claude: implementação de Tipos/Talentos de entidade e revisão cruzada de personagem. Edição direta somente em `revisao-b47/cd-entidades/`; mudanças no núcleo são patches nessa pasta. Este papel substitui o de revisor exclusivo de A+B.
- Só o integrador aplica os patches ao núcleo, gera/publica GS, escreve no Google e atualiza o ramo de integração. Frentes auxiliares entregam código/testes isolados, não uma segunda geração de produção.
- Três chats no total; não abrir outros chats/agentes nem enviar mensagens automaticamente. Preservar os demais limites abaixo. `PLANO-PARALELO-B47.md` e os prompts fora de `prompts-b47/cd/` descrevem a divisão histórica de A+B.

## Preparação e limites comuns

Leia `PLANO-RETOMADA-B47.md`, o plano paralelo vigente indicado acima e `NUVEM.md` antes de trabalhar. O ramo de integração é `codex/configuracao-b47`; `main` está atrás. O papel e a autorização dados pelo usuário prevalecem. A preparação de nuvem já existe; não refazer o bootstrap.

- Instalação: `bash nuvem-b47/preparar.sh`. Diagnóstico: `.venv/bin/python nuvem-b47/conferir.py`. Validação inicial: `.venv/bin/python nuvem-b47/conferir.py --smoke`.
- As referências necessárias estão versionadas. Não dependa de `/home/mizuki`, `/media`, pastas irmãs, abas ou sessão do PC anterior. `nuvem-b47/saidas/` e `.venv/` não são versionados.
- Os testes antigos têm escopos/versionamentos distintos. Leia `nuvem-b47/TESTES.md`: uma asserção histórica pode precisar de atualização após a redução. Não mudar expectativa só para produzir verde.
- Trabalhos pesados em série por ambiente. Verifique memória antes; no PC original use o limitador já documentado. Não lance a bateria completa por padrão. Smoke não equivale à validação mecânica/visual integral.
- Nunca importar Excel no Google. XLSX aqui é referência/calculadora local. Nunca executar `construir()`/`continuar()` na revisão preenchida/oficial. Migração exige snapshot atual e validação em descartável.
- O Git não fornece conta Google. Não presumir conectores, consentimento ou APIs disponíveis; avançar nas partes independentes e registrar aplicação/testes nativos pendentes. Sem tokens/credenciais no Git.
- Somente o integrador escreve na cópia nativa de revisão e reúne commits em `codex/configuracao-b47`. Respeitar as áreas da divisão vigente; `infra-b47/` permanece como infraestrutura de A+B já integrada. Sem merge em `main`, force push, bot, ficha oficial ou alterações de acesso sem autorização específica.
- Ao iniciar, em cada checkpoint e ao encerrar, recomendar modelo/esforço para a próxima ação com motivo curto. Não inventar o modelo atual nem alterar configurações automaticamente.
