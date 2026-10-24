# Ficha em PDF

Uma versão da ficha em PDF preenchível, para quem prefere PDF à planilha. O jogador escreve, e as contas básicas se fazem sozinhas. Não substitui a planilha e não mexe nela.

Os PDFs ficam em [`saidas/`](saidas/), em quatro cores (Mizuki claro e escuro, Eclipse claro e escuro). As cores vêm de `medidas/paletas-grandes/paletas-grandes.json`, as mesmas da planilha. Prévias: `saidas/previa-paginas.png` e `saidas/previa-cores.png`.

O estilo é o **misto** escolhido nos [estudos](estudos/README.md): moldura de painel de mangá (cantos cortados, sombra deslocada, retícula, linhas de velocidade) com o repertório em fichas catalográficas. Toda a arte é desenhada por código.

## Onde abrir

| leitor | preenche | calcula, selos e barras |
|---|---|---|
| Adobe Acrobat Reader (computador) | sim | sim |
| Firefox (leitor embutido, pdf.js) | sim | sim, testado |
| Chrome / Edge | sim | em boa parte; ainda não testado aqui |
| Visualizador do Mac, Arquivos do iPhone, vários leitores Android | sim | **não**: os selos ficam fechados e nada calcula |

Recomendação para o jogador: **Acrobat Reader no computador**. No Firefox também funciona. O leitor pinta um realce (azulado no Firefox) por trás dos campos preenchíveis; isso é do leitor, não do desenho.

## As seis páginas

1. **Personagem** · identidade, atributos em hexágono, progressão do nível, recursos com barra que acompanha o atual, Sequelas, combate (Defesa, Bloquear, ataques, carga e a cura do Morrendo), 23 perícias, 4 TRs, 11 ofícios.
2. **Técnica** · Fundamento, régua de espaços do repertório, 5 Talentos pagos + o CE 4 da Restrição corporal, 12 Aptidões (só o nome), 5 vagas de Classe 0.
3. e 4. **Repertório** · 12 fichas de feitiço, Manejo ou Kata.
5. **Poderes avançados** · Expansão de Domínio, três Liberações Máximas e a Técnica Máxima.
6. **Perfil** · foto, aparência, história, Origem, equipamento, traje, dinheiro, laços e anotações.

## Regras da casa

**Textos:** títulos sem artigo e rótulos com só o nome do campo. Explicação vai na dica que aparece ao passar o mouse; nota pequena na página só quando é regra usada na mesa.

## Todo automático tem ±

**Todo número que a ficha calcula tem ao lado uma caixinha ±** para bônus, penalidade, item ou exceção, e ela soma ao resultado. Se um valor não comporta ajuste, ele não é automático: fica como campo que o jogador escreve. Campos calculados são as etiquetas inclinadas com o número em negrito.

A soma da carga usada é a única exceção: ela só soma o Volume que o próprio jogador digitou, então o ajuste é feito nos itens.

## Selos 封

O que ainda não abriu pelo nível fica coberto pelo carimbo **SELADO** (com o nível que abre), e os campos embaixo ficam travados. O selo some sozinho quando a condição vale:

| seção | abre |
|---|---|
| 3ª, 4ª e 5ª vagas de Classe 0 | níveis 5, 11 e 17 |
| Expansão de Domínio | nível 10 e Refino 4 |
| Liberações Máximas | níveis 10, 20 e 30 |
| Técnica Máxima | nível 17 |

O Refino usado é o da página 1, com o ±, então um marco de Refino já conta. Para exceções da campanha, a caixa **IGNORAR SELOS** (página 5) abre todos.

## O que é automático

