# -*- coding: utf-8 -*-
"""O estudo das Origens do R45 (14/10/2026, B46). Desenhado como a planilha, com os menus funcionando, para comparar
formas antes de construir. Três perguntas, uma de cada vez na página:

  1. o bloco ORIGEM no dossiê da FICHA PESSOAL (marcante e duas menores, do livro ou criadas com o mestre);
  2. o painel retrátil à direita da FICHA, com tudo o que a Origem oferece;
  3. a linha do Morrendo embaixo da vida.

Os dados saem do livro (LIVRO-COMPLETO.md do JJK---Project, capítulo 5), lidos aqui mesmo: é rascunho de estudo, o
extrator de verdade vem na construção.

Uso: python3 mockup/estudo_origens.py <LIVRO-COMPLETO.md> <saida.html>"""
import json, re, sys, html as H

LIVRO, SAIDA = sys.argv[1], sys.argv[2]
L = open(LIVRO, encoding="utf-8").read().splitlines()
ini = L.index("## 5. Origens")
fim = L.index("### Personalizar sua Origem")


def limpa(s):
    s = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", s)
    return s.replace("`", "").strip()


def negrito(s):
    s = H.escape(s)
    return re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", s)


# --- o capítulo em árvore: Origem (###) > seção (####) > capacidade (#####)
cap = {}
cur = sec = cc = None
for l in L[ini:fim]:
    if l.startswith("<") or l.startswith("|---"):
        continue
    m = re.match(r"^(#{3,6}) (.+)$", l)
    if m:
        n, t = len(m.group(1)), m.group(2)
        if n == 3:
            cur = t; cap[cur] = {"intro": [], "secoes": []}; sec = cc = None
        elif n == 4 and cur:
            sec = {"titulo": t, "texto": [], "caps": []}; cap[cur]["secoes"].append(sec); cc = None
        elif n == 5 and sec is not None:
            cc = {"nome": t, "texto": []}; sec["caps"].append(cc)
        continue
    if not l.strip() or cur is None:
        continue
    l = limpa(l)
    if l.startswith("**Legados de história:**"):
        (sec if sec else cap[cur])["legados"] = l.split(":**", 1)[1].strip(); continue
    if l.startswith("**Perícia da Origem:**"):
        (sec if sec else cap[cur])["pericia"] = l; continue
    (cc["texto"] if cc else (sec["texto"] if sec else cap[cur]["intro"])).append(l)


def secao(o, t):
    return next(s for s in cap[o]["secoes"] if s["titulo"] == t)


def texto_da_secao(s):
    partes = [" ".join(s["texto"])] + [f'**{c["nome"]}.** ' + " ".join(c["texto"]) for c in s["caps"]]
    return "\n\n".join(p for p in partes if p.strip())


def primeira_frase(t):
    t = re.sub(r"\s+", " ", t)
    m = re.match(r"(.+?[.!?])(\s|$)", t)
    return m.group(1) if m else t


def frequencia(t):
    m = re.search(r"\*\*((Uma|Duas) vez(es)? [^*]+|Maestria vezes por [^*]+|metade da Constituição[^*]+)\*\*", t)
    if m:
        return m.group(1).rstrip(",. ")
    for p in ("Uma vez por dia", "Uma vez por cena", "Uma vez por descanso longo", "Uma vez por descanso curto",
              "Maestria vezes por dia", "Maestria vezes por cena", "Duas vezes por cena"):
        if p.lower() in t.lower():
            return p
    return "Passiva"


def menores(o, titulo, extra=None):
    out = []
    for c in secao(o, titulo)["caps"]:
        t = " ".join(c["texto"])
        ex = re.match(r"\*\*(Exclusiva \w+|Requisito: \w+)\.(\*\*)?\s*", t)
        resto = (t[ex.end():] if ex.group(2) else "**" + t[ex.end():]) if ex else t
        fq = frequencia(resto)
        rs = re.sub(r"\*\*", "", resto)
        rs = re.sub(r"^" + re.escape(fq) + r"[,.]?\s*", "", rs, flags=re.I) if fq != "Passiva" else rs
        out.append({"nome": c["nome"], "texto": t, "freq": fq, "resumo": primeira_frase(rs[:1].upper() + rs[1:]),
                    "extra": extra or (ex.group(1).lower().replace("requisito: ", "exige ") if ex else None)})
    return out


def marcante(nome, t, comp=None):
    return {"nome": nome, "texto": t, "freq": frequencia(t), "comp": comp or []}


def pericias(o, ramo=None):
    p = cap[o].get("pericia", "")
    if ramo:
        s = secao(o, ramo)
        p = s.get("pericia", p)
    m = re.search(r"escolha ([^.]+)\.", p)
    return m.group(1) if m else ""


ORIG = {}
for o, m in (("Latente", "Tentativa e Erro"), ("Encarnado", "Duas Vidas"), ("Híbrido", "Regeneração Orgânica")):
    s = secao(o, m)
    ORIG[o] = {"marcantes": [marcante(m, texto_da_secao(s))], "menores": menores(o, f"Menores do {o}"),
               "pericias": pericias(o), "legados": cap[o]["legados"], "rota": "Fundamento (ou Manejos, com Sem Técnica)"}
ORIG["Receptáculo"] = {
    "marcantes": [marcante(f"Coexistência", texto_da_secao(secao("Receptáculo", "Coexistência")),
                           [c["nome"] for c in secao("Receptáculo", "Coexistência")["caps"]]),
                  marcante(f"Conflito", texto_da_secao(secao("Receptáculo", "Conflito")),
                           [c["nome"] for c in secao("Receptáculo", "Conflito")["caps"]])],
    "menores": menores("Receptáculo", "Menores do Receptáculo"), "pericias": pericias("Receptáculo"),
    "legados": cap["Receptáculo"]["legados"], "rota": "Fundamento (ou Manejos, com Sem Técnica)"}
