# -*- coding: utf-8 -*-
"""O estudo das caixas de Buff/Debuff dos máximos (08/10/2026): onde a caixa entra na linha de cada barra da FICHA, e
ao lado da carga na FICHA PESSOAL. Desenhado como a planilha, para comparar formas; o peso de cada caixa é o número de
colunas que ela ocupa na aba de verdade."""
import sys

def cx(rot, val="", w=1, cls="", novo=True):
    return (f'<div class="cx {"novo" if novo else "velho"}" style="flex:{w}"><div class="rot">{rot}</div>'
            f'<div class="val {cls}">{val}</div></div>')
def linha(*c): return '<div class="linha">' + "".join(c) + "</div>"
def forma(letra, titulo, corpo, obs): return f'<section><h3><em>{letra}</em> {titulo}</h3><div class="aba">{corpo}</div><p>{obs}</p></section>'
V = lambda *a, **k: cx(*a, novo=False, **k)
def barra(w, cheio): return V("&nbsp;", f'<div class="barra"><div style="width:{cheio}%"></div></div>', w=w)

RECURSOS = (("VIDA", "25 &nbsp;/&nbsp; 28", "+5", 89), ("ENERGIA", "12 &nbsp;/&nbsp; 20", "0", 60), ("INTEGRIDADE", "18 &nbsp;/&nbsp; 20", "−5", 90))
def bloco(ordem):
    out = ""
    for nome, par, buff, cheio in RECURSOS:
        pecas = {"par": V(f"{nome} · ATUAL / MÁXIMA", par, w=10, cls="num"), "buff": cx("Buff/Debuff", buff, w=2, cls="num"),
                 "temp": V("TEMPORÁRIO", "0", w=6, cls="num")}
        out += linha(*[(barra(int(p[1:]), cheio) if p[0] == "b" and p[1:].isdigit() else
                        V("± PERDA &/ou GANHO", "", w=int(p[1:]), cls="num") if p[0] == "d" else pecas[p]) for p in ordem])
    return out

b1 = "".join([
    forma("A", "Logo depois do máximo, antes da barra", bloco(("par", "buff", "b12", "temp", "d6")),
          "A caixa fica colada no número que ela muda, como a de Buff/Debuff da Defesa e do deslocamento. A barra perde 3 das 15 colunas."),
    forma("B", "Depois da barra, antes do temporário", bloco(("par", "b12", "buff", "temp", "d6")),
          "O atual, o máximo e a barra continuam juntos, e a caixa abre o grupo das caixas de digitar. A barra perde as mesmas 3 colunas."),
    forma("C", "No fim da linha, depois da caixa de ±", bloco(("par", "b15", "temp", "d5", "buff")),
          "A barra fica inteira: a caixa usa as duas colunas livres do fim, e a de ± perde uma. Fica longe do máximo e colada na caixa de ±, que faz outra coisa (aplica e se limpa)."),
])
carga_hoje = linha(V("CARGA · LIMITE 5 + FORÇA", '<span class="n">6 de 8</span><div class="barra p"><div style="width:75%"></div></div>', w=10, cls="mista"),
                   V("IENES", "150000", w=7, cls="num"), V("SALÁRIO POR MÊS", "—", w=8, cls="num"))
carga_nova = linha(V("CARGA · LIMITE 5 + FORÇA", '<span class="n">6 de 10</span><div class="barra p"><div style="width:60%"></div></div>', w=8, cls="mista"),
                   cx("Buff/Debuff", "+2", w=2, cls="num"), V("IENES", "150000", w=7, cls="num"), V("SALÁRIO POR MÊS", "—", w=8, cls="num"))
b2 = "".join([forma("", "Hoje", carga_hoje, "A caixa da carga e a barra dela ocupam dez colunas, e a linha não tem coluna livre."),
              forma("", "Com a caixa", carga_nova, "A caixa entra no fim da carga, e a barra dela passa de 5 para 3 colunas. O limite vira 5 + Força + o que estiver na caixa. Não tem outra posição para escolher.")])

