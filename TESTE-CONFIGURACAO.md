# B47 · roteiro nativo de bônus e mudanças

[Cópia de revisão](https://docs.google.com/spreadsheets/d/1EdEXzFRL8n21dLb60lxE2wbP4PFxFUiBdw7BiTTkNg0/edit?gid=47001#gid=47001), feita diretamente da ficha do servidor, sem importar Excel. A oficial permanece intacta. As três primeiras linhas trazem exemplos; somente o bônus de Defesa está ligado. O Buff/Debuff de Defesa foi restaurado para 0.

| Passo | Ação | Resultado esperado |
|---|---|---|
| 1 | Abra a CARTEIRA e as demais abas visíveis. | Moldura da foto, imagens, larguras, caixas, agrupamentos e seletor de paleta preservados. |
| 2 | Na CONFIGURAÇÃO, desligue B11. | Defesa volta para 11 nesta cópia em branco. |
| 3 | Ligue B11 e escreva 3 no Buff/Debuff de Defesa (FICHA!L59). | Defesa 16: 11 + 3 + 2. |
| 4 | Ligue B12, a troca de Defesa por 0. | Defesa 0, mesmo com o bônus e o Buff/Debuff ligados. |
| 5 | Crie uma segunda troca ligada para Defesa. | Aviso de conflito; Defesa fica em #N/A, sem escolher uma troca arbitrariamente. |
| 6 | Desligue a segunda troca e escreva `zero` no valor da primeira. | Aviso de entrada inválida; o texto não é tratado como 0. |
| 7 | Edite uma caixa calculada da CONFIGURAÇÃO, por exemplo F46. | O gatilho simples devolve a fórmula. Entradas B:G continuam editáveis. |
| 8 | Troque a paleta na CARTEIRA. | A CONFIGURAÇÃO permanece em Mizuki Escuro; a ANALISE permanece neutra. A troca das demais abas continua conforme a ficha já fazia. |
| 9 | Exiba a ANALISE pelo menu de abas. | 5.274 chaves únicas, formato 4: 5.156 anteriores e 118 de campanha, XP, vida e sequelas. Oculte-a novamente depois. |
| 10 | Restaure os exemplos e o Buff/Debuff para 0. | Só B11 ligado; Defesa 13; sem aviso de efeito. |

Somar aceita valores negativos e decimais. Trocar por fixa o valor final da caixa. Duas trocas ligadas da mesma caixa são conflito; uma linha desligada não afeta a conta.

Uma caixa de seleção apagada também conta como desligada. Um texto estranho no lugar do estado lógico continua gerando aviso, para não ser tratado como uma marcação válida.

## Contrato com o bot

Cada efeito tem seis chaves: `efeito.N.ligado`, `.caixa`, `.como`, `.valor`, `.tipo_de_fonte`, `.fonte`, com N de 1 a 30. A parte é `configuração`. Os diagnósticos são `aviso.efeito.N` e `aviso.efeito_caixa.<caixa>`.

A ANALISE 2 já está no `main` do gerador e nas cópias de validação do bot. A base do servidor consultada nesta rodada ainda tinha formato 1 e 2.650 campos. A cópia de revisão preserva sua apresentação e recebe o contrato mais recente com efeitos e regras de campanha, formato 4. O bot precisa reconhecer e conferir esses efeitos antes de esta etapa ser publicada para jogadores.

Conteúdo custom e automatização das exceções de Origem continuam em etapas separadas.

## Parte 2 · campanha

Testar apenas na cópia; guardar e restaurar todos os valores originais.

1. CAMPANHA E46:E59 vazia usa LIVRO, inclusive nível inicial 2. O comparador local deve dar IGUAIS à parte 1.
2. Nível inicial E46 = 5 e custo de saída do nível 5 E69 = 700: XP acumulado do nível 5 é 0 e do nível 6 é 700. O custo 1→2 exige definição da campanha se ela começar no nível 1; vazio aparece Pendente.
3. Cada regra altera só a conta correspondente. Zero é explícito; texto inválido não vira zero e produz aviso.
4. Vida rolada E59 = Sim, Caminho Vanguarda, nível 4, Constituição 3, Buff 5 e dados 5/4/6: vida máxima 40. Vida inicial 8 + Constituição 12 + dados 15 + Buff 5. Dado ausente/999 dá aviso e #N/A. Trocar por continua fixando o resultado final.
5. Prazo 5, uma caixa de Sequela e extras 2: próxima queda dispõe de 2 rodadas. Descanso curto conserva as sequelas; longo limpa caixas e extras.
6. ANALISE 4: 5.274 chaves únicas, preservação das 5.156 anteriores, sem erros de fórmula. Regras e rolagens constam no contrato.
7. Restaurar entradas, efeitos de exemplo e resultados temporários. Inspecionar as grades de regras, XP, vida e o campo de extras. CONFIGURAÇÃO permanece Mizuki Escuro e o lado J:O fica reservado ao custom.

Validação local: regressao-campanha.py (13 cenários), comparar-ficha-01.py, conferir-ficha-xlsx.py, regressao-construir.js, regressao-configuracao.py, regressao-paleta.js e ler-analise.py --teste. O rodar-tudo.sh agora inclui a regressão de campanha; sua bateria integral de 21 não foi repetida nesta etapa.
