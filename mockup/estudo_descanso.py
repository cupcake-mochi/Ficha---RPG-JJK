# -*- coding: utf-8 -*-
"""O estudo do descanso (09/10/2026): onde entra o menu de descanso na FICHA, e o que cada tipo faz. Desenhado como a
planilha, para comparar formas; o peso de cada caixa é o número de colunas que ela ocupa na aba de verdade."""
import sys

def cx(rot, val="", w=1, cls="", novo=True, sub=None, menu=False, h=34):
    v = f'<div class="val {cls}" style="height:{h}px">{val}{"<i>▾</i>" if menu else ""}</div>'
    s = f'<div class="sub">{sub}</div>' if sub else ""
    return f'<div class="cx {"novo" if novo else "velho"}" style="flex:{w}"><div class="rot">{rot}</div>{v}{s}</div>'
def linha(*c): return '<div class="linha">' + "".join(c) + "</div>"
def vao(w): return f'<div style="flex:{w}"></div>'
def forma(letra, titulo, corpo, obs): return f'<section><h3><em>{letra}</em> {titulo}</h3><div class="aba">{corpo}</div><p>{obs}</p></section>'
V = lambda *a, **k: cx(*a, novo=False, **k)
barra = lambda w, cheio: V("&nbsp;", f'<div class="barra"><div style="width:{cheio}%"></div></div>', w=w)

MENU = "Escolha o descanso"
ULTIMO = "Longo, fora de lugar propício · vida 3 → 11 · PE 8 → 30 · Integridade 18 → 25 · Sequelas 2 → 0 · Exaustão fica em 1"
atributos = lambda extra="": linha(*[V(n, v, w=7, cls="grande", h=52) for n, v in (("FOR", 3), ("DES", 0), ("CON", 0), ("INT", 0), ("ESS", 2))], extra or vao(10))
def barras():
    out = ""
    for nome, par, cheio in (("VIDA", "11 &nbsp;/&nbsp; 23", 48), ("ENERGIA", "30 &nbsp;/&nbsp; 60", 50), ("INTEGRIDADE", "25 &nbsp;/&nbsp; 25", 100)):
        out += linha(V(f"{nome} · ATUAL / MÁXIMA", par, w=10, cls="num"), V("Buff/Debuff", "0", w=2, cls="num"), barra(12, cheio),
                     V("TEMPORÁRIO", "0", w=6, cls="num"), V("± PERDA &/ou GANHO", "", w=6, cls="num"))
    return out + '<div class="tira">Alma Inteira</div>'
seq = lambda w: V("SEQUELAS", "0", w=w, cls="num", menu=True, sub="Próxima queda: 3 rodadas de janela", h=24)
exa = lambda w: V("EXAUSTÃO", "1", w=w, cls="num", menu=True, sub="Desvantagem em perícias e ofícios", h=24)
res = lambda w: V("RESISTÊNCIAS", "Fogo · Cortante (Alicerce)", w=w, cls="esq", h=46)
imu = lambda w: V("IMUNIDADES", "Envenenado", w=w, cls="esq", h=46)
estado = linha(seq(10), exa(10), res(10), imu(10))
descanso = lambda w: cx("DESCANSO", MENU, w=w, menu=True, h=30)

b1 = "".join([
    forma("A", "Uma linha própria, entre as barras e o estado",
          barras() + linha(descanso(10), cx("O ÚLTIMO DESCANSO", ULTIMO, w=32, cls="esq peq", h=30)) + estado,
          "O menu fica embaixo do que ele mexe (as barras) e em cima do que ele limpa (Sequelas e Exaustão). Ao lado, a ficha escreve o que o último descanso mudou, para você conferir ou desfazer à mão. A FICHA cresce três linhas."),
    forma("B", "Ao lado dos atributos, no espaço que hoje está vazio",
          atributos(cx("DESCANSO", MENU, w=10, menu=True, h=30, sub="Longo, fora · vida 3 → 11 · PE 8 → 30 · Sequelas 2 → 0")) + barras() + estado,
          "Não abre linha nenhuma: usa as dez colunas livres à direita da Essência, em cima da coluna do ±. O registro do último descanso cabe resumido, em letra pequena, embaixo do menu."),
    forma("C", "Na linha do estado, como a quinta caixa",
          barras() + linha(seq(8), exa(8), descanso(8), res(8), imu(8)),
          "Tudo o que é estado numa linha só, sem abrir linha. As cinco caixas ficam mais estreitas, o texto embaixo da Exaustão passa a quebrar em duas linhas, e não sobra lugar para o registro do último descanso (ele iria só no aviso do canto da tela)."),
])
tabela = '''<table>
<tr><th>O que você escolhe no menu</th><th>Vida</th><th>PE</th><th>Integridade</th><th>Sequelas</th><th>Exaustão</th></tr>
<tr><td><b>Curto · lugar propício</b></td><td>não muda</td><td>+25% do máximo</td><td>não muda</td><td>ficam</td><td>fica</td></tr>
<tr><td><b>Curto · fora</b></td><td>não muda</td><td>+25%, +15%, +5% ou nada, pelo degrau de Exaustão (0, 1, 2, 3)</td><td>não muda</td><td>ficam</td><td>fica</td></tr>
<tr><td><b>Longo · lugar propício</b></td><td>volta ao máximo</td><td>volta ao máximo</td><td>volta ao máximo</td><td>saem</td><td>sai</td></tr>
<tr><td><b>Longo · fora</b></td><td>vai à metade do máximo, se estiver abaixo</td><td>vai à metade do máximo, se estiver abaixo</td><td>volta ao máximo</td><td>saem</td><td>fica</td></tr>
</table>'''

