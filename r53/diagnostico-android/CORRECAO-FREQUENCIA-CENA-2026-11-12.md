# Frequência por cena nas cartas de habilidade · 12/11/2026

Achado da `AUDITORIA-CAMINHOS-TRILHAS-2026-11-11.md`. O R66 trocou "uma vez por combate" por "uma vez por cena" em
cinco habilidades (registros R66-05 a R66-12, motivo "frequência aprovada por cena"), e as cartas da ficha ainda
diziam "por combate". O Mizuki mandou corrigir.

## O que mudou no texto

Ao todo são oito frases. Cada uma aparece uma única vez na carta, e o texto novo é o do registro do livro.

| carta | Caminho ou Trilha, nível | frases |
|---|---|---|
| Especial Combinada | Evocador, 30 | "Uma vez por cena · Participantes a até 18 m." e "Marque o uso da habilidade na cena." |
| Resposta Técnica da Dupla | Parceria, 27 | "Uma vez por cena · Turno de outra criatura", "marque o uso da habilidade na cena" e "O uso por cena pertence ao conjunto" |
| Um Passo à Frente | Incursor, 30 | "Uma vez por cena, pode ativar imediatamente…" |
| Sentença Final | Assassino, 27 | "Uma vez por cena, ao utilizar Golpe Cirúrgico…" |
| Trajetória Perfeita | Malabarista, 27 | "Uma vez por cena · Fluidez e 12 PE." |

Nenhuma outra regra muda: o resto do texto, os nomes, os níveis e os subtítulos continuam iguais. Na ficha
inteira não sobrou nenhum "por combate".

## Como entra

- **Fonte:** `r53/textos_revisados.py`, em `FREQUENCIA_POR_CENA`. É a mesma camada que já trazia o texto do R60 e
  do R61, porque o `manual.txt` do repositório é o R53.
- **Extrator:** `ficha-v01/extrair_habilidades.py` aplica as trocas depois de ler o manual (`revisa_r66`). Ele para
  em dois casos:
  - a frase do R53 não aparece exatamente uma vez;
  - sobra "por combate" ou "uso da habilidade no combate" em qualquer carta.

  O `--confere` leva o texto revisado de volta à frase do R53 antes de procurar no manual.
- **Gerados:** `habilidades-do-livro.json` (as 5 cartas), `apps-script/Habilidades.gs` e `apps-script/Caminho.gs`.
  O caminho leve guarda uma cópia compactada das cartas. Aberta, ela difere do HEAD só nessas frases.
- **Teste:** `r53/testes/frequencia_cena.js`, que está no smoke. Ele confere:
  - o JSON contra o extrator, com só as 5 cartas mudando;
  - as duas cópias no Apps Script;
  - a recusa de frase ausente e de "por combate" novo;
  - o instalador.
- **Smoke completo:** 161 OK, saída 0.

## Instalação nas duas QAs

Nas QAs o código não fica em arquivos soltos. As cartas moram em dois lugares do projeto instalado, os dois com hash:

1. o módulo R53, compactado nos cinco `R53_CODIGO_` (hash no `r53Modulo_` do `Codigo.gs`);
2. o caminho leve, no blob do `r53CaminhoLeve_` dentro do `Codigo.gs` (hash próprio).

O `r53/diagnostico-android/instalar_frequencia_cena.js` gera o trecho que roda no console do editor. Antes do
primeiro `setValue`, ele faz quatro coisas:
- confere os dois hashes;
- troca as oito frases, exigindo exatamente uma de cada em cada lugar;
- recompacta e confirma a ida e volta;
- coloca os hashes novos.

Com `--reverter`, o trecho desfaz a troca. Não é o pacote integral: o resto do código instalado fica intacto.

| QA | módulo | caminho leve | depois de recarregar o editor |
|---|---|---|---|
| Era (`1LBZOf9v…`) | `9dc3480af822` → `bd42b5351ec1` | `98fb3594c5bb` → `97972ea00a2c` | hashes conferem, zero "por combate" |
| Ciclo (`1HQqGOVG…`) | `9dc3480af822` → `bd42b5351ec1` | `98fb3594c5bb` → `97972ea00a2c` | hashes conferem, zero "por combate" |

## Ensaio no Sheets (entradas repostas)

| QA | escolha | carta lida |
|---|---|---|
| Era | Evocador + Parceria | Especial Combinada (D159) e Resposta Técnica da Dupla (D190): "Uma vez por cena", "na cena" |
| Ciclo | Incursor + Assassino | Um Passo à Frente (D159) e Sentença Final (D190): "Uma vez por cena" |
| Ciclo | Incursor + Malabarista | Trajetória Perfeita (D190): "Uma vez por cena · Fluidez e 12 PE." |

**Reposição.** As duas QAs começaram sem Caminho e sem Trilha. Elas voltaram ao estado de antes:
- a Trilha voltou digitada como "Escolha sua Trilha";
- o Caminho foi apagado, o que dispara o onEdit e desmarca os treinos que ele tinha posto;
- o texto "Escolha seu Caminho" foi reposto pela API, porque a validação recusa esse texto digitado;
- conferido depois: perícias, treinos de arma da FICHA PESSOAL, AK81 ("Não trocou") e cartas iguais ao estado
  guardado antes.

## Achado à parte (não consertado)

**Aviso de categoria que fica.** Escolher uma Trilha com categoria de arma escreve "Escolha a categoria de arma
(Treino de Combate)" em FICHA!AK85. O exemplo é a Parceria: é o `grupoDeArmaDaTrilha_`.

Quando a Trilha muda para outra, esse aviso não some. O código só escreve, de propósito, para não apagar a categoria
que o jogador escolheu. No ensaio da Era, a célula foi limpa pela API. É um caso de interface que já existia antes
deste conserto e fica para o Mizuki decidir.

## Fora deste conserto

- **Oficiais.** Nada foi aplicado. Fica para o Mizuki, junto com a mescla da pilha na main. Nas oficiais o mesmo
  trecho serve, desde que os hashes instalados sejam os esperados (o trecho confere e recusa se não forem).
- **Fichas já montadas.** Uma carta já escrita na planilha só pega o texto novo quando o Caminho ou a Trilha forem
  escolhidos de novo.
- **Redação R66 no resto da ficha e atributos naturais:** decisões abertas na auditoria de 11/11.
