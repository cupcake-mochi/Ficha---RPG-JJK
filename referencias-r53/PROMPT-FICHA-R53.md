# Atualizar a ficha do Ciclo Maldito para a R53

Atualize o comportamento da ficha digital pela edição R53 completa do Ciclo Maldito. A atualização abrange o rework de Fundamento e suas dependências em Sem Técnica, Técnica Marcial e invocações. Inclua nos cartões de criação uma linha chamada **Função**, conforme os requisitos abaixo.

Implemente no projeto da ficha. O livro e os arquivos de desenvolvimento do sistema são fontes de consulta. Preserve os dados existentes dos personagens e as personalizações de aparência.

## Fontes e versão

O livro completo tem **411 páginas**. As versões clara e noturna têm as mesmas regras.

- Clara: https://ciclo-maldito.vercel.app/livro/Ciclo-Maldito-Livro-de-Regras.pdf
- Noturna: https://ciclo-maldito.vercel.app/noturno
- Metadados e hashes: https://ciclo-maldito.vercel.app/livro/EDICAO-ATUAL.json
- Repositório da publicação: `cupcake-mochi/JJK---PDF---RPG`, branch `main`, commit da R53 `3a810995e5211e2c21c90b02c8a5f43f67fa9d8a`.
- SHA-256 do PDF claro revisado: `a69455a9ca0451983c524362f2765d5753ddfb56b1b52a161d8a444dda4eeece`.
- SHA-256 do noturno: `5d9ab8468c25741b5de2b29ec8864decf917138f1b5a25e2a89a7500c002c35a`.

No computador do projeto, as fontes ficam em:

`/home/mizuki/CHAT-GPT/RPG -JJK/entregas/livro-diagramado-r53/`

Leia `LIVRO-COMPLETO.md`, `LEIA-ME-R53.md` e `ALTERACOES-R52-para-R53.json`. Confira também `ALTERACOES-R51-para-R52.json`, que corrigiu a personalização de marcantes, e `revisao-r53/publicacao-vercel/CORRECAO-RECONFERENCIA-R53.json`, que documenta a última correção do Vigia de papel. Essa correção já está no texto final e no registro R52 para R53.

Se recebeu o pacote junto deste prompt, ele contém cópias dessas fontes. `BLOCOS-R53.json` traz o texto final identificado por bloco. `CATALOGO-E-INTERFACES-R53.json` reúne o catálogo completo e os blocos ligados à montagem. `MANIFESTO.json` registra os hashes dos arquivos do pacote.

Use as regras finais da R53 para resolver diferenças com protótipos, prompts anteriores ou textos históricos de outros repositórios. A nova linha Função é um pedido de interface do autor feito depois da publicação da R53 e deve acompanhar esta implementação. Qualquer decisão nova de regra precisa voltar ao autor; decisões normais de implementação podem ser resolvidas no projeto.

## Começar pelo estado real da ficha

O projeto da ficha vinha sendo desenvolvido em `cupcake-mochi/Ficha---RPG-JJK`, na pasta conhecida como Claude 3. Confirme o clone e a versão atuais antes de alterar arquivos. Leia as instruções locais e o registro de pendências. Preserve as mudanças que já estiverem em andamento.

Identifique a versão do livro usada pelos extratores e catálogos. Atualize todas as referências ativas para a R53. O caminho antigo que contém `r41` chegou a abrigar edições posteriores; confirme o conteúdo pela edição e pelos hashes.

Mapeie, em uma lista curta, os pontos afetados: criação e edição de aplicações, cálculos, validação de escolhas, armazenamento, cartões exibidos, exportação e textos de ajuda. Verifique as superfícies que de fato existem no projeto.

Onde houver arquivos gerados, altere o gerador e regenere as saídas. Confira a estrutura atual antes de usar instruções antigas sobre `ficha-v01/`, `monta.py`, `.gs` ou extratores. O resultado precisa funcionar também nas cópias da planilha, conforme o fluxo vigente do projeto.

## Linha Função nos cartões

Acrescente uma linha visível com o rótulo exato **Função** nos cartões de feitiços, Manejos e Katas. Aplique a mesma apresentação às habilidades montadas de invocações, respeitando suas regras próprias. Posicione-a junto da Classe e da Forma, antes do resultado detalhado, conforme o espaço do cartão atual.

