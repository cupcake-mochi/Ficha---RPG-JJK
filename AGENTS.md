# Trabalho em nuvem — Ciclo Maldito B47

Leia `PLANO-RETOMADA-B47.md`, `PLANO-PARALELO-B47.md` e `NUVEM.md` antes de trabalhar. O ramo de integração é `codex/configuracao-b47`; `main` está atrás. O papel e a autorização dados pelo usuário prevalecem. A preparação de nuvem é comum aos três papéis; não repita sua implementação na frente de infraestrutura.

- Instalação: `bash nuvem-b47/preparar.sh`. Diagnóstico: `.venv/bin/python nuvem-b47/conferir.py`. Validação inicial: `.venv/bin/python nuvem-b47/conferir.py --smoke`.
- As referências necessárias estão versionadas. Não dependa de `/home/mizuki`, `/media`, pastas irmãs, abas ou sessão do PC anterior. `nuvem-b47/saidas/` e `.venv/` não são versionados.
- Os testes antigos têm escopos/versionamentos distintos. Leia `nuvem-b47/TESTES.md`: uma asserção histórica pode precisar de atualização após a redução. Não mudar expectativa só para produzir verde.
- Trabalhos pesados em série por ambiente. Verifique memória antes; no PC original use o limitador já documentado. Não lance a bateria completa por padrão. Smoke não equivale à validação mecânica/visual integral.
- Nunca importar Excel no Google. XLSX aqui é referência/calculadora local. Nunca executar `construir()`/`continuar()` na revisão preenchida/oficial. Migração exige snapshot atual e validação em descartável.
- O Git não fornece conta Google. Não presumir conectores, consentimento ou APIs disponíveis; avançar nas partes independentes e registrar aplicação/testes nativos pendentes. Sem tokens/credenciais no Git.
- Somente o integrador escreve na cópia nativa de revisão e reúne commits em `codex/configuracao-b47`. Claude: `revisao-b47/`; infraestrutura: `infra-b47/`. Sem merge em `main`, force push, bot, ficha oficial ou alterações de acesso sem autorização específica.
- Ao iniciar, em cada checkpoint e ao encerrar, recomendar modelo/esforço para a próxima ação com motivo curto. Não inventar o modelo atual nem alterar configurações automaticamente.
