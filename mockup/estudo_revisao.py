# -*- coding: utf-8 -*-
"""O estudo da revisão (07/10/2026): onde entram as caixas novas. Desenhado como a planilha, para comparar formas."""
import sys
def cx(rot, val="", w=1, cls="", h=1, sub=None, menu=False, novo=True):
    v = f'<div class="val {cls}" style="height:{26 * h}px">{val}{"<i>▾</i>" if menu else ""}</div>'
    s = f'<div class="sub">{sub}</div>' if sub else ""
    return f'<div class="cx {"novo" if novo else "velho"}" style="flex:{w}"><div class="rot">{rot}</div>{v}{s}</div>'
def linha(*c): return '<div class="linha">' + "".join(c) + "</div>"
def faixa(n, t): return f'<div class="faixa"><b>{n}</b><span>{t}</span></div>' if n else f'<div class="faixa sem"><span>{t}</span></div>'
def forma(letra, titulo, corpo, obs): return f'<section><h3><em>{letra}</em> {titulo}</h3><div class="aba">{corpo}</div><p>{obs}</p></section>'
V = lambda *a, **k: cx(*a, novo=False, **k)

seq = cx("SEQUELAS", "1", menu=True, cls="num", w=3, sub="Próxima queda: 2 rodadas")
exa = cx("EXAUSTÃO", "2", menu=True, cls="num", w=4, sub="Desv. em perícias e ofícios · até 4,5 m")
res = cx("RESISTÊNCIAS", "Fogo · Cortante", w=4, cls="esq")
imu = cx("IMUNIDADES", "Envenenado", w=4, cls="esq")
barras = (linha(V("VIDA · ATUAL / MÁXIMA", "75 &nbsp;/&nbsp; 75", w=2, cls="num"), V("&nbsp;", '<div class="barra"></div>', w=3), V("TEMPORÁRIO", "0", cls="num"), V("± PERDA / GANHO", "", cls="num"))
          + '<div class="tira">Alma Inteira</div>')
registro = (linha(V("DEFESA", "11", cls="num"), V("PROTEÇÃO", "1", cls="num"), V("EQUIPAMENTO", "Traje 1"), V("INICIATIVA", "d20 + 0", cls="num"))
            + linha(V("MAESTRIA", "2", cls="num"), V("DESLOCAMENTO", "4,5 m", cls="num"), V("ATRIBUTO DE CONJURAÇÃO", "ESSÊNCIA", menu=True), V("ATRIBUTO DE ATAQUE", "FORÇA", menu=True)))

b1 = "".join([
    forma("A", "Uma linha embaixo das barras, na seção 2",
          faixa(2, "VALORES") + barras + linha(seq, exa, res, imu),
          "Tudo junto do que mede o corpo (vida, energia, integridade). A seção 2 cresce três linhas."),
    forma("B", "Uma linha no fim da seção 3, REGISTRO",
          faixa(3, "REGISTRO") + registro + linha(seq, exa, res, imu),
          "Fica ao lado do que elas mudam: a Exaustão mexe no deslocamento, a resistência anda com a Defesa. A seção 3 cresce três linhas."),
    forma("C", "Dividido: o estado com as barras, as proteções com a Defesa",
          faixa(2, "VALORES") + barras + linha(seq, exa, '<div style="flex:8"></div>') + '<div class="corte"></div>'
          + faixa(3, "REGISTRO") + registro + linha(res, imu),
          "Sequelas e Exaustão embaixo das barras; resistências e imunidades no fim do Registro. Cada coisa perto do que afeta, em dois lugares."),
])

