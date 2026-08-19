# -*- coding: utf-8 -*-
# ==========================================================================
# 7. FAMILIAS — as nove da ficha sao as nove do manual
# ==========================================================================
# Por que ela existe: a ficha imprimia Ataque, Corpo, Movimento e Percepcao,
# que o manual nao tem, e nao imprimia Alcance, Mira, Tempo e Marca, que juntas
# sao 27 das 66 Melhorias. Passou porque as outras seis checagens deste arquivo
# cobrem pericia, oficio, Caminho, Trilha e constante — e a lista de Familias
# era a unica copia da ficha sem dono. Licao no 9, na camada que vai para a mao
# do jogador.
#
# O DONO: hoje a lista so existe impressa, no gerador do manual. Se uma peca de
# 03-mecanica passar a declarar as nove, troque a fonte abaixo para ela — o
# gerador do manual e' saida, e saida nao devia ser autoridade de ninguem.
bloco('7. FAMILIAS — as nove da ficha sao as nove do manual')

PARTB = ler(os.path.join(AQUI, '..', '..', 'manual', 'gerador', 'partB.js'),
            'o partB.js do gerador do manual')
m = re.search(r"H2\('Famílias'\).*?TBL\(\[[^\]]*\],\s*\[(.*?)\n\s*\],", PARTB, re.S)
if not m:
    erro('nao achei a tabela de Familias no partB.js — se o gerador do manual '
         'mudou de forma, esta checagem parou de conferir')
else:
    do_manual = re.findall(r"\['([^']+)',", m.group(1))
    da_ficha = lista_js('FAMILIAS')
    if da_ficha is None:
        erro('nao achei FAMILIAS no dados.js')
    elif len(do_manual) != 9:
        erro(f'li {len(do_manual)} Familias no partB.js, e deviam ser 9 — '
             f'a checagem esta lendo errado, conserte ela antes de confiar')
    else:
        sobra = [f for f in da_ficha if f not in do_manual]
        falta = [f for f in do_manual if f not in da_ficha]
        if sobra:
            erro(f'a ficha imprime Familia que o manual nao tem: {sobra}. '
                 f'Nenhuma Melhoria pertence a elas, e o jogador marca um quadrado vazio')
        if falta:
            erro(f'a ficha nao imprime Familia que o manual tem: {falta}. '
                 f'O jogador nao tem onde marcar ela como Livre ou Fechada')
        if not sobra and not falta:
            print(f'  [x] as 9 Familias da ficha sao as 9 do manual')