Essa linha apresenta as funções escolhidas e a distribuição salva para a Classe utilizada. Exemplos de apresentação:

- `Função: Dano 2d8; Cura 2d8.`
- `Função: Cura 4d8; Vida temporária 6 pontos.`
- `Função: Proteção por Guarda (+2 Defesa); saldo sem uso 1 ponto.`
- `Função: Controle sem dano, por Prende.`

Os exemplos ilustram a apresentação. A disponibilidade e os números dependem da montagem válida.

No editor do cartão:

1. Permita selecionar uma ou mais funções autorizadas pela Regra, pelas Famílias e pela rota do personagem. Para entidades, use sua definição e suas próprias Famílias. Mostre o motivo quando uma função estiver indisponível.
2. Depois dos custos, permita distribuir pontos inteiros do saldo entre dano, cura e vida temporária. Mostre os pontos atribuídos, o resultado convertido e a sobra sem uso.
3. Cada ponto atribuído a dano produz 1d8; a cura produz 1d8; vida temporária produz 3 pontos. Aplique os tetos da modalidade. Classe 0, máximas e outras concessões específicas conservam seus procedimentos.
4. Funções realizadas por Melhorias, como Guarda, Prende e Anteparo, mostram o efeito comprado. Elas usam a quantidade da própria peça. Uma sobra de pontos conserva o estado sem uso quando não tem uma função variável válida para recebê-la.
5. Exija pelo menos um ponto em cada função variável registrada numa montagem comum. Uma função pode aparecer sem saldo quando seu efeito vem da Melhoria comprada, como a vantagem de Impulso. Separe esses casos no modelo de dados e na validação.
6. Salve a distribuição na ficha da aplicação, inclusive nas versões ampliadas preparadas. Durante a conjuração, use a distribuição daquela Classe. Mais Um permite repartir a quantidade de cada função entre destinatários antes das rolagens, conservando o total reservado a cada função.
7. Em mesclas, mostre o destinatário e a resolução de cada parte, assim como as dependências registradas. Uma cura independente pode acontecer após um ataque errado. Sugar conserva sua dependência do dano causado.
8. Ao selecionar outra Classe preparada, atualize Função, PE e os resultados apresentados no cartão. As linhas preparadas ocupam o mesmo espaço conhecido da aplicação.
9. Exiba a mesma informação nas visualizações e exportações que o projeto já oferece. O cartão precisa apresentar o dado correto em cada função, sem exigir que o jogador procure a distribuição num comentário.

Mantenha separadas no armazenamento as escolhas de função, os pontos atribuídos e os resultados calculados. Preserve também a modalidade, a Forma, as peças e suas opções. Evite armazenar apenas uma frase final impossível de recalcular. Adapte os nomes técnicos à arquitetura existente.

Nos cartões antigos com campo único de dados, converta automaticamente somente quando a função e a distribuição estiverem comprovadas pelos dados salvos. Conserve a versão anterior e marque para revisão os casos ambíguos. Uma mescla antiga com uma única quantidade de dados exige conferir como aquela quantidade era usada antes de preencher as parcelas novas.

## Montagem comum

Separe as decisões da criação: funcionamento da técnica, acesso pelas Famílias, funções, Forma, Melhorias, Restrições e distribuição final do saldo. Cura, vida temporária e Efeito fora de combate passam a usar os procedimentos correspondentes à função. As seis Formas publicadas são Projétil, Toque, Explosão, Aura, Cone e Linha.

### Pontos e conta

Use a Classe da aplicação em uso, inclusive ao Ampliar.

| Classe | Nível mínimo | Pontos e PE normais | Leve | Média | Pesada | Máximo de Melhorias |
|---|---|---|---|---|---|---|
| 1 | 1 | 3 | 1 | 1 | 2 | 2 |
| 2 | 5 | 6 | 1 | 2 | 3 | 2 |
| 3 | 9 | 9 | 2 | 3 | 5 | 3 |
| 4 | 13 | 12 | 2 | 4 | 6 | 3 |
| 5 | 17 | 15 | 3 | 5 | 8 | 4 |
| 6 | 21 | 18 | 3 | 6 | 9 | 4 |
| 7 | 26 | 21 | 4 | 7 | 11 | 4 |