html = f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Estudo do descanso</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Oswald:wght@400;500&family=Roboto:wght@400;500&display=swap">
<style>
:root{{--fundo:#0c0a14;--folha:#12101c;--painel:#1b1736;--rot:#3a2f70;--regua:#8475d8;--tinta:#ebe4dc;--fraca:#a59ec2;--novo:#e8b84a}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--fundo);color:var(--tinta);font-family:Roboto,sans-serif;padding:26px 30px 40px;width:1500px}}
h1{{font-family:Oswald,sans-serif;font-weight:500;font-size:26px;margin:0 0 4px}} .lede{{color:var(--fraca);font-size:15px;margin:0 0 6px;max-width:1150px;line-height:1.45}}
.leg{{font-size:13px;color:var(--fraca);margin:0 0 18px}} .leg b{{color:var(--novo);font-weight:500}}
h2{{font-family:Oswald,sans-serif;font-weight:500;font-size:19px;margin:26px 0 8px;border-top:1px solid #2a2547;padding-top:18px}}
h2 small{{font-family:Roboto,sans-serif;font-weight:400;font-size:13.5px;color:var(--fraca);margin-left:10px}}
.grade{{display:grid;gap:14px;align-items:start;grid-template-columns:1260px}}
h3{{font-family:Oswald,sans-serif;font-weight:400;font-size:15.5px;margin:10px 0 8px}} h3 em{{font-style:normal;background:var(--tinta);color:#12101c;border-radius:3px;padding:0 7px;margin-right:6px;font-weight:500}}
section p{{font-size:13.5px;color:var(--fraca);line-height:1.45;margin:6px 2px 0;max-width:1200px}}
.aba{{background:var(--folha);border:1px solid #262142;padding:12px 12px 4px}}
.linha{{display:flex;gap:28px;margin-bottom:10px}}
.cx{{min-width:0;display:flex;flex-direction:column}}
.rot{{background:var(--rot);border:2px solid var(--regua);font-family:Oswald,sans-serif;font-size:9.5px;letter-spacing:.3px;text-align:center;padding:2px 3px;white-space:nowrap;overflow:hidden}}
.val{{background:var(--painel);border:2px solid var(--regua);border-top:0;display:flex;align-items:center;justify-content:center;font-size:12.5px;padding:0 8px;overflow:hidden;position:relative;line-height:1.25}}
.val.num{{font-family:Oswald,sans-serif;font-size:17px}} .val.grande{{font-family:Oswald,sans-serif;font-size:26px}}
.val.esq{{justify-content:flex-start;text-align:left;font-size:12px}} .val.peq{{font-size:11.5px;color:var(--tinta)}}
.val i{{position:absolute;right:5px;font-style:normal;font-size:9px;color:var(--fraca)}}
.sub{{border:2px solid var(--regua);border-top:0;background:#151226;font-size:10px;color:var(--fraca);text-align:center;padding:3px 4px;line-height:1.25}}
.novo .rot,.novo .val,.novo .sub{{border-color:var(--novo)}} .novo .rot{{background:#5a4416}}
.tira{{background:var(--rot);border:2px solid var(--regua);font-size:11px;text-align:center;padding:2px;margin-bottom:10px}}
.barra{{width:100%;height:14px;background:#2a2547}} .barra div{{height:100%;background:var(--tinta)}}
table{{border-collapse:collapse;font-size:13.5px;max-width:1260px}} th,td{{border:1px solid #2f2950;padding:7px 10px;text-align:left;vertical-align:top}}
th{{font-family:Oswald,sans-serif;font-weight:400;background:#1b1736}} td b{{font-weight:500}}
</style></head><body>
<h1>Descanso · um menu que a ficha aplica</h1>
<p class="lede">Você escolhe o tipo no menu, o script faz a conta do livro nas caixas e o menu volta a ficar vazio, como a caixa de ±. Um aviso no canto da tela diz o que mudou. Os números de exemplo são os do livro: vida máxima 23 com saldo 3, e 60 PE com saldo 8, num descanso longo fora da base.</p>
<p class="leg"><b>Em âmbar:</b> o que é novo. Em roxo: o que a ficha já tem hoje.</p>
<h2>1 · O que cada tipo faz <small>pela tabela do livro</small></h2>{tabela}
<h2>2 · Onde o menu fica <small>na FICHA</small></h2><div class="grade">{b1}</div>
</body></html>'''
open(sys.argv[1], "w", encoding="utf-8").write(html)
