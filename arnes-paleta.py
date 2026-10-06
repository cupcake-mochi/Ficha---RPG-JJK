# -*- coding: utf-8 -*-
"""Arnes de perturbacao das checagens de cor do regressao-paleta.js (a revisao de 01/10/2026): a barra cheia, a tinta de
enfeite e a cor da arte; e, desde o B31, a cor de aviso que a troca lia acesa e gravava na celula.

As tres regras do projeto: numa copia isolada, nunca nos arquivos reais; a base tem de passar NA COPIA antes de
perturbar; e cada perturbacao tem de mudar o arquivo de verdade antes de eu ler o resultado. Cada perturbacao e um
defeito que o Codigo.gs poderia ter, e a agulha e a frase da checagem que tem de acender.

Nao entra no rodar-tudo.sh: sao treze rodadas do regressao-paleta.js, uns dois minutos. Roda a mao, depois de mexer na
troca de paleta:    python3 arnes-paleta.py
"""
import os, shutil, subprocess, sys, tempfile
AQUI = os.path.dirname(os.path.abspath(__file__))
if shutil.which("node") is None:
    print("node nao existe nesta maquina: o arnes da paleta nao roda aqui."); sys.exit(0)
def copia():
    d = tempfile.mkdtemp(prefix="arnes-cores-")
    os.makedirs(os.path.join(d, "apps-script"))
    for f in ("regressao-paleta.js", "apps-script/Codigo.gs", "apps-script/Ficha.gs", "apps-script/Invocacoes.gs"):
        shutil.copy(os.path.join(AQUI, f), os.path.join(d, f))
    return d
def roda(d):
    r = subprocess.run(["node", "regressao-paleta.js"], cwd=d, capture_output=True, text=True)
    return r.returncode, [l for l in (r.stdout + r.stderr).splitlines() if "FALHA" in l]
d = copia(); cod, f = roda(d); shutil.rmtree(d)
print("base na cópia:", "passa" if cod == 0 else "JÁ FALHA", f[:2]); assert cod == 0
casos = [
 ("a barra não é gravada", "if (String(cel.getValue()) !== cor) cel.setValue(cor);", "", "a barra cheia é gravada"),
 ("a barra leva a régua do tema, e não a barra", "var cor = '#' + String(agora.barra).toUpperCase();", "var cor = '#' + String(agora.regua).toUpperCase();", "a barra cheia é gravada"),
 ("a letra de enfeite volta a ser achada pela cor", "} else if (enfeites[ra + ',' + c]) {", "} else if (false) {", "a lombada que uma troca antiga deixou"),
 ("a lombada leva o bloco em vez da linha", "papel['#' + PALETA_DE_FABRICA_.linha] = 'linha';", "papel['#' + PALETA_DE_FABRICA_.linha] = 'bloco';", "letras de enfeite"),
 ("a arte que não aparece fica como está", "if (contrasteHex_(cor, fundo) >= PISO_ARTE_) return cor;", "return cor;", "nas 122 paletas cada imagem sai na cor do papel dela"),
 ("a arte que não aparece cai no texto do tema", "return mesmaCorQueLe_(cor, fundo, PISO_ARTE_);\n}", "return '#' + String(agora.texto).toUpperCase();\n}", "quando nem o papel nem o acento aparecem"),
 ("o vermelho de aviso lido na troca vira o fundo da célula", "if (f === VERMELHO_DE_ESTADO_HEX_ && fabrica.bg[ra][c] !== VERMELHO_DE_ESTADO_HEX_) {", "if (false) {", "o vermelho de estado aceso na troca não vira o fundo"),
 ("o âmbar de aviso lido na troca vira a fonte da célula", "} else if (t === AMBAR_HEX_ && !avisos[ra + ',' + c]) {", "} else if (false) {", "o âmbar de estado aceso na troca não vira a fonte"),
 # 02/10/2026: a FICHA com o menu rápido é pintada em trechos de linhas; o resto dela não pode ficar para trás
 ("a troca pinta só o primeiro trecho da aba grande", "var trechos = trechosDaAba_(spec) || [null];",
  "var trechos = (trechosDaAba_(spec) || [null]).slice(0, 1);", "nenhum fundo nem fonte das abas visíveis ficou na cor de fábrica"),
 # 03/10/2026: o canto chanfrado da moldura da foto emenda na borda, e segue a régua exata, sem o piso da arte
 ("o canto da moldura da foto passa pelo piso de contraste da arte", "var cor = ARTE_DA_BORDA_[nome] ? '#' + String(agora.regua).toUpperCase()",
  "var cor = false ? '#' + String(agora.regua).toUpperCase()", "cantos da moldura da foto saem na régua exata"),
 ("a arte cai no texto antes de tentar o acento", "if (agora.acento && contrasteHex_(acento, fundo) >= PISO_ARTE_) return acento;", "if (agora.acento) return '#' + String(agora.texto).toUpperCase();", "nas 122 paletas cada imagem sai na cor do papel dela"),
]
ruins = 0
for nome, a, b, agulha in casos:
    d = copia(); alvo = os.path.join(d, "apps-script/Codigo.gs"); s = open(alvo, encoding="utf-8").read()
    if s.count(a) != 1:
        print(f"  [INUTIL ] {nome}: o trecho aparece {s.count(a)} vez(es)"); ruins += 1; shutil.rmtree(d); continue
    open(alvo, "w", encoding="utf-8").write(s.replace(a, b)); cod, f = roda(d); shutil.rmtree(d)
    bom = cod != 0 and any(agulha in l for l in f)
    print(f"  [{'ACENDEU' if bom else 'NAO ACENDEU' if cod == 0 else 'acendeu outra'}] {nome} -> {len(f)} falha(s) {'' if bom else f[:2]}")
    ruins += not bom
# o contra-teste: mudanca que nao muda a regra fica verde
d = copia(); alvo = os.path.join(d, "apps-script/Codigo.gs"); s = open(alvo, encoding="utf-8").read()
assert s.count("var enfeites = celulasDeEnfeite_(spec);") == 1
open(alvo, "w", encoding="utf-8").write(s.replace("var enfeites = celulasDeEnfeite_(spec);", "var enfeites = celulasDeEnfeite_(spec);   // a tinta de enfeite"))
cod, f = roda(d); shutil.rmtree(d)
print(f"  [{'FICOU VERDE' if cod == 0 else 'ACENDEU A ESMO'}] contra-teste: um comentario a mais no Codigo.gs")
ruins += cod != 0
print(f">>> TUDO OK — {len(casos)} perturbacoes acendem a checagem certa, e o contra-teste fica verde." if not ruins else f">>> {ruins} PERTURBACAO(OES) NAO FIZERAM O QUE DEVIAM")
sys.exit(1 if ruins else 0)