- **Nível →** Maestria, Espaços, Classe 0, Classe máxima e Refino (tabela de Progressão, cap. 9).
- **Caminho + nível + CON →** Vida máxima. **Caminho + nível →** PE máximo. **ESS + nível →** Integridade.
- **DES + proteção →** Defesa e Bloquear (`2d10 + Defesa − 11`). Sem Traje/Revestimento, a proteção é a do Cobrir-se de Energia (`1 + Refino ÷ 3`); com o campo do Traje preenchido, usa o do Traje. O escudo soma. "Teto DES" limita a Destreza na Defesa.
- Iniciativa, deslocamento (9 m), carga (`5 + FOR`), CD e ataque da técnica (pelo atributo escolhido), corpo a corpo e à distância.
- **Perícias:** atributo, mais a maestria se treinada, mais metade da maestria se especialista. **TRs:** o Físico usa FOR ou DES conforme a escolha da criação. **Ofícios:** só mostram bônus se treinados, com o atributo padrão do livro.
- **Morrendo:** cura necessária para Aguentar, Insistir 1ª e 2ª (teto de `15 × Classe máxima`) e a janela, que cai com as Sequelas marcadas.
- **Barras** de Vida, Energia e Integridade acompanham o atual contra o máximo.
- **Régua de espaços:** fichas de repertório com nome, Talentos pagos (CE = espaços), degrau da Expansão (2, 3 ou 5) e entidades, contra os Espaços do nível.
- **Fichas de repertório:** PE = `3 × Classe` (Classe 0 é grátis).
- **Expansão** (pela maior Classe, Refino e degrau): abertura `6 × C` PE, raio `1,5 m × Refino` (Incompleta até 7,5 m), duração `metade do Refino` (mínimo 1), desconto `Refino ÷ 3` na Incompleta ou `÷ 2`, barreira `50 × metade do Refino` PV, Acerto `2 × C` d8. O desconto de Família Livre no Acerto entra pelo ±.
- **Liberação Máxima:** PE `3 × Classe + 50%`, arredondado para cima; dano extra `+Classe d8`.
- **Técnica Máxima:** 24/28/32 d8 e 8/12/16 pontos pela faixa de nível; PE `5 × maior Classe`.

## O que ficou de fora, de propósito

Montagem de feitiço com custo de Melhoria/Restrição, catálogos, invocações, missões de XP, salários, a FICHA PESSOAL completa e travas de criação. No PDF esses itens são texto livre que o jogador preenche olhando o livro.

Limites conhecidos:

- Origens sem energia (Restrição Celestial, Sem Técnica) não usam o Cobrir-se de Energia: corrija a Proteção pelo ±.
- A vida rolada (variante) entra pelo ±.
- Texto não numérico num campo de número conta como 0.
- A foto (página 6) é um botão que importa imagem no Acrobat Reader; no Firefox fica só a moldura. Não foi possível testar o Acrobat neste ambiente.

## Gerar e testar

```bash
python3 ficha-pdf/gerar.py          # gera as quatro em ficha-pdf/saidas/
bash ficha-pdf/teste/rodar.sh       # abre no pdf.js e confere 90 valores em cada cor
```

O gerador usa reportlab, pypdf e Pillow. O teste preenche a Kaori do livro (cap. 4: 23 PV, 8 PE, Defesa 13, Atletismo +4, CD 12, TRs +4/+3/+1/+1), sobe para o nível 10 (selos da Liberação e da Classe 0 abrem, o da Expansão espera o Refino 4), ganha um marco de Refino, monta a Expansão e uma Liberação, e chega ao nível 17. Confere contas, barras, régua de espaços, selos visíveis e campos travados. Precisa de node e playwright, e baixa o `pdfjs-dist` na primeira vez. `TELA=1` salva um print de cada página.

As regras saem do livro R53 (`referencias-r53/LIVRO-COMPLETO.md`). Se o livro mudar uma tabela, a mudança entra nas constantes do topo do `gerar.py`.

### Detalhes técnicos que custaram tempo

- O pdf.js só obedece ao "mostrar/esconder" em botões que têm alguma ação; por isso selos e segmentos levam uma ação vazia.
- `NeedAppearances` fica falso: com verdadeiro, leitores sem JavaScript redesenham os botões do zero e os selos somem.
- Os campos de texto não têm o limite padrão de 100 caracteres do reportlab, e as caixas de marcar não têm a marca de "obrigatório" (borda vermelha no leitor).
- O Firefox desenha a marca da caixa como um X fino na cor do sistema, invisível no tema escuro. Por baixo de cada caixa há uma marca cheia que o cálculo acende.
