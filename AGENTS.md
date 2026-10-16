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
