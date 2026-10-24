# Possíveis ideias pro futuro

Ideias levantadas em 24/10/2026, depois de uma leitura do repositório e da ficha oficial (R53 + salários). Nenhuma está aprovada nem em andamento: é só um banco de ideias.

Ponto de partida comum: a aba **ANALISE** (18.394 chaves, formato fixo e versionado, já lida pelo bot do Discord) funciona como uma API do personagem. Dá pra construir em cima dela sem tocar na ficha oficial.

## 1 · Carteira viva fora do Sheets

Página web leve, feita pro celular, que lê a ANALISE e mostra o personagem como documento da escola: vida, energia, cartões, técnica e missões. Só leitura. A CARTEIRA ganharia um QR code apontando pra ela.

- Resolve a dor de abrir 7 abas pesadas no celular (requisito desde o DESIGN).
- Não exige migração na oficial.

## 2 · A ficha reage ao estado do personagem

Usar o motor de troca de paleta (122 paletas) de forma narrativa: em **Morrendo** a ficha escurece e mostra um aviso; com **Expansão de Domínio** ativa, uma paleta própria temporária.

- Sempre com texto junto: cor não carrega informação sozinha (DESIGN §3.2).
- Mexe na oficial: exige snapshot e ensaio em cópia.

## 3 · Holerite da Escola

A cada fechamento salarial, gerar um contracheque no estilo do universo (Grau, missões do ciclo, parcela, assinatura) em PDF ou Doc, a partir do que a extensão de salários já registra.

## 4 · Crônica do personagem

Linha do tempo com as datas que a ficha já grava (emissão, missões, mudanças de Grau, salários, sequelas), escrita como crônica: "Em 20/10 foi emitido... em 19/11 recebeu ¥150.000 após 3 missões...".

## 5 · Sala de treino

Ler os cartões pela ANALISE e simular: chance de acerto contra Defesa X, dano médio por rodada, rodadas pra derrubar um alvo padrão. Serve ao jogador e ao mestre como ferramenta de balanceamento.

> Combinação mais forte: 1 + 5 (mesma leitura da ANALISE, nada na oficial).