perfil = linha(V("CAMINHO", "Bastião", menu=True), V("TRILHA", "Muro", menu=True), V("ORIGEM", "Latente", menu=True), V("NÍVEL", "10", cls="num"), V("XP", "0", cls="num"))
traco = cx("TRAÇO · UMA FRASE DA SUA HISTÓRIA", "Meu irmão entrou para a escola antes de mim e desapareceu numa missão.", w=5, cls="esq")
dossie_topo = linha(V("NOME", "Kaori", w=2), V("GRAU", "Grau 4", menu=True), V("IDADE", ""), V("ALTURA", ""))
b2 = "".join([
    forma("A", "Traço na FICHA, embaixo da Origem; cicatrizes na FICHA PESSOAL",
          faixa(1, "PERFIL AMALDIÇOADO") + perfil + linha(traco) + '<div class="corte"></div>' + faixa("", "DOSSIÊ · FICHA PESSOAL")
          + linha(V("APARÊNCIA", "", w=3, cls="esq"), cx("CICATRIZES", "Queimadura no antebraço esquerdo (2ª queda, missão do metrô)", w=2, cls="esq")),
          "O traço é uma das escolhas da Origem, e fica ao lado dela. A cicatriz é aparência, e divide a linha da Aparência."),
    forma("B", "Os dois no dossiê da FICHA PESSOAL",
          faixa("", "DOSSIÊ · FICHA PESSOAL") + dossie_topo
          + linha(V("APARÊNCIA", "", w=3, cls="esq"), cx("CICATRIZES", "Queimadura no antebraço esquerdo", w=2, cls="esq"))
          + linha(traco) + linha(V("HISTÓRIA", "O clã da Kaori perdeu o nome faz três gerações…", w=5, cls="esq", h=3)),
          "Tudo o que é história num lugar só. O traço entra como uma linha em cima da História, que perde duas linhas. A FICHA não muda."),
])

vida = linha(V("VIDA ATUAL", "19", cls="num"), V("VIDA MÁXIMA", "27", cls="num"), V("TEMPORÁRIA", "", cls="num"), V("± PERDA / GANHO", "", cls="num"), V("RESERVA DE PE", "", cls="num"))
bar = '<div class="barrinha"><div></div></div>'
b3 = "".join([
    forma("A", "Uma linha embaixo da barra de vida",
          vida + bar + linha(cx("ALMA", "Com alma", menu=True), cx("INTEGRIDADE ATUAL", "13", cls="num"), cx("INTEGRIDADE MÁXIMA", "13", cls="num"), cx("ESTÁGIO", "Alma inteira", w=2))
          + linha(V("CONDIÇÕES E USOS GASTOS", "", w=5, h=2)),
          "A máxima é metade da vida máxima (a regra das criaturas). Com <b>Sem alma</b> no menu as caixas ficam em “—” (corpo não autônomo). As Condições perdem três linhas."),
    forma("B", "Só duas caixas, sem estágio",
          vida + bar + linha(cx("ALMA", "Com alma", menu=True), cx("INTEGRIDADE ATUAL", "13", cls="num", w=2), cx("INTEGRIDADE MÁXIMA", "13", cls="num", w=2))
          + linha(V("CONDIÇÕES E USOS GASTOS", "", w=5, h=2)),
          "A mesma linha, mais enxuta: o estágio fica por conta do jogador conferir no livro."),
])

orc = linha(V("ESPAÇOS", "9", cls="num"), V("DO LEQUE", "0", cls="num"), V("EM TALENTOS", "2", cls="num"), V("NO DOMÍNIO", "0", cls="num"),
            cx("EM INVOCAÇÕES", "1", cls="num"), V("LIVRES", "6", cls="num"))
b4 = forma("", "Uma caixa nova no Orçamento da FICHA AMALDIÇOADA", faixa("", "ORÇAMENTO") + orc,
           "Conta sozinha as fichas da aba INVOCAÇÕES com nome e aquisição <b>Espaço conhecido</b> (cada uma ocupa uma vaga), e desconta dos livres. Não tem forma para escolher.")

