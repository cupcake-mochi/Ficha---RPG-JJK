# Prompt para a conversa nova

Cole o texto abaixo e anexe o `projeto-m-ficha-digital.zip` inteiro, mais o `Projeto-M-Manual-da-Guilda.pdf`.

---

Quero construir a ficha de personagem digital do meu sistema de RPG, o Projeto M: sistema de mesa de Jujutsu Kaisen, base d20, feito para um servidor de guilda com cinco a sete mestres e personagem persistente entre mesas. O filtro que decidiu quase toda regra dele foi um só: dois mestres que nunca conversaram chegam ao mesmo número?

Anexei um zip com tudo o que já foi levantado, e o manual em PDF. **Uma conversa inteira já aconteceu sobre isso**, e o zip é o resultado dela. Não recomece do zero.

**Comece assim, nesta ordem:**

1. **Leia o `PENDENCIAS.md` primeiro.** Ele tem nove decisões em aberto, com as opções e o preço de cada uma já calculados. **As cinco do bloco A travam a construção.**

2. **Me traga as cinco do bloco A, uma rodada de cada vez, e espere eu responder.** Não decida por mim, e não me traga as nove de uma vez. Se você tiver recomendação, diga qual e por quê, mas a escolha é minha.

3. **Depois leia o `HANDOFF-ficha-digital.md`** (onde o trabalho parou, e os quatro problemas achados no repositório) **e o `DESIGN-ficha-digital.md`** (paleta com contraste medido, tipografia, estrutura de abas, reservas, progressão e automação).

4. **A `ESPECIFICACAO-ficha-digital.md` é consulta**, não leitura de cabo a rabo. Volte nela quando precisar de uma fórmula ou de um catálogo.

5. **O `catalogo-projeto-m.json` é a fonte de dados.** Não redigite catálogo, leia dele: 23 perícias, 11 ofícios, 5 Caminhos, 15 Trilhas, 9 Famílias, 10 Formas, 66 Melhorias, 14 condições, 19 Restrições, 9 rotas de criação, 85 Legados e a tabela de progressão.

6. **Rode os validadores antes de mexer em qualquer número.** São seis, e todos passam hoje:

```
python3 conferir-catalogo.py      integridade e as contagens que o manual declara por extenso
python3 conferir-kaori.py         regressão contra a ficha de exemplo
python3 conferir-progressao.py    as fórmulas contra a tabela impressa, do nível 1 ao 30
python3 regressao-exemplos.py     os feitiços publicados na página 137
python3 arnes.py                  prova que cada checagem acende quando devia
python3 revisao-cetica.py         confere a especificação contra o manual
```

**Só depois que eu responder o bloco A, comece a construir**, e nesta ordem: números derivados, perícias e testes, camada de escolha, Fundamento, e a ficção por último.

**Regras que valem a conversa inteira:**

- **Onde a ficha e o manual discordarem, o manual vence.** O PDF é a referência de mesa; as peças do repositório são argumento de design.
- **Onde a regra não existe, não invente.** O que está em aberto está no `PENDENCIAS.md`. Se achar uma lacuna que não está lá, **me pergunte antes de decidir**.
- **Escolha de sabor é minha**: quantos itens, como se chamam, em que ordem aparecem, e o que fica bonito. Traga opções com o trade-off **calculado**, em rodadas curtas. Não me entregue uma proposta grande pronta.
- **Não me pergunte o que a conta responde.** Se dá para medir, meça e me mostre o resultado.
- **Discuta antes de construir.** Quando eu pedir para debater, debata; não saia fazendo.
- **Mostre o resultado no chat**, não só no arquivo.
- **Sempre me entregue os arquivos num zip só.**
- **Português informal do Brasil.** Nunca português de Portugal.
- **Evite travessão** fora de cabeçalho de item de catálogo.
- **Nunca edite nem comite nos meus repositórios.** Trabalho vai em diretório próprio, e entrega é por envio de arquivo.

**Três coisas que já custaram erro nesta conversa, e que vão custar de novo:**

1. **Não confie na Kaori sozinha.** Ela é o único caso de teste, é nível 2, e já deixou passar dois defeitos: a divergência das Famílias (porque ela só usa as que as duas listas têm em comum) e o erro de maestria (que só aparece do nível 8 em diante).
2. **Contagem declarada é ouro.** O manual escreve "vinte e três perícias" e "sessenta e seis Melhorias" por extenso. Toda extração que bate contra esses números pegou defeito. Onde não existe contagem declarada, como nos Legados, a garantia é menor e vale dizer isso.
3. **Frase ambígua vira número errado.** "Maestria sobe +1 a cada oito níveis" produziu uma fórmula que errava em seis dos trinta níveis. Quando a especificação e a tabela discordarem, **a tabela é a dona**.