Há até duas Restrições. A Forma e a base da função ficam fora das vagas de Melhoria. Cada compra de Melhoria ocupa sua vaga, salvo permissão expressa.

Calcule:

`saldo = orçamento − base das funções − custo da Forma − Melhorias realmente pagas + devolução aproveitada`.

`devolução aproveitada = mínimo entre devoluções válidas, gasto real nas Melhorias e 2 × Classe`.

Some a devolução de Toque às Restrições para conferir esse teto compartilhado. O preço da base e o da Forma ficam fora do gasto recuperável. O saldo precisa ser válido depois dos arredondamentos. Pontos sem uso podem permanecer na ficha.

### Bases das funções

- Dano tem base zero.
- Cura direta paga Média e exige Amparo.
- Vida temporária individual paga Leve e exige Amparo.
- Cura coletiva paga Média. Vida temporária, Guarda, Impulso e Firmeza coletivos também exigem a base Média.
- Use uma única base nas mesclas, pelo maior custo exigido por suas funções. Acrescente o custo da Forma e os preços das Melhorias.
- Guarda, Impulso e Firmeza individuais pagam suas próprias Melhorias. Capacidades próprias usam os custos aprovados para elas.
- A base e a Forma são pagas integralmente. O desconto de Família Livre é aplicado às Melhorias.

Cura individual tem teto de `2 × Classe` d8. Cura e vida temporária coletivas compartilham um teto de pontos igual a `3 × Classe − preço Pesado`. Aplique o teto à soma dos pontos dessas parcelas coletivas, antes da conversão, conservando o saldo calculado. Os limites gerais da reserva de vida temporária continuam valendo.

Quando uma função atingir o teto, conserve como sem uso os pontos que excedem sua distribuição. A conjuração mantém as parcelas registradas. Corrija também os exemplos e as descrições prontos que ainda ofereçam 9 de vida temporária no Projétil comum de Classe 1 sem peças: o resultado atualizado é **6**, antes do teto geral da reserva.

### Famílias

Na montagem pessoal, são duas Livres, três Fechadas e quatro de preço normal. Cada Melhoria de uma Livre recebe desconto de metade da Classe, para cima, com preço final mínimo 1.

Conferir as proibições pela função e pelas peças, inclusive nas criações próprias:

- Cura direta e vida temporária pelo saldo exigem Amparo disponível.
- Formas de área exigem Área disponível. Cura em área exige também Amparo.
- Mais Um exige Área, inclusive para benefícios individuais repartidos.
- Guarda, Impulso e Firmeza exigem Auxiliares; suas aplicações coletivas exigem Área.
- As demais Melhorias exigem a Família publicada em sua entrada.

Projétil e Toque preservam o acesso às Formas; os efeitos entregues por elas precisam de acesso próprio. Efeitos de recuperação concedidos por outras peças ou Talentos conservam seus requisitos específicos. A seleção de Amparo Fechada precisa continuar permitindo o que essas concessões expressamente autorizam.

### Formas e medidas

Para Classes 1 a 5:

| Forma | Custo | Alcance e região básicos |
|---|---|---|
| Projétil | 0 | Alvo ofensivo a 18 m; benefício individual a 9 m. |
| Toque | 0 e devolução Leve aplicável | Alvos a 1,5 m. |
| Explosão | Média | Esfera de raio 3 m; centro a até 18 m. |
| Aura | Leve | Esfera de raio 3 m centrada em quem executa. |
| Cone | Leve | Comprimento 4,5 m; origem a até 18 m. |
| Linha | Leve | 18 m por 1,5 m; origem a até 18 m. |

Alcance mede a distância até o alvo ou a origem da área. Área mede as dimensões a partir dessa origem. Longe e Maior fazem alterações diferentes. Use as tabelas completas de progressão da R53 para Classes 0, 6 e 7 e para entidades.

Toque concede devolução Leve nas montagens comuns de Classes 1 a 7, fora das vagas de Restrição. Uma aplicação exclusivamente pessoal fica sem essa devolução. Toque e Aura não aceitam Longe nem Queima-Roupa.