cla = []
for c in ("Zenin", "Kamo", "Gojo", "Inumaki"):
    s = secao("Descendente", c)
    if c == "Zenin":
        cla += [marcante("Zenin · Akashi", texto_da_secao(s), [x["nome"] for x in s["caps"]]),
                marcante("Zenin · Kukuru (Sem Técnica)", texto_da_secao(s), [x["nome"] for x in s["caps"]])]
    else:
        cla.append(marcante(c, texto_da_secao(s), [x["nome"] for x in s["caps"]]))
ORIG["Descendente"] = {"marcantes": cla, "menores": menores("Descendente", "Menores do Descendente"),
                       "pericias": pericias("Descendente"), "legados": cap["Descendente"]["legados"],
                       "rota": "Fundamento (ou Manejos, com Sem Técnica)"}
ea = secao("Corpo Amaldiçoado", "Existência Artificial")
hist = secao("Corpo Amaldiçoado", "Histórias do corpo")
ORIG["Corpo Amaldiçoado"] = {
    "marcantes": [marcante("Existência Artificial", texto_da_secao(ea), [c["nome"] for c in ea["caps"]])],
    "menores": menores("Corpo Amaldiçoado", "Menores do Corpo Amaldiçoado")
               + menores("Corpo Amaldiçoado", "Menores de Manutenção", extra="só com a história Manutenção"),
    "pericias": pericias("Corpo Amaldiçoado"), "legados": " ".join(hist["texto"]),
    "rota": "Técnica Marcial, com energia", "oficio": True}
asp = secao("Restrição Celestial", "Ataque sem Prenúncio")
ORIG["Restrição Celestial · Sem Energia"] = {
    "marcantes": [marcante("Ataque sem Prenúncio", texto_da_secao(asp), [c["nome"] for c in asp["caps"]])],
    "menores": menores("Restrição Celestial", "Menores de Sem Energia"),
    "pericias": pericias("Restrição Celestial", "Sem Energia"), "legados": secao("Restrição Celestial", "Sem Energia")["legados"], "rota": "Técnica Marcial, sem energia"}
saida = texto_da_secao(secao("Restrição Celestial", "Saída Elevada"))
corpos = [marcante(c, texto_da_secao(secao("Restrição Celestial", c)) + "\n\n**Saída Elevada.** " + saida,
                   ["Talento de Categoria de Efeito 4", "Saída Elevada", c])
          for c in ("Corpo Debilitado", "Corpo Quebradiço", "Corpo Exaurido")]
rc = secao("Restrição Celestial", "Restrição corporal")
ORIG["Restrição Celestial · Restrição corporal"] = {
    "marcantes": corpos, "menores": menores("Restrição Celestial", "Menores da Restrição corporal"),
    "pericias": pericias("Restrição Celestial", "Restrição corporal"),
    "legados": rc["legados"],
    "rota": "Fundamento", "ce4": True}
ORDEM = ["Latente", "Receptáculo", "Descendente", "Encarnado", "Híbrido", "Corpo Amaldiçoado",
         "Restrição Celestial · Sem Energia", "Restrição Celestial · Restrição corporal"]
n_menores = {o: len(ORIG[o]["menores"]) for o in ORDEM}
assert sum(n_menores.values()) == 67, n_menores

DADOS = json.dumps({"ordem": ORDEM, "orig": ORIG}, ensure_ascii=False)

