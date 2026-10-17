Retomada do B47 depois da Fila D — Ciclo Maldito. Você é o integrador e continua de onde o chat anterior parou, sem refazer nada que já está provado.

Repositório: https://github.com/cupcake-mochi/Ficha---RPG-JJK, branch `main` (igual a `codex/configuracao-b47`). Leia nesta ordem: o bloco do topo de `acabamento-b47/RETOMADA-D.md` (parada de 17/10, noite), `AGENTS.md`, `PENDENCIAS.md` e `nuvem-b47/TESTES.md`.

IDs:
- Revisão (B47 completa, com dados do personagem): 1EdEXzFRL8n21dLb60lxE2wbP4PFxFUiBdw7BiTTkNg0 · Apps Script 1wdZc903PPK6EoGxFG4KcuPNx_plElCBsWxa4lEBgLUlFBD4OrbZPHYnf
- Descartável de construção (montada do zero com o código final): 14Ad8e5hUECLimCFuilEGSIxrhv0IWpDUEjEBR4N8N-Q
- Cópia de teste da revisão: 1_1oBYdoci0j-B5LSfYp6UPLpnQB5vNxEOJafx-FRHqw
- Ficha oficial (ainda B46): 1u0zWQFVaRTTc_VlrAJsabgAiJ1D4rTYhzG7QQWof1ro · backup de 17/10: 117rWwlUgRHTthjPpTqS37TV_SVgpFu_-hjtQyqXPpJw

Antes de qualquer coisa, diga quais ferramentas você tem de fato (Git, leitura/escrita no Google Sheets, editor do Apps Script, LibreOffice local). Sem uma delas, avance no que não depende dela e registre o que ficou pendente.

Faça, nesta ordem:

1. **Item 3 — manutenção dos testes antigos.** A tabela "Item 3" do `RETOMADA-D.md` diz o estado de cada teste. Rode **um de cada vez** (LibreOffice disputa CPU e estoura o `timeout`), conferindo antes que não há `soffice.bin` vivo. Comece pelos já corrigidos e não rodados (`regressao-ficha-pessoal.py`, `regressao-configuracao.py`, `regressao-progressao.py`, `regressao-familias-invocacao.py`). Depois `regressao-campanha.py` e `regressao-custom.py` (imprima a lista inteira de diferenças antes de excluir qualquer coisa; só sai o que for mudança aprovada em C, como os rótulos das Famílias), e `regressao-amaldicoada.py`. **Não troque expectativa só para ficar verde**: para cada falha, prove pelo livro (`manual.txt`), pelo gerador ou pela regra aprovada se o teste está velho ou se a ficha tem defeito. Em especial, `regressao-custom.py` "base Latente permite marcante publicada" pode ser defeito real.
2. **Item 2 — medidas e perfil de lentidão** (`PLANO-RETOMADA-B47.md`, itens abertos de A/B): linhas, fórmulas, tamanho dos arquivos, tempo de abrir/editar/construir, separando medida nativa de VM.
3. **Ficha oficial** — só com o usuário presente na sessão, pelo `acabamento-b47/ROTEIRO-OFICIAL-B47.md` (a autorização para rodar `construir()` na oficial depois do backup está registrada lá). Combine um horário sem jogadores copiando a ficha.
4. Atualize `RETOMADA-D.md` e `PENDENCIAS.md` a cada etapa, com commit e push em `codex/configuracao-b47` e fast-forward em `main`.

Restrições: nunca `construir()`/`continuar()` na revisão preenchida; na oficial só pelo roteiro, com o usuário presente. Não importar XLSX no Google. Não mexer no bot nem em permissões; não conceder autorização nova sem perguntar. Sem force-push. Dados do personagem ficam fora do Git. Ao publicar código no Apps Script, confira o hash do arquivo antes de salvar, espere o salvamento terminar e releia os 36 arquivos depois de recarregar.