Queima-Roupa ocupa uma vaga de Restrição. Em Projétil, devolve Média e limita todos os alvos diretos a 1,5 m, incluindo as extensões indicadas na entrada. Em Explosão, Cone e Linha, devolve Leve e fixa a origem em quem executa. A área mantém suas dimensões e pode receber Maior. Longe e mudanças de origem não podem retirar essa exigência mantendo sua devolução.

### Mesclas e destinatários

Mais Um acrescenta um destinatário individual diferente; admite duas compras e ocupa uma vaga a cada compra. Dados de dano e cura, ou pontos de vida temporária, são repartidos entre os destinatários antes de rolar. As parcelas de cada função conservam seu total. Rajada segue sua divisão em tiros e permite repetir alvo.

Guarda, Impulso e as categorias compradas de Firmeza podem beneficiar integralmente os destinatários individuais autorizados por Mais Um. Em aplicação coletiva, essas peças compartilham um grupo de até `Classe do uso + 1` criaturas. Maior conserva esse número. Cura em área segue seus próprios destinatários e teto; confira cada função separadamente.

Levanta, Pressa, Anteparo, marcas e outras peças preservam seus limites próprios. Salto e Estilhaço repetem somente o efeito secundário descrito. Cada um produz no máximo um secundário por conjuração. Preserve o teto de `4 × Classe` em d8 da montagem e as exceções publicadas, incluindo Acúmulo, Ritual e máximas.

### Controle

Salve na criação a escolha entre sem reforço, dano limitado à Classe e sem dano. Dano limitado à Classe concede a rodada adicional aos efeitos compatíveis. Sem dano descarta todo o saldo e acrescenta também +2 à CD dos TRs próprios de Controle compatíveis. Os pontos descartados deixam de estar disponíveis para outras funções.

**Controle Livre conserva o reforço.** Quando o desconto deixar saldo restante, a opção sem dano descarta esse saldo e recebe o +2 aplicável. O desconto sozinho não cria esse bônus. Salve essa opção também nas alternativas que precisem dela.

Condição, Prende e Cerca exigem TR mesmo após um ataque acertar. O +2 afeta as CDs próprias compatíveis, incluindo as saídas indicadas no livro. Uma mesma aplicação pode ter CDs diferentes por função. Anteparo e Terreno não recebem um TR inventado para aproveitar o bônus. Conserve os prazos individuais das peças, os testes de saída e as incompatibilidades com duração ampliada. Classe 0 e máximas seguem suas regras próprias.

## Catálogo e Restrições

Atualize o catálogo completo pelos textos finais: **61 entradas de Melhorias e 19 de Restrições**. Para cada entrada, confira Família, preço, requisitos, opções fixas, repetição, duração e incompatibilidades. As opções internas de uma entrada também precisam ser representadas.

Pontos que exigem atenção:

- Impulso concede vantagem no próximo ataque, até o fim do próximo turno do beneficiário.
- Firmeza escolhe na criação a categoria perícia, ofício ou TR. Dura até o começo do próximo turno de quem conjurou. Compras distintas podem abranger categorias diferentes. Testes de categorias diferentes conservam seus próprios benefícios.
- Mais Um incorpora a distribuição de benefícios. Revise registros antigos de Junto para evitar compras duplicadas.
- Longe conserva as modalidades publicadas de alcance. Maior conserva as modalidades de área. Revise nomes históricos como Muito Longe e Muito Maior pela modalidade correspondente.
- Sobrecusto cobra `2 × Classe usada` PE adicionais na própria conjuração, mesmo com dispensa ou redução do custo normal. Migre Dívida conforme a regra final, conferindo o custo total salvo.
- Uma Vez, Condicional, Aquecer e equivalentes próprios compartilham o grupo de frequência. Atrasar e Parado têm impedimentos sobrepostos. Consulte também os demais grupos e exceções de Barulho e Assinatura.
- Gesto conserva duas mãos livres e voz audível mesmo com Silencioso. O executante precisa conseguir cumprir a Restrição.
- Consulte a R53 para peças removidas, unificadas ou deslocadas. Uma troca de posições completa que sobreviva em catálogo antigo exige revisão; não a restaure como Melhoria publicada.