html = f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Estudo da revisão</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Castoro&family=Oswald:wght@400;500&family=Roboto:wght@400;500&display=swap">
<style>
:root{{--fundo:#0c0a14;--folha:#12101c;--painel:#1b1736;--rot:#3a2f70;--regua:#8475d8;--tinta:#ebe4dc;--fraca:#a59ec2;--novo:#e8b84a}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--fundo);color:var(--tinta);font-family:Roboto,sans-serif;padding:26px 30px 40px;width:1560px}}
h1{{font-family:Oswald,sans-serif;font-weight:500;font-size:26px;margin:0 0 4px}} .lede{{color:var(--fraca);font-size:15px;margin:0 0 6px;max-width:1100px;line-height:1.45}}
.leg{{font-size:13px;color:var(--fraca);margin:0 0 22px}} .leg b{{color:var(--novo);font-weight:500}}
h2{{font-family:Oswald,sans-serif;font-weight:500;font-size:19px;margin:30px 0 4px;border-top:1px solid #2a2547;padding-top:18px}}
h2 small{{font-family:Roboto,sans-serif;font-weight:400;font-size:13.5px;color:var(--fraca);margin-left:10px}}
.grade{{display:grid;gap:22px;align-items:start}} .g3{{grid-template-columns:repeat(3,1fr)}} .g2{{grid-template-columns:repeat(2,1fr)}} .g1{{grid-template-columns:780px}}
h3{{font-family:Oswald,sans-serif;font-weight:400;font-size:15.5px;margin:10px 0 8px}} h3 em{{font-style:normal;background:var(--tinta);color:#12101c;border-radius:3px;padding:0 7px;margin-right:6px;font-weight:500}} h3 em:empty{{display:none}}
section p{{font-size:13.5px;color:var(--fraca);line-height:1.45;margin:8px 2px 0}} section p b{{color:var(--tinta);font-weight:500}}
.aba{{background:var(--folha);border:1px solid #262142;padding:12px 12px 14px}}
.faixa{{display:flex;margin:2px 0 8px}} .faixa b{{font-family:Oswald,sans-serif;font-weight:400;font-size:20px;width:38px;height:34px;display:flex;align-items:center;justify-content:center;background:var(--painel);border:2px solid var(--regua)}}
.faixa span{{flex:1;background:var(--rot);border:2px solid var(--regua);border-left:0;font-family:Oswald,sans-serif;font-size:13px;display:flex;align-items:center;padding-left:8px;letter-spacing:.3px}}
.faixa.sem span{{border-left:2px solid var(--regua);height:26px}}
.linha{{display:flex;gap:8px;margin-bottom:9px}}
.cx{{min-width:0;display:flex;flex-direction:column}}
.rot{{background:var(--rot);border:2px solid var(--regua);font-family:Oswald,sans-serif;font-size:9.5px;letter-spacing:.3px;text-align:center;padding:2px 3px;white-space:nowrap;overflow:hidden}}
.val{{background:var(--painel);border:2px solid var(--regua);border-top:0;display:flex;align-items:center;justify-content:center;font-size:12.5px;padding:0 6px;position:relative;overflow:hidden;text-align:center;line-height:1.25}}
.val.num{{font-family:Oswald,sans-serif;font-size:17px}} .val.esq{{justify-content:flex-start;text-align:left;font-size:12px}}
.val i{{position:absolute;right:4px;font-style:normal;font-size:9px;color:var(--fraca)}}
.sub{{border:2px solid var(--regua);border-top:0;background:#151226;font-size:10.5px;color:var(--fraca);text-align:center;padding:3px 4px;line-height:1.25}}
.novo .rot,.novo .val,.novo .sub{{border-color:var(--novo)}} .novo .rot{{background:#5a4416}}
.tira{{background:var(--rot);border:2px solid var(--regua);font-size:11px;text-align:center;padding:2px;margin-bottom:9px}}
.barra{{width:100%;height:12px;background:var(--tinta)}} .barrinha{{border:2px solid var(--regua);background:var(--painel);padding:2px;margin:-3px 0 9px}} .barrinha div{{height:9px;width:70%;background:var(--tinta)}}
.corte{{border-top:1px dashed #3a3460;margin:12px 0 10px}}
</style></head><body>
<h1>Revisão da ficha · onde entram as caixas novas</h1>
<p class="lede">Os itens que você escolheu: traço, sequelas, cicatrizes, exaustão, resistências e imunidades, Integridade da entidade com alma, e o espaço de feitiço ocupado por invocação. Cada bloco traz as formas para comparar; os números são de exemplo.</p>
<p class="leg"><b>Em âmbar:</b> o que é novo. Em roxo: o que a ficha já tem hoje, para dar o lugar.</p>
<h2>1 · Sequelas, Exaustão, resistências e imunidades <small>na FICHA</small></h2><div class="grade g3">{b1}</div>
<h2>2 · Traço e cicatrizes</h2><div class="grade g2">{b2}</div>
<h2>3 · Integridade da entidade com alma <small>na ficha de cada invocação</small></h2><div class="grade g2">{b3}</div>
<h2>4 · Espaço de feitiço ocupado por invocação</h2><div class="grade g1">{b4}</div>
</body></html>'''
open(sys.argv[1], "w", encoding="utf-8").write(html)