html = f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Estudo dos máximos</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Oswald:wght@400;500&family=Roboto:wght@400;500&display=swap">
<style>
:root{{--fundo:#0c0a14;--folha:#12101c;--painel:#1b1736;--rot:#3a2f70;--regua:#8475d8;--tinta:#ebe4dc;--fraca:#a59ec2;--novo:#e8b84a}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--fundo);color:var(--tinta);font-family:Roboto,sans-serif;padding:26px 30px 40px;width:1500px}}
h1{{font-family:Oswald,sans-serif;font-weight:500;font-size:26px;margin:0 0 4px}} .lede{{color:var(--fraca);font-size:15px;margin:0 0 6px;max-width:1100px;line-height:1.45}}
.leg{{font-size:13px;color:var(--fraca);margin:0 0 18px}} .leg b{{color:var(--novo);font-weight:500}}
h2{{font-family:Oswald,sans-serif;font-weight:500;font-size:19px;margin:26px 0 4px;border-top:1px solid #2a2547;padding-top:18px}}
h2 small{{font-family:Roboto,sans-serif;font-weight:400;font-size:13.5px;color:var(--fraca);margin-left:10px}}
.grade{{display:grid;gap:14px;align-items:start}} .g1{{grid-template-columns:1260px}} .g2{{grid-template-columns:repeat(2,730px)}}
h3{{font-family:Oswald,sans-serif;font-weight:400;font-size:15.5px;margin:10px 0 8px}} h3 em{{font-style:normal;background:var(--tinta);color:#12101c;border-radius:3px;padding:0 7px;margin-right:6px;font-weight:500}} h3 em:empty{{display:none}}
section p{{font-size:13.5px;color:var(--fraca);line-height:1.45;margin:6px 2px 0}}
.aba{{background:var(--folha);border:1px solid #262142;padding:12px 12px 4px}}
.linha{{display:flex;gap:28px;margin-bottom:10px}}
.cx{{min-width:0;display:flex;flex-direction:column}}
.rot{{background:var(--rot);border:2px solid var(--regua);font-family:Oswald,sans-serif;font-size:9.5px;letter-spacing:.3px;text-align:center;padding:2px 3px;white-space:nowrap;overflow:hidden}}
.val{{background:var(--painel);border:2px solid var(--regua);border-top:0;display:flex;align-items:center;justify-content:center;font-size:12.5px;padding:0 6px;height:34px;overflow:hidden}}
.val.num{{font-family:Oswald,sans-serif;font-size:17px}}
.val.mista{{gap:12px;justify-content:flex-start}} .val.mista .n{{font-family:Oswald,sans-serif;font-size:16px;white-space:nowrap;padding:0 6px}}
.novo .rot,.novo .val{{border-color:var(--novo)}} .novo .rot{{background:#5a4416}}
.barra{{width:100%;height:14px;background:#2a2547}} .barra div{{height:100%;background:var(--tinta)}} .barra.p{{flex:1}}
</style></head><body>
<h1>Buff/Debuff dos máximos · onde a caixa entra</h1>
<p class="lede">Uma caixa para somar ou tirar do máximo de vida, de energia, de Integridade e do limite de carga (a lapidação, uma habilidade de técnica, o custo de Insistir numa queda). O máximo passa a ser a conta do livro mais o que estiver na caixa, e aceita número negativo. Os números são de exemplo: vida 23 do livro com +5, Integridade 25 com −5.</p>
<p class="leg"><b>Em âmbar:</b> o que é novo. Em roxo: o que a ficha já tem hoje. A largura de cada caixa segue as colunas da aba de verdade.</p>
<h2>1 · Vida, energia e Integridade <small>na FICHA, na linha de cada barra</small></h2><div class="grade g1">{b1}</div>
<h2>2 · Limite de carga <small>na FICHA PESSOAL</small></h2><div class="grade g2">{b2}</div>
</body></html>'''
open(sys.argv[1], "w", encoding="utf-8").write(html)
