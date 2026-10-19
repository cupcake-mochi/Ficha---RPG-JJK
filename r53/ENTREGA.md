# R53 · entrega na ficha oficial · 19/10/2026

A R53 está aplicada na [ficha oficial — Ficha - Era da Revolução](https://docs.google.com/spreadsheets/d/1u0zWQFVaRTTc_VlrAJsabgAiJ1D4rTYhzG7QQWof1ro/edit). O endereço foi preservado. Este documento substitui os estados históricos de “oficial intacta” e de editor separado.

Os 249 cartões são editáveis no próprio local. MONTAGENS é armazenamento técnico oculto; não existe uma segunda página de edição para o jogador. São 25 abas, sete visíveis. Formas custom e as notas do restante da ficha foram atualizadas. O estado do cartão usa **VÁLIDO**, sem o rótulo técnico “R53 · válida”. Nomes, exemplos e preparações de teste foram retirados.

## Como usar

1. Escolha a Classe disponível, preencha o nome e COMO É no cartão. Use COMO É para alvos, resolução, duração e detalhes narrativos das Melhorias/Restrições.
2. Escolha a Forma. SÓ EM SI significa afetar exclusivamente quem executa; na Forma Toque não concede devolução de pontos.
3. Distribua inteiros nas colunas DANO, CURA e PV TEMP. A conta compartilha o saldo e calcula o resultado.
4. Escolha Melhorias/Restrições no próprio cartão. Os custos e devoluções são calculados; os demais detalhes ficam em COMO É.
5. Nas modalidades de dados fixos, marque a função. Liberação e Técnica Máxima continuam nas seções próprias.
6. **Ao trocar Classe, espere os campos terminarem de atualizar antes de editar.** O Google salva de forma assíncrona; a proteção preserva uma edição pendente e pode pedir que a troca seja repetida. Não há garantia de troca instantânea.

Amparo Fechada mostra “—” nos campos de Cura/PV temporários, bloqueia inserção e mantém os valores guardados para eventual reabertura. Limitações de Classe 0, básicas e máximas continuam valendo.

## Publicação e preservação

- Backup integral nativo criado antes da atualização: [backup da oficial](https://docs.google.com/spreadsheets/d/1lmZ3gF2OGsHe0fa9750vJ6Ym2lHaCJDSmN-EtcULkjQ/edit).
- Migração validada primeiro em cópia nativa da própria oficial, sem importar Excel/Office.
- Snapshot de todas as entradas visíveis relido antes de aplicar: nenhuma alteração concorrente. Só o resíduo de digitação do cartão inicial foi limpo.
- Aplicação incremental de 31.255 pedidos em 45 blocos; preservados arquivo, IDs de abas existentes, imagens, carteira e paleta. CONFIGURAÇÃO mantém a cor fixa.
- INVOCAÇÕES recebeu 120 linhas. Grupos finais conferidos: 53 na FICHA AMALDIÇOADA e 90 em INVOCAÇÕES. Não repetir inserções ou lotes.
- Sete módulos do pacote relidos após nova abertura; 29 módulos antigos conferidos como incorporados e desativados. Manifesto e escopos preservados.
- Carteira/foto, ficha principal, cartões, invocações/nove famílias/autonomia, ficha pessoal, glossário e configuração inspecionados visualmente na oficial. Capturas locais em `r53/saidas/publicacao/` não entram no Git.

## Validação

| Verificação | Resultado |
|---|---|
| Runtime dos cartões diretos | 547 verificações locais |
| Pacote autossuficiente | 7 arquivos, 25 abas, 249 cartões, sem sobras |
| Estrutura da interface | 16.917 verificações locais da rodada anterior |
| Catálogos/contrato/migração | 50 verificações focais e 20 testes unitários da rodada anterior |
| Regras numéricas | 89 cenários, incluindo execução nativa no Google nas etapas anteriores |
| Fórmulas na oficial, após limpeza final | zero erros nas 25 abas |
| Exportação ANALISE12/esquema2 | 18.394 chaves únicas, 5.140 preenchidas, zero aplicações de teste |
| Edição real na oficial | 1 ponto de Dano → 1d8; VÁLIDO; versão preparada salva |
| Limites de Classe | Classe indisponível rejeitada |

As provas da revisão e dos testes custom/Amparo permanecem em `r53/testes/evidencias/`. Elas identificam a cópia e geração em que foram feitas; não devem ser confundidas com testes novos da oficial. A promoção final está registrada em [PUBLICACAO-OFICIAL-R53.json](testes/evidencias/PUBLICACAO-OFICIAL-R53.json).

Geração publicada: `e142593fdc5be157`. Fonte do pacote SHA-256: `2f153f659f714a7e5d16e483832f0bd4914bb93175f0527d97c7d20a03c2b110`.

O ramo de entrega é `codex/publicacao-r53`. Não executar `construir()`/`continuar()` na oficial nem na revisão preenchida. Snapshots e backups de código locais são privados/ignorados. Para manutenção integrada, Sol/High; para conferência focal, Medium.