Mantenha Melhorias e Restrições próprias com campos para a aprovação do mestre e seus limites. A criação precisa registrar Família, efeito, ação, custo e condições pertinentes. As proibições de Família e os limites de compras continuam valendo. Compras próprias repetidas ou equivalentes dependem do acordo previsto no livro.

## Classe 0 e máximas

Preserve o procedimento de dados-base da Classe 0. A Melhoria Leve retira um dado; uma Restrição Leve válida recupera no máximo esse dado. Toque não devolve pontos automaticamente nessa Classe. Queima-Roupa só usa sua modalidade Leve nas áreas elegíveis. Vida temporária, cura e benefícios coletivos permanecem indisponíveis. Uma aplicação benéfica individual pode usar sua Melhoria Leve e descartar o dano.

Liberação Máxima e Técnica Máxima conservam suas contas e permissões próprias. Leia os blocos completos antes de aplicar a elas o novo modelo de funções. A Técnica Máxima não aceita Queima-Roupa. Disponibilize escolhas de função e distribuição apenas nos casos permitidos pela modalidade e pela rota.

## Sem Técnica e Técnica Marcial

As duas rotas usam o procedimento comum de montagem. Apresente os mesmos controles de função, Forma e peças, com os nomes próprios de cada rota.

| Elemento | Técnica amaldiçoada | Sem Técnica | Técnica Marcial |
|---|---|---|---|
| Aplicação | Feitiço | Manejo | Kata |
| Liberação Máxima | Liberação Máxima | Liberação Máxima | Ruptura |
| Técnica Máxima | Técnica Máxima | Auge | Ōgi |

Sem Técnica desenvolve uma semente e conserva energia, Refino e aptidões. A semente limita o funcionamento possível e sua aquisição segue a regra de nível 2. A opção é separada das escolhas de marcante e menores.

Técnica Marcial parte de arma ou ferramenta. O equipamento funciona como Selo. O dado da arma não se soma ao dano da Kata. O Corpo Amaldiçoado conserva energia, Refino e aptidões; o Restringido Sem Energia usa Lapidação e Bênçãos, com PE de Esforço. A Restrição corporal segue o Fundamento comum.

Preserve as proibições de Ritual e Domínio de cada rota. Escolher a função de cura exige tanto acesso pelas Famílias quanto permissão do funcionamento adotado. O novo campo Função deve respeitar esses filtros.

## Invocações

Confira integralmente Invocações em campo e Construir invocações. A montagem compartilha o catálogo, mas usa o orçamento e o desconto próprios da entidade.

| Classe da especial | Pontos | PE | Máximo de Melhorias |
|---|---|---|---|
| 1 | 2 | 3 | 2 |
| 2 | 4 | 6 | 2 |
| 3 | 6 | 9 | 3 |
| 4 | 9 | 12 | 3 |
| 5 | 11 | 15 | 4 |
| 6 | 13 | 18 | 4 |
| 7 | 16 | 21 | 4 |

Na regra normal da entidade, são três Famílias abertas, uma delas Livre. O desconto da Livre é metade da Classe real **para baixo**, mínimo 1, com preço final mínimo 1. Invocação Principal e Múltiplas Invocações conservam suas exceções de Famílias abertas e Livres.

A base das funções, o preço da Forma e a devolução de Toque seguem o procedimento comum. Mantenha os pontos iniciais da tabela acima. Cura individual tem teto de `pontos da entidade − preço Médio` em d8; vida temporária individual tem teto de `3 × (pontos da entidade − preço Leve)`; o teto coletivo compartilhado é `pontos da entidade − preço Pesado`. Conserve os limites gerais de vida temporária.

Custos, PE e requisitos usam a Classe real. Somente os efeitos listados em Efeitos reduzidos usam uma Classe a menos, mínimo 1. O alcance até alvo ou origem usa a Classe real; a área tem sua progressão própria. O grupo coletivo de Guarda, Impulso e Firmeza usa `Classe real + 1`.

Condições Médias e Pesadas exigem especial comandada ativamente. Básicas e respostas autônomas conservam suas restrições. Uma Aura ou especial com Reação pode usar essas condições quando executada por comando e com os custos exigidos. A básica de Classe 0 usa dados próprios e não produz cura, vida temporária ou benefícios coletivos.