PAGINA = r'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Estudo das Origens</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Oswald:wght@400;500&family=Roboto:wght@400;500&display=swap">
<style>
:root{--fundo:#0c0a14;--folha:#12101c;--painel:#1b1736;--rot:#3a2f70;--regua:#8475d8;--tinta:#ebe4dc;--fraca:#a59ec2;--novo:#e8b84a;--novo-f:#5a4416}
*{box-sizing:border-box} body{margin:0;background:var(--fundo);color:var(--tinta);font-family:Roboto,sans-serif;padding:24px 28px 60px;min-width:1320px}
h1{font-family:Oswald,sans-serif;font-weight:500;font-size:26px;margin:0 0 4px} .lede{color:var(--fraca);font-size:15px;margin:0 0 6px;max-width:1180px;line-height:1.45}
.leg{font-size:13px;color:var(--fraca);margin:0 0 14px} .leg b{color:var(--novo);font-weight:500}
h2{font-family:Oswald,sans-serif;font-weight:500;font-size:20px;margin:30px 0 6px;border-top:1px solid #2a2547;padding-top:18px}
h2 small{font-family:Roboto,sans-serif;font-weight:400;font-size:13.5px;color:var(--fraca);margin-left:10px}
.botoes{display:flex;gap:8px;margin:8px 0 10px;flex-wrap:wrap} .botoes button{font-family:Oswald,sans-serif;font-size:14px;background:#1b1736;color:var(--tinta);border:1px solid #3d3566;border-radius:4px;padding:6px 12px;cursor:pointer}
.botoes button.on{background:var(--tinta);color:#12101c;border-color:var(--tinta)}
.expl{font-size:13.5px;color:var(--fraca);line-height:1.5;margin:6px 2px 10px;max-width:1240px}
.expl b{color:var(--tinta);font-weight:500}
.aba{background:var(--folha);border:1px solid #262142;padding:12px 14px 6px;position:relative}
.cols{display:flex;font-family:Roboto,sans-serif;font-size:9px;color:#5d5680;margin:0 0 6px 0;gap:0}
.linha{display:flex;gap:14px;margin-bottom:10px;align-items:flex-start}
.cx{min-width:0;display:flex;flex-direction:column}
.rot{background:var(--rot);border:2px solid var(--regua);font-family:Oswald,sans-serif;font-size:10px;letter-spacing:.3px;text-align:center;padding:2px 3px;white-space:nowrap;overflow:hidden}
.val{background:var(--painel);border:2px solid var(--regua);border-top:0;display:flex;align-items:center;justify-content:center;font-size:12.5px;padding:3px 8px;position:relative;line-height:1.3;min-height:26px}
.val.num{font-family:Oswald,sans-serif;font-size:17px} .val.esq{justify-content:flex-start;text-align:left}
.val.txt{display:block;text-align:left;font-size:11.5px;white-space:pre-wrap;color:var(--tinta)}
.val.txt.calc{color:#d9d2ea} .val.txt textarea{width:100%;min-height:70px;background:transparent;border:1px dashed #6c5fb8;color:var(--tinta);font:inherit;resize:vertical}
.val select,.val input{width:100%;background:transparent;color:var(--tinta);border:0;font:inherit;font-size:12.5px;appearance:none;cursor:pointer;outline:none;text-align:inherit}
.val select option{background:#1b1736}
.val i.m{position:absolute;right:5px;font-style:normal;font-size:9px;color:var(--fraca);pointer-events:none}
.val i.f{position:absolute;left:4px;top:2px;font-style:normal;font-size:9px;color:var(--fraca)}
.sub{border:2px solid var(--regua);border-top:0;background:#151226;font-size:10.5px;color:var(--fraca);text-align:center;padding:3px 4px;line-height:1.3}
.novo>.rot,.novo>.val,.novo>.sub{border-color:var(--novo)} .novo>.rot{background:var(--novo-f)}
.etq{display:inline-block;font-size:9.5px;font-family:Oswald,sans-serif;padding:0 5px;border-radius:2px;margin-left:6px;vertical-align:1px}
.etq.livro{background:#3a2f70;color:#d8d0ff} .etq.criada{background:var(--novo);color:#1b1408}
.vel{opacity:.55}
.tit{background:var(--rot);border:2px solid var(--regua);font-family:Oswald,sans-serif;font-size:13px;letter-spacing:.6px;padding:3px 10px;margin:4px 0 10px;display:flex;justify-content:space-between}
.tit span:last-child{color:var(--fraca);font-size:11px;font-family:Roboto,sans-serif;letter-spacing:0}
/* a FICHA com o grupo de colunas à direita */
.ficha{display:flex;align-items:flex-start;gap:0}
.ficha .folha{width:760px;flex:none}
.calha{width:26px;flex:none;align-self:stretch;border-left:1px solid #2a2547;border-right:1px solid #2a2547;background:#0f0d18;display:flex;flex-direction:column;align-items:center;padding-top:6px}
.calha button{width:18px;height:18px;padding:0;border:1px solid #6c5fb8;background:#1b1736;color:var(--tinta);font-size:13px;line-height:14px;cursor:pointer;border-radius:2px}
.calha .traco{flex:1;width:2px;background:#6c5fb8;margin:4px 0 8px}
.painel{width:520px;flex:none;padding:0 0 0 14px}
.painel.fechado{display:none}
.card{border:2px solid var(--regua);background:var(--painel);margin-bottom:8px}
.card.esc{border-color:var(--novo)} .card .cab{background:var(--rot);font-family:Oswald,sans-serif;font-size:11.5px;padding:2px 7px;display:flex;justify-content:space-between;gap:6px}
.card.esc .cab{background:var(--novo-f)} .card .cab em{font-style:normal;color:var(--fraca);font-family:Roboto,sans-serif;font-size:10px;white-space:nowrap}
.card .corpo{font-size:11px;line-height:1.35;padding:4px 7px;color:#d9d2ea;white-space:pre-wrap}
.grade2{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.lista{font-size:11.5px;line-height:1.45} .lista div{display:flex;gap:8px;border-bottom:1px solid #2a2547;padding:3px 2px}
.lista div b{font-weight:500;min-width:170px} .lista div span{color:var(--fraca)} .lista div.esc b{color:var(--novo)}
.lista div.esc b:before{content:"✓ ";}
.barra{width:100%;height:14px;background:#2a2547} .barra div{height:100%;background:var(--tinta)}
.morre{font-size:12.5px;line-height:1.5}
.mk{display:inline-flex;width:20px;height:20px;border:2px solid var(--tinta);align-items:center;justify-content:center;font-size:13px;cursor:pointer;background:#0f0d18}
.mk.on{background:#8b2c3a;border-color:#e2a0aa}
.morre b{font-family:Oswald,sans-serif;font-weight:500;font-size:15px}
.contas{font-size:12.5px;color:var(--fraca);margin:6px 2px 0;line-height:1.55}
.contas code{color:var(--tinta);font-family:Roboto Mono,monospace;font-size:12px}
table.comp{border-collapse:collapse;font-size:13px;margin-top:8px;max-width:1260px} table.comp th,table.comp td{border:1px solid #2f2950;padding:6px 9px;text-align:left;vertical-align:top}
table.comp th{font-family:Oswald,sans-serif;font-weight:400;background:#1b1736}
.ctrl{display:flex;gap:16px;align-items:center;font-size:13px;color:var(--fraca);margin:6px 0 10px;flex-wrap:wrap}
.ctrl select,.ctrl input{background:#1b1736;color:var(--tinta);border:1px solid #3d3566;border-radius:3px;padding:3px 6px;font:inherit}
</style></head><body>
<h1>Origens do R45 · estudo, rodada 2</h1><p class="lede"><b>Rodada 2 (14/10):</b> as formas que você escolheu (1A, 2B só com as suas escolhas, 3A com o prazo explicado e as Sequelas em caixinhas de marcar). Os botões das outras formas continuam aí, se quiser comparar.</p>
<p class="lede">Os menus funcionam: escolha a Origem logo abaixo e as caixas trocam junto, nas três perguntas. Os dados saem do capítulo 5 do livro R51: 8 catálogos e 67 menores. Toda caixa de capacidade tem, no fim do menu, a opção <b>✎ Criada com o mestre</b>, e nas formas A e B também dá pra escrever um nome que não está na lista. Com uma das duas, a caixa de texto embaixo fica livre pra você escrever a versão criada.</p>
<p class="leg"><b>Em âmbar:</b> o que é novo. Em roxo: o que a ficha já tem hoje. <span class="etq livro">DO LIVRO</span> <span class="etq criada">CRIADA</span> marcam de onde veio cada capacidade.</p>
<div class="ctrl">Origem na FICHA: <select id="origem"></select>
  <label><input type="checkbox" id="semtec"> Sem Técnica</label>
  <span id="aviso-st"></span></div>

<h2>1 · O bloco ORIGEM no dossiê <small>FICHA PESSOAL, no lugar dos dois Legados</small></h2>
<div class="botoes" id="b1"></div><div class="expl" id="e1"></div><div class="aba" id="dossie"></div>

<h2>2 · O painel retrátil à direita da FICHA <small>um grupo de colunas depois da AU, que nasce fechado</small></h2>
<div class="botoes" id="b2"></div><div class="expl" id="e2"></div><div class="aba"><div class="ficha" id="ficha"></div></div>

<h2>3 · O Morrendo embaixo da vida <small>FICHA, calculado da vida máxima e da maior Classe</small></h2>
<div class="ctrl">Vida máxima <input id="vmax" type="number" value="93" style="width:70px"> Maior Classe <input id="classe" type="number" value="3" min="0" max="7" style="width:50px"> · clique nas caixinhas das Sequelas para marcar</div>
<div class="botoes" id="b3"></div><div class="expl" id="e3"></div><div class="aba" id="morre"></div>
<p class="contas" id="contas"></p>

<h2>Lado a lado</h2>
<table class="comp">
<tr><th></th><th>A</th><th>B</th><th>C</th></tr>
<tr><td><b>1 · Dossiê</b></td><td>três cartas lado a lado, com o texto embaixo de cada uma</td><td>três faixas de ponta a ponta, uma embaixo da outra, com o nome à esquerda e o texto à direita</td><td>três linhas finas, só nome e frequência, com o texto inteiro na nota</td></tr>
<tr><td><b>2 · Painel</b></td><td>as cartas inteiras numa coluna, com as suas escolhas em âmbar</td><td>a sua escolha em cima, com as outras numa lista de uma linha cada</td><td>em duas colunas: a base e a marcante à esquerda, as menores em grade à direita</td></tr>
<tr><td><b>3 · Morrendo</b></td><td>três caixas de número, cada uma com o rótulo do que significa</td><td>uma faixa com a frase inteira, sem caixa</td><td>dentro da caixa das Sequelas, junto da janela</td></tr>
</table>
<p class="expl"><b>Minha indicação:</b> 1A, 2B e 3A. Na 1A o texto de cada capacidade fica à vista no dossiê, que é onde o jogador lê com calma. A 2B põe na mesa o que você já tem, e o resto aparece só como lista pra consulta. A 3A diz o número e o que ele significa sem precisar ler frase.</p>

<script>
const D = __DADOS__;
const OP_CRIADA = "✎ Criada com o mestre";
const st = {origem: "Descendente", semtec: false, f1: "A", f2: "B", f3: "A", seq: 1,
  esc: {marcante: "Zenin · Akashi", m1: "Notas de Família", m2: OP_CRIADA},
  livre: {marcante: "", m1: "", m2: "Treino de lâmina com o tio: uma vez por cena, depois de errar um ataque com Lâmina Longa, rerrole o d20 e aceite o segundo resultado."},
  nomeLivre: {m2: "Lição do Tio Kenji"}, painel: true, oficio: "Entalhador", legados: "O tio Kenji, que me ensinou a lâmina escondido do resto da casa. Ele ainda me deve uma explicação sobre a ferramenta que sumiu do cofre."};
const esc = s => s.replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const neg = s => esc(s).replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>");
function O() { return D.orig[st.origem]; }
function itens(slot) { return slot === "marcante" ? O().marcantes : O().menores; }
function achado(slot) { return itens(slot).find(x => x.nome === st.esc[slot]); }
function criada(slot) { return !achado(slot); }
function nomeDe(slot) { const a = achado(slot); if (a) return a.nome; return st.esc[slot] === OP_CRIADA ? (st.nomeLivre[slot] || "") : st.esc[slot]; }
function freqDe(slot) { const a = achado(slot); return a ? a.freq : "escrita por você"; }

// --- os controles do topo
const so = document.getElementById("origem");
D.ordem.forEach(o => so.add(new Option(o, o)));
so.value = st.origem;
so.onchange = () => { st.origem = so.value; st.esc = {marcante: O().marcantes[0].nome, m1: O().menores[0].nome, m2: O().menores[1].nome};
  st.livre = {marcante: "", m1: "", m2: ""}; st.nomeLivre = {}; tudo(); };
document.getElementById("semtec").onchange = e => { st.semtec = e.target.checked; tudo(); };

function botoes(id, chave, nomes) {
  const b = document.getElementById(id); b.innerHTML = "";
  Object.entries(nomes).forEach(([k, t]) => { const x = document.createElement("button"); x.textContent = k + " · " + t;
    x.className = st[chave] === k ? "on" : ""; x.onclick = () => { st[chave] = k; tudo(); }; b.appendChild(x); });
}

// --- uma caixa de menu de capacidade
function menuCap(slot, rotulo, larg) {
  const lista = itens(slot).map(x => x.nome + (x.extra ? "  (" + x.extra + ")" : ""));
  const nomes = itens(slot).map(x => x.nome);
  const val = st.esc[slot];
  let opts = nomes.map((n, i) => `<option value="${esc(n)}" ${n === val ? "selected" : ""}>${esc(lista[i])}</option>`).join("");
  opts += `<option value="${OP_CRIADA}" ${val === OP_CRIADA ? "selected" : ""}>${OP_CRIADA}</option>`;
  if (!nomes.includes(val) && val !== OP_CRIADA) opts += `<option selected>${esc(val)}</option>`;
  return `<div class="cx novo" style="flex:${larg}"><div class="rot">${rotulo}</div>
    <div class="val esq"><select data-slot="${slot}">${opts}</select><i class="m">▾</i></div></div>`;
}
function nomeCriado(slot, larg) {
  if (!criada(slot) || st.esc[slot] !== OP_CRIADA) return "";
  return `<div class="cx novo" style="flex:${larg}"><div class="rot">NOME DA CRIADA</div>
    <div class="val esq"><input data-nome="${slot}" value="${esc(st.nomeLivre[slot] || "")}" placeholder="escreva o nome"></div></div>`;
}
function textoCap(slot, minh) {
  const a = achado(slot);
  if (a) return `<div class="val txt calc" style="min-height:${minh}px"><i class="f">ƒ</i>${neg(a.texto)}</div>`;
  return `<div class="val txt" style="min-height:${minh}px"><textarea data-livre="${slot}" placeholder="Escreva o que ela faz, quando funciona, a ação, o custo e a frequência, como combinado com o mestre.">${esc(st.livre[slot] || "")}</textarea></div>`;
}
function etiqueta(slot) { return criada(slot) ? '<span class="etq criada">CRIADA</span>' : '<span class="etq livro">DO LIVRO</span>'; }
const ROT = {marcante: "MARCANTE", m1: "MENOR 1", m2: "MENOR 2"};

function extras() {
  let out = "";
  const o = O();
  const cx = [];
  cx.push(`<div class="cx novo" style="flex:30"><div class="rot">LEGADOS DE HISTÓRIA · SEM EFEITO NA FICHA</div>
    <div class="val txt" style="min-height:44px"><textarea id="legados" style="min-height:40px" placeholder="${esc(o.legados)}">${esc(st.legados)}</textarea></div></div>`);
  if (o.oficio) cx.push(`<div class="cx novo" style="flex:10"><div class="rot">OFÍCIO COMPATÍVEL</div><div class="val"><select>${["Entalhador","Forja","Alfaiate","Caligrafia","Condução","Arrombamento","Herbalismo","Burocracia","Culinária","Instrumento","Jogatina"].map(x=>`<option>${x}</option>`).join("")}</select><i class="m">▾</i></div><div class="sub">aceita outro: escreva por cima</div></div>`);
  if (o.ce4) cx.push(`<div class="cx novo" style="flex:14"><div class="rot">TALENTO DE CATEGORIA DE EFEITO 4</div><div class="val txt" style="min-height:44px"><textarea style="min-height:40px" placeholder="O que a exceção permite, os limites e as consequências, combinados com o mestre (Rede Remota é o exemplo do livro)."></textarea></div></div>`);
  return `<div class="linha">${cx.join("")}</div>`;
}
function cabecalhoOrigem() {
  const o = O();
  const st_ = st.semtec ? " · Sem Técnica" : "";
  return `<div class="linha">
    <div class="cx" style="flex:14"><div class="rot">ORIGEM</div><div class="val">${esc(st.origem + st_)}</div><div class="sub">vem da FICHA</div></div>
    <div class="cx" style="flex:22"><div class="rot">PERÍCIA DA ORIGEM · UMA DESTAS</div><div class="val">${esc(o.pericias)}</div><div class="sub">o treino é marcado na FICHA</div></div>
    <div class="cx" style="flex:14"><div class="rot">ROTA DE CRIAÇÃO</div><div class="val">${st.semtec ? "Manejos (Sem Técnica)" : esc(o.rota)}</div><div class="sub">${st.semtec ? "não ocupa marcante nem menor" : "vem da Origem"}</div></div></div>`;
}

const F1 = {A: "cartas lado a lado", B: "faixas de ponta a ponta", C: "linhas finas, texto na nota"};
const E1 = {
  A: "As três caixas dividem a largura do dossiê. Cada uma tem o menu com o nome, a etiqueta de onde veio e o texto do livro embaixo, que estica com o tamanho. Ao escolher <b>✎ Criada com o mestre</b>, aparece a caixa do nome e o texto vira uma caixa livre (a ficha guarda a conta e a devolve se você voltar a uma do livro, como as outras caixas calculadas). <b>Preço:</b> o dossiê cresce, porque o texto mais comprido do livro (Ataque sem Prenúncio) tem perto de 3.900 letras; numa carta de um terço da largura isso dá muitas linhas.",
  B: "Cada capacidade ocupa a largura inteira: o nome e a frequência numa coluna estreita à esquerda, o texto à direita. É a forma mais fácil de ler texto longo, e a altura fica parecida entre as três. <b>Preço:</b> o bloco desce bastante na página, e as três ficam uma embaixo da outra, sem a vista de conjunto.",
  C: "Só uma linha por capacidade: o menu, a etiqueta e a frequência. O texto inteiro vai na nota da caixa (passando o mouse) e no painel da FICHA. Na criada, o texto livre fica numa caixa curta ao lado. <b>Preço:</b> no celular a nota quase não abre, e a criada fica com pouco espaço pra escrever."
};
function dossie() {
  let corpo = `<div class="tit"><span>ORIGEM</span><span>a base, a marcante e as duas menores</span></div>` + cabecalhoOrigem();
  const slots = ["marcante", "m1", "m2"];
  if (st.f1 === "A") {
    corpo += `<div class="linha">` + slots.map(s => `<div class="cx" style="flex:1">${menuCap(s, ROT[s] + " " + etiqueta(s), 1)}${nomeCriado(s, 1)}<div class="cx novo">${textoCap(s, 150)}</div><div class="sub" style="border-color:var(--novo)">${esc(freqDe(s))}</div></div>`).join("") + `</div>`;
  } else if (st.f1 === "B") {
    corpo += slots.map(s => `<div class="linha"><div class="cx" style="flex:12">${menuCap(s, ROT[s] + " " + etiqueta(s), 1)}${nomeCriado(s, 1)}<div class="sub" style="border-color:var(--novo)">${esc(freqDe(s))}</div></div><div class="cx novo" style="flex:36"><div class="rot">O QUE FAZ</div>${textoCap(s, 70)}</div></div>`).join("");
  } else {
    corpo += slots.map(s => `<div class="linha"><div style="flex:14;display:flex;flex-direction:column">${menuCap(s, ROT[s] + " " + etiqueta(s), 1)}</div>${nomeCriado(s, 10)}<div class="cx novo" style="flex:12"><div class="rot">FREQUÊNCIA</div><div class="val">${esc(freqDe(s))}</div></div>${criada(s) ? `<div class="cx novo" style="flex:22"><div class="rot">O QUE FAZ</div>${textoCap(s, 40)}</div>` : `<div class="cx" style="flex:22"><div class="rot">O QUE FAZ</div><div class="val esq" style="color:var(--fraca)">o texto do livro está na nota desta caixa ▸</div></div>`}</div>`).join("");
  }
  corpo += extras();
  document.getElementById("dossie").innerHTML = corpo;
}

// --- a FICHA, com o espelho embaixo das barras e o painel à direita
const F2 = {A: "cartas inteiras", B: "a sua escolha em cima e o resto em lista", C: "duas colunas"};
const E2 = {
  A: "Tudo o que a Origem oferece, carta por carta, com o texto inteiro. As suas três escolhas ficam com a borda âmbar e sobem para o topo. É o livro dentro da ficha. <b>Preço:</b> fica muito comprido: a Descendente passa de 15 cartas.",
  B: "Só o que você escolheu: a marcante e as duas menores com o texto inteiro (do livro ou o da criada) e os Legados de história que você escreveu no dossiê. O catálogo da Origem fica fora da ficha. <b>Antes</b> (versão 1): no topo vão as suas três escolhas, com o texto inteiro, o que você usa na mesa. Embaixo, numa linha cada, o resto do catálogo (nome, frequência e a primeira frase) e as sugestões de Legado de história. Pra ler uma inteira, ela está na nota. <b>Preço:</b> quem quer comparar opções antes de trocar lê pela nota.",
  C: "A base e a marcante à esquerda, as menores em grade de duas colunas à direita, todas com o resumo. As suas escolhas em âmbar. <b>Preço:</b> o painel fica mais largo (umas 30 colunas), e o texto das menores aparece só resumido."
};
function espelho() {
  const s = ["marcante", "m1", "m2"].map(k => `<div class="cx novo" style="flex:1"><div class="rot">${ROT[k]}</div><div class="val esq" style="font-size:12px">${esc(nomeDe(k) || "—")}${criada(k) ? ' <span class="etq criada">CRIADA</span>' : ""}</div><div class="sub" style="border-color:var(--novo)">${esc(freqDe(k))}</div></div>`).join("");
  return s;
}
function carta(x, escolhida, curto) {
  return `<div class="card ${escolhida ? "esc" : ""}"><div class="cab"><span>${escolhida ? "✓ " : ""}${esc(x.nome)}${x.extra ? " · " + esc(x.extra) : ""}</span><em>${esc(x.freq)}</em></div><div class="corpo">${curto ? esc(x.resumo || "") : neg(x.texto)}</div></div>`;
}
function painel() {
  const o = O(), escolhidas = new Set([st.esc.marcante, st.esc.m1, st.esc.m2]);
  const base = `<div class="tit"><span>${esc(st.origem.toUpperCase())}</span><span>o que a Origem oferece</span></div>
    <div class="card"><div class="cab"><span>Base</span><em>uma vez</em></div><div class="corpo">Uma perícia entre ${esc(o.pericias)} · uma perícia livre · dois ofícios (ou mais uma perícia livre) · um TR · um traço · uma marcante · duas menores · rota: ${esc(o.rota)}</div></div>`;
  const leg = `<div class="card"><div class="cab"><span>Legados de história</span><em>sem efeito na ficha</em></div><div class="corpo">${neg(o.legados)}</div></div>`;
  const criadas = ["marcante", "m1", "m2"].filter(criada).map(k => `<div class="card esc"><div class="cab"><span>✓ ${esc(nomeDe(k) || "(sem nome)")} · criada</span><em>${ROT[k].toLowerCase()}</em></div><div class="corpo">${esc(st.livre[k] || "")}</div></div>`).join("");
  if (st.f2 === "A") {
    const ord = a => a.slice().sort((p, q) => escolhidas.has(q.nome) - escolhidas.has(p.nome));
    return base + `<div class="tit"><span>MARCANTE</span><span>${o.marcantes.length > 1 ? "escolha uma" : "a da Origem"}</span></div>` + ord(o.marcantes).map(x => carta(x, escolhidas.has(x.nome))).join("")
      + `<div class="tit"><span>MENORES</span><span>escolha duas · ${o.menores.length} no catálogo</span></div>` + criadas + ord(o.menores).map(x => carta(x, escolhidas.has(x.nome))).join("") + leg;
  }
  if (st.f2 === "B") {
    const minhas = ["marcante", "m1", "m2"].map(k => achado(k) ? carta(achado(k), true) : "").join("") + criadas;
    const resto = (t, a) => `<div class="tit"><span>${t}</span><span>passe o mouse no nome: o texto inteiro está na nota</span></div><div class="lista">${a.map(x => `<div class="${escolhidas.has(x.nome) ? "esc" : ""}"><b>${esc(x.nome)}</b><span>${esc(x.freq)} · ${esc(x.resumo || (x.comp || []).join(", "))}</span></div>`).join("")}</div>`;
    const meusLeg = `<div class="card esc"><div class="cab"><span>Legados de história</span><em>sem efeito na ficha · do dossiê</em></div><div class="corpo">${esc(st.legados || "—")}</div></div>`;
    return `<div class="tit"><span>${esc(st.origem.toUpperCase())}</span><span>o que você escolheu, inteiro</span></div>` + minhas + meusLeg;
  }
  return `<div class="grade2"><div>${base}<div class="tit"><span>MARCANTE</span><span></span></div>${o.marcantes.map(x => carta(x, escolhidas.has(x.nome))).join("")}${leg}</div>
    <div><div class="tit"><span>MENORES · ${o.menores.length}</span><span>escolha duas</span></div>${criadas}${o.menores.map(x => carta(x, escolhidas.has(x.nome), true)).join("")}</div></div>`;
}
function ficha() {
  const larg = st.f2 === "C" ? 760 : 520;
  const barras = ["VIDA", "ENERGIA", "INTEGRIDADE"].map((n, i) => `<div class="linha" style="gap:10px"><div class="cx" style="flex:10"><div class="rot">${n} · ATUAL / MÁXIMA</div><div class="val num">${["40 / 93", "30 / 60", "25 / 25"][i]}</div></div><div class="cx" style="flex:3"><div class="rot">Buff/Debuff</div><div class="val num">0</div></div><div class="cx" style="flex:14"><div class="rot">&nbsp;</div><div class="val"><div class="barra"><div style="width:${[43, 50, 100][i]}%"></div></div></div></div></div>`).join("");
  document.getElementById("ficha").innerHTML = `<div class="folha"><div class="tit"><span>FICHA</span><span>colunas A a AU</span></div>${barras}
    <div class="linha" style="gap:10px"><div class="cx novo" style="flex:1"><div class="rot">SEQUELAS</div><div class="val" style="gap:6px">${caixinhas(st.seq).replace(/class="mk/g, 'class="mk mk2')}</div></div><div class="cx vel" style="flex:1"><div class="rot">EXAUSTÃO</div><div class="val num">0</div></div><div class="cx vel" style="flex:2"><div class="rot">RESISTÊNCIAS</div><div class="val">—</div></div></div>
    <div class="tit" style="margin-top:6px"><span>ORIGEM · ${esc(st.origem)}</span><span>no lugar do LEGADO 1 e LEGADO 2 · abra o painel →</span></div><div class="linha" style="gap:10px">${espelho()}</div>
    <div class="expl" style="font-size:12px;margin-top:2px">A linha de cima é o espelho que já existe hoje (os dois Legados), trocado pelas três capacidades, com nome e frequência.</div></div>
    <div class="calha"><button id="tg" title="abre e fecha o grupo de colunas">${st.painel ? "−" : "+"}</button>${st.painel ? '<div class="traco"></div>' : ""}</div>
    <div class="painel ${st.painel ? "" : "fechado"}" style="width:${larg}px">${painel()}</div>`;
  document.getElementById("tg").onclick = () => { st.painel = !st.painel; tudo(); };
}

// --- o Morrendo
const F3 = {A: "três caixas de número", B: "uma faixa com a frase", C: "dentro da caixa das Sequelas"};
const E3 = {
  A: "Uma linha nova embaixo das barras, só de leitura, com três números e o que cada um quer dizer. Ela muda sozinha quando a vida máxima, a Classe ou as Sequelas mudam. Não guarda o tratamento recebido: isso se conta na mesa.",
  B: "A mesma conta numa frase só, de ponta a ponta. Lê como o livro fala. <b>Preço:</b> o número fica no meio do texto, e de relance é mais difícil achar.",
  C: "Não abre linha: a caixa das Sequelas, que já diz a janela, ganha os três números embaixo. <b>Preço:</b> a caixa fica apertada, com letra pequena."
};
function caixinhas(sq) {
  return [0, 1, 2].map(i => `<span class="mk ${i < sq ? "on" : ""}" data-sq="${i}" title="marque ao sair de uma queda">${i < sq ? "✕" : ""}</span>`).join("");
}
function janela(sq) { return sq >= 3 ? "Derrotado na hora" : (3 - sq) + (3 - sq === 1 ? " rodada" : " rodadas"); }
function linhaEstado(sq) {
  return `<div class="linha" style="gap:10px"><div class="cx novo" style="flex:12"><div class="rot">SEQUELAS · MARQUE UMA POR QUEDA</div><div class="val" style="gap:8px">${caixinhas(sq)}</div><div class="sub">Próxima queda: ${janela(sq)}. O descanso longo desmarca.</div></div>
    <div class="cx vel" style="flex:12"><div class="rot">EXAUSTÃO</div><div class="val num">0</div><div class="sub">—</div></div><div class="cx vel" style="flex:12"><div class="rot">RESISTÊNCIAS</div><div class="val">—</div></div><div class="cx vel" style="flex:12"><div class="rot">IMUNIDADES</div><div class="val">—</div></div></div>`;
}
function morrendo() {
  const vm = Math.max(0, +document.getElementById("vmax").value || 0), cl = Math.max(0, +document.getElementById("classe").value || 0), sq = st.seq;
  const teto = 15 * cl, ag = Math.ceil(vm / 4), i1 = Math.min(Math.ceil(vm / 3), teto), i2 = Math.min(Math.ceil(vm / 2), teto);
  const jan = janela(sq);
  let h;
  if (st.f3 === "A") {
    h = `<div class="tit"><span>SE A VIDA CHEGAR A 0 · MORRENDO</span><span>cura que você precisa receber para levantar</span></div><div class="linha">
      <div class="cx novo" style="flex:1"><div class="rot">AGUENTAR · INCONSCIENTE</div><div class="val num">${ag}</div><div class="sub">¼ da vida máxima</div></div>
      <div class="cx novo" style="flex:1"><div class="rot">INSISTIR · 1ª VEZ NA CENA</div><div class="val num">${i1}</div><div class="sub">⅓ da vida máxima${Math.ceil(vm / 3) > teto ? ", no teto de 15 × Classe" : ""}</div></div>
      <div class="cx novo" style="flex:1"><div class="rot">INSISTIR · 2ª VEZ EM DIANTE</div><div class="val num">${i2}</div><div class="sub">½ da vida máxima${Math.ceil(vm / 2) > teto ? ", no teto de 15 × Classe" : ""}</div></div>
      <div class="cx novo" style="flex:1.3"><div class="rot">PRAZO ATÉ SER DERROTADO</div><div class="val num" style="font-size:${sq >= 3 ? 13 : 17}px">${jan}</div><div class="sub">tempo para receber a cura: 3 rodadas, menos 1 por Sequela marcada; cada dano sofrido no chão tira mais 1</div></div></div>`;
  } else if (st.f3 === "B") {
    h = `<div class="linha"><div class="cx novo" style="flex:1"><div class="rot">SE A VIDA CHEGAR A 0 · MORRENDO</div><div class="val esq morre">Para levantar, você precisa receber <b>${ag}</b> de cura se Aguentar (fica Inconsciente), <b>${i1}</b> se Insistir pela 1ª vez na cena, ou <b>${i2}</b> da 2ª vez em diante. Tempo: <b>${jan}</b>.</div></div></div>`;
  } else {
    h = `<div class="linha"><div class="cx" style="flex:12"><div class="rot">SEQUELAS</div><div class="val num">${sq}</div><div class="sub" style="border-color:var(--novo);color:var(--tinta)">Próxima queda: ${jan}<br>levanta com <b>${ag}</b> (Aguentar) · <b>${i1}</b> / <b>${i2}</b> (Insistir 1ª / depois)</div></div>
      <div class="cx vel" style="flex:12"><div class="rot">EXAUSTÃO</div><div class="val num">0</div><div class="sub">—</div></div><div class="cx vel" style="flex:24"><div class="rot">RESISTÊNCIAS</div><div class="val">—</div></div></div>`;
  }
  document.getElementById("morre").innerHTML = `<div class="linha" style="gap:10px"><div class="cx vel" style="flex:10"><div class="rot">VIDA · ATUAL / MÁXIMA</div><div class="val num">0 / ${vm}</div></div><div class="cx vel" style="flex:17"><div class="rot">&nbsp;</div><div class="val"><div class="barra"><div style="width:0"></div></div></div></div></div>` + h + linhaEstado(sq);
  document.querySelectorAll(".mk").forEach(m => m.onclick = () => { const i = +m.dataset.sq; st.seq = (i < st.seq) ? i : i + 1; morrendo(); });
  document.getElementById("contas").innerHTML = `A conta, com os números de cima: Aguentar <code>${vm} ÷ 4 = ${(vm / 4).toFixed(2)} → ${ag}</code> (para cima). Insistir 1ª <code>${vm} ÷ 3 = ${(vm / 3).toFixed(2)} → ${Math.ceil(vm / 3)}</code>, teto <code>15 × ${cl} = ${teto}</code> → <b>${i1}</b>. Insistir 2ª <code>${vm} ÷ 2 = ${(vm / 2).toFixed(1)} → ${Math.ceil(vm / 2)}</code>, teto ${teto} → <b>${i2}</b>. É o exemplo do livro (máximo 93, Classe 3: 24, 31 e 45). A nota da linha explica o resto: ao alcançar o número, toda a cura recebida vira vida e você ganha uma Sequela; dano enquanto está a 0 tira uma rodada e não apaga a cura já recebida; Estabilizar é Medicina CD 14 com Ação Padrão.`;
}
["vmax", "classe"].forEach(i => document.getElementById(i).oninput = morrendo);

function tudo() {
  const o = O();
  const podeST = !st.origem.startsWith("Corpo") && !st.origem.startsWith("Restrição");
  if (!podeST) st.semtec = false;
  document.getElementById("semtec").checked = st.semtec; document.getElementById("semtec").disabled = !podeST;
  document.getElementById("aviso-st").textContent = podeST ? "" : "esta Origem não aceita Sem Técnica";
  botoes("b1", "f1", F1); botoes("b2", "f2", F2); botoes("b3", "f3", F3);
  document.getElementById("e1").innerHTML = E1[st.f1]; document.getElementById("e2").innerHTML = E2[st.f2]; document.getElementById("e3").innerHTML = E3[st.f3];
  dossie(); ficha(); morrendo();
  document.querySelectorAll("select[data-slot]").forEach(s => s.onchange = () => { st.esc[s.dataset.slot] = s.value; tudo(); });
  document.querySelectorAll("textarea[data-livre]").forEach(t => t.oninput = () => { st.livre[t.dataset.livre] = t.value; });
  document.querySelectorAll("input[data-nome]").forEach(t => t.onchange = () => { st.nomeLivre[t.dataset.nome] = t.value; tudo(); });
  const lg = document.getElementById("legados"); if (lg) lg.oninput = () => { st.legados = lg.value; };
}
tudo();
</script></body></html>'''

open(SAIDA, "w", encoding="utf-8").write(PAGINA.replace("__DADOS__", DADOS))
print(SAIDA, {o: n_menores[o] for o in ORDEM})
