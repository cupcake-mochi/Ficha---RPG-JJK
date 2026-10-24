# Ficha em PDF · protótipo

Uma versão enxuta da ficha, em PDF preenchível, para quem prefere PDF à planilha. Ela segue o estilo das fichas de D&D: o jogador escreve, e as contas básicas se fazem sozinhas. Não substitui a planilha e não mexe nela.

Os PDFs ficam em [`saidas/`](saidas/), em quatro cores (Mizuki claro e escuro, Eclipse claro e escuro). As cores vêm de `medidas/paletas-grandes/paletas-grandes.json`, as mesmas da planilha.

## Onde abrir

| leitor | preenche | calcula |
|---|---|---|
| Adobe Acrobat Reader (computador) | sim | sim |
| Firefox (leitor embutido, pdf.js) | sim | sim, testado |
| Chrome / Edge | sim | em boa parte; ainda não testado aqui |
| Visualizador do Mac, Arquivos do iPhone, vários leitores Android | sim | **não** |

Recomendação para o jogador: **Acrobat Reader no computador**. No Firefox também funciona.

## Regra: todo automático tem ±

**Todo número que a ficha calcula tem ao lado uma caixinha ±** para bônus, penalidade, item ou exceção, e ela soma ao resultado. Se um valor não comporta ajuste, ele não deve ser automático: fica como campo que o jogador escreve. Campos automáticos têm fundo mais forte e texto em negrito.

A soma da carga usada é a única exceção: ela só soma o Volume que o próprio jogador digitou, então o ajuste é feito nos itens.

## O que é automático

- **Nível →** Maestria, Espaços, Classe 0, Classe máxima e Refino (tabela de Progressão, cap. 9).
- **Caminho + nível + CON →** Vida máxima. **Caminho + nível →** PE máximo. **ESS + nível →** Integridade.
- **DES + proteção →** Defesa e Bloquear (`2d10 + Defesa − 11`). Sem Traje/Revestimento, a proteção é a do Cobrir-se de Energia (`1 + Refino ÷ 3`); com o campo do Traje preenchido, usa o do Traje. O escudo soma. "Teto de DES" limita a Destreza na Defesa.
- Iniciativa, deslocamento (9 m), carga (`5 + FOR`), CD e ataque da técnica (pelo atributo escolhido), corpo a corpo e à distância.
- **23 perícias:** atributo, mais a maestria se treinada, mais metade da maestria se especialista.
- **4 TRs:** o Físico usa FOR ou DES conforme a escolha da criação.
- **11 ofícios:** só mostram bônus se treinados, com o atributo padrão do livro.
- **Morrendo:** cura necessária para Aguentar, Insistir 1ª e 2ª (com o teto de `15 × Classe máxima`) e a janela, que cai com as Sequelas marcadas.
- **Feitiços:** PE = `3 × Classe`. **Equipamento:** soma do Volume contra o limite de carga.

## O que ficou de fora, de propósito

Montagem de feitiço com custo de Melhoria/Restrição, catálogos, invocações, missões de XP, salários, FICHA PESSOAL completa, travas de criação. No PDF esses itens são texto livre que o jogador preenche olhando o livro.

Limites conhecidos do protótipo:

- Origens sem energia (Restrição Celestial, Sem Técnica) não usam o Cobrir-se de Energia: corrija a Proteção pelo ±.
- A vida rolada (variante) também entra pelo ±.
- Texto não numérico num campo de número conta como 0.

## Gerar e testar

```bash
python3 ficha-pdf/gerar.py          # gera as quatro em ficha-pdf/saidas/
bash ficha-pdf/teste/rodar.sh       # abre no pdf.js e confere 43 valores
```

O gerador usa reportlab e pypdf. O teste preenche a Kaori do livro (cap. 4: 23 PV, 8 PE, Defesa 13, Atletismo +4, CD 12, TRs +4/+3/+1/+1) e depois a sobe para o nível 10 com ajustes. Precisa de node e playwright, e baixa o `pdfjs-dist` na primeira vez.

As regras saem do livro R53 (`referencias-r53/LIVRO-COMPLETO.md`). Se o livro mudar uma tabela, a mudança entra nas constantes do topo do `gerar.py`.