Traduza Rápido, Reação, Armado, Segura, Atrasar e Carregar pelos recursos de comando e atuação de Invocações em campo. A distância e as exigências se referem à entidade executora. Recolher e manifestar não renovam usos gastos.

Atualize os exemplos prontos, incluindo Orientação do Vigia: Firmeza na categoria perícia, até o começo do próximo turno de Bruna. Tiras de resgate paga a base Leve e usa Parado cumprido pela entidade. Use os números e as ações do texto final.

## Dependências de Caminhos e Ritual

Leia todos os blocos dependentes do registro R52 para R53. Em particular:

- **Forma Fluida:** troca somente a Forma. Conserva funções e distribuição do saldo. Recalcula base, Forma e devoluções válidas; a troca não pode aumentar o saldo.
- **Remodelar:** paga a diferença positiva retirando o resultado já registrado. Numa mescla, nenhuma parcela aumenta e os pontos não migram entre funções. Efeito Próprio conserva sua proibição de retirada.
- **Manifestação Condutora:** preserva Toque, Aura e Queima-Roupa, mesmo com suas permissões de origem.
- **Modulação Divisão:** usa Mais Um também em aplicações sem dano.
- **Expressão Instintiva:** inclui Sobrecusto e conserva as alternativas de custo completas e os acréscimos independentes.
- **Evocador:** aplique as exigências de proximidade e demais Restrições a quem executa a especial. Preserve as permissões próprias do Caminho.
- **Ritual de Compartilhamento:** copia uma parcela benéfica individual da origem autorizada. Com Mais Um, usa uma das menores parcelas. Mantém os limites únicos e exclui a aplicação coletiva. Ritual de Alcance conserva as incompatibilidades com proximidade.

Atualize também Energia Reversa, Energia Positiva, Prática Cotidiana, exemplos de criação e remissões afetadas. As permissões específicas de cura hostil continuam exigindo suas aptidões.

## Regras anteriores que precisam continuar corretas

Confira se a ficha já implementou as edições anteriores. Faça apenas os ajustes que faltarem para corresponder ao texto final da R53.

- Personalização da Origem permite menores e Legados de história. A marcante usa opções publicadas, com a exceção expressa de Criar sua Restrição no ramo Restrição corporal. Famílias próprias de Descendente usam uma modalidade publicada da marcante.
- Preserve o modelo atual de Origens, suas escolhas separadas de Sem Técnica, o CE4 específico da Restrição corporal e a ausência de benefício mecânico do Legado de história.
- Preserve Morrendo, Aguentar e Insistir da versão atual, suas Sequelas e tratamento, incluindo Recomposição em **4 × a maior Classe**. Confira as interações de Levanta, Limpa Fundo, Ainda Há Tempo e Segundo Fôlego nos textos finais.
- Confira ofício compatível, reparo de corpos superiores, progressão das entidades criadas e reconstrução. A maldição domada mantém sua regra própria de nível.
- Confira as Bênçãos Represália e Sangue Frio, o momento de Bloquear, Ataque sem Prenúncio, as vagas de pactos, Ritual e Cortina pelo texto atual.

Esses pontos são verificações de compatibilidade para fichas com atraso de versão. Preserve o comportamento já correto.

## Migração e validação

Registre quais campos mudaram e como cada ficha antiga foi tratada. Preserve a versão anterior para permitir conferência. Trate de forma explícita os registros de antigas Formas de Cura, Apoio, Onda e Efeito, as peças renomeadas e as mesclas que ainda não têm distribuição armazenada.

Na migração de Toque e Aura, remova a antiga inclusão automática de Corpo a Corpo e sua devolução Média. Recalcule Toque pela devolução Leve fora das vagas; Aura paga Leve e conserva suas vagas sem devolução automática. Um registro explícito da antiga Restrição em outra Forma precisa ser conferido pelas modalidades atuais de Queima-Roupa. Registre qualquer mudança de custo ou resultado e mantenha o original recuperável.

Liste de uma vez os padrões que os extratores deixaram de localizar. Atualize IDs, textos de ajuda, filtros e cálculos relacionados. Faça uma varredura das regras ativas por termos antigos ao final. Textos históricos identificados podem permanecer no histórico.

Teste, no mínimo:

1. **Vida temporária pessoal de Classe 1:** Projétil sem peças, orçamento 3, base Leve 1, saldo 2, resultado 6 de vida temporária antes do teto geral. Toque sem Melhorias conserva essa base paga e não devolve pontos aproveitáveis.
2. **Toque pessoal de Classe 3:** Precisão de preço normal custa 2, devolução de Toque 2, saldo 9. Resultado 9d8, bônus da peça e alcance 1,5 m; uma Melhoria e nenhuma Restrição.
3. **Mescla de Classe 3:** Projétil, base Média 3, Mais Um 2, sem desconto ou Restrição: saldo 4, distribuição salva de 2d8 de dano e 2d8 de cura. Errar o ataque conserva a cura independente. Alterar a distribuição durante o uso precisa ser impedido.
4. **Ampliação da mesma mescla:** Classe 4, PE 12, base 4, Mais Um 2, saldo 6. Uma linha preparada com 4d8 de dano e 2d8 de cura ocupa o mesmo espaço da versão de Classe 3.
5. **Família Fechada:** Amparo Fechada bloqueia cura direta por saldo; Área Fechada bloqueia cura em área e Mais Um. Guarda individual com Auxiliares disponível continua elegível, conforme a Regra.
6. **Controle Livre:** a opção sem dano descarta a sobra do desconto e mantém o +2 nas CDs compatíveis. CD normal 14 com Prende passa a 16; uma peça de outra Família conserva sua CD 14. Resultado 15 pode evitar uma e receber a outra.
7. **Proximidade:** Aura custa Leve; Explosão custa Média; Cone e Linha custam Leve. Queima-Roupa em Cone fixa a origem e mantém o comprimento. Toque e Aura rejeitam a Restrição. Longe e Maior alteram somente suas medidas elegíveis.
8. **Entidade de Classe 3:** uma Melhoria Média de Família Livre custa 2. Na montagem pessoal da mesma Classe, custa 1. Confira também os tetos distintos e o alcance de Classe real com a área reduzida.
9. **Entidade de Classe 1:** Projétil e vida temporária individual, sem peças: orçamento 2, base 1, resultado 3 de vida temporária antes do teto geral. O teto de pontos de cura coletiva nessa Classe é zero.
10. **Impulso e Firmeza:** confira as categorias que consomem cada vantagem, as compras separadas de Firmeza e os momentos de término. O cartão precisa mostrar a categoria escolhida.
11. **Forma Fluida de Classe 3:** Aura 2 e Fura 3 produzem 4d8, sem descontos ou Restrições. Trocar por Explosão 3 reduz para 3d8 e preserva a função de dano. O adicional de Remodelar é 2 PE.
12. **Classe 0 e rotas:** rejeite cura e vida temporária na Classe 0. Uma Kata usa os dados da montagem; arma equipada conserva seu dado fora dessa conta. A escolha de Sem Técnica conserva o pacote de Origem.
13. **Cartões e dados salvos:** teste aplicação com uma função, mescla, efeito sem dados, versão ampliada e especial de entidade. Reabra a ficha e confira a mesma distribuição. Verifique também edição, cópia e exportações disponíveis.
14. **Ficha antiga:** um registro ambíguo precisa continuar recuperável e marcado para revisão. Uma migração comprovada mantém destinatários, requisitos e efeitos existentes.

Execute a suíte prevista pelo projeto e os testes de interface necessários. Rode as verificações pesadas em série, respeitando o limite de memória já adotado, pois o computador teve travamentos com execuções simultâneas. Não acrescente testes que apenas repitam a implementação; os casos acima devem conferir regras e resultados observáveis.

## Entrega

Entregue a ficha implementada e validada, com um resumo curto das mudanças. Informe os registros antigos que precisaram de revisão manual e o que ainda depender de decisão do autor. Inclua um roteiro de teste com aba ou tela, cartão e resultado esperado. Atualize o registro de pendências usando o próximo identificador disponível.

Preserve as regras do projeto para publicação. Este prompt autoriza a implementação e a validação da ficha; commit, push ou publicação da ficha dependem da autorização aplicável a ela. O envio dos PDFs do livro ao Git é uma operação já concluída em outro repositório.
