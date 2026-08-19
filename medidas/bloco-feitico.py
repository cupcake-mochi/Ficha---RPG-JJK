# -*- coding: utf-8 -*-
"""O bloco de feitiço: o que o jogador digita e o que a ficha deduz.
Prova que a maioria dos campos sai das escolhas, sem digitação."""
import json
CAT = json.load(open('catalogo-projeto-m.json', encoding='utf-8'))
BASE_ALCANCE = {  # manual p.111, base por Classe
 "Projétil": {"0":"9 m","1-5":"18 m","6-7":"36 m"}, "Toque": {"0":"1,5 m","1-5":"1,5 m","6-7":"1,5 m"},
 "Explosão": {"0":"raio 3 m a 9 m","1-5":"raio 3 m a 18 m","6-7":"raio 4,5 m a 36 m"},
 "Cone": {"0":"3 m","1-5":"4,5 m","6-7":"9 m"}, "Linha": {"0":"9 × 1,5 m","1-5":"18 × 1,5 m","6-7":"30 × 1,5 m"},
}
ESCADA = ["1,5 m","9 m","18 m","36 m","90 m","o que você enxergar"]

def deduz(f):
    c, forma, mel, res = f["classe"], f["forma"], f["melhorias"], f["restricoes"]
    faixa = "0" if c == 0 else ("1-5" if c <= 5 else "6-7")
    # ACAO
    acao = "Ação Padrão"
    if "Rápido" in mel: acao = "Ação Bônus"
    if "Reação" in mel: acao = "Reação"
    if "Lento" in res:  acao = "Ação Completa (rodada inteira)"
    if "Carregar" in res: acao += " + 1 turno carregando"
    # ALCANCE
    alc = BASE_ALCANCE.get(forma, {}).get(faixa, "—")
    degraus = mel.count("Longe") + 3*("Muito Longe" in mel)
    if degraus and alc in ESCADA:
        alc = ESCADA[min(len(ESCADA)-1, ESCADA.index(alc)+degraus)] + f"  (subiu {degraus})"
    # ALVO
    alvo = "um alvo" if forma in ("Projétil","Toque") else "área"
    extra = mel.count("Mais Um")
    if extra: alvo += f" + {extra}, dados divididos"
    if "Rajada" in mel: alvo = f"{c+1} tiros, dados divididos"
    if "Salto" in mel: alvo += " + pula com metade dos dados"
    # RESOLVE
    resolve = "rolagem de acerto" if forma in ("Projétil","Toque") else "Teste de Resistência, metade no sucesso"
    if "Certeiro" in mel: resolve = "sem acerto; TR para metade"
    if "Inescapável" in mel: resolve = "automático, sem acerto e sem TR"
    return {"Ação": acao, "Alcance": alc, "Alvo": alvo, "Como resolve": resolve,
            "Custo em PE": f"{3*c} (+{c} se estágio 2 de alma)", "Classe": c}

EXEMPLOS = [
 ("Marca do Carrasco", {"classe":3,"forma":"Projétil","melhorias":["Marca","Queima"],"restricoes":["Uma Vez"]}),
 ("Domo de Gelo",      {"classe":3,"forma":"Explosão","melhorias":["Terreno","Maior"],"restricoes":["Condicional"]}),
 ("um Classe 1 rápido",{"classe":1,"forma":"Projétil","melhorias":["Rápido"],"restricoes":["Lento"]}),
]
for nome, f in EXEMPLOS:
    print(f"\n{nome}   ·   escolhas: Forma {f['forma']}, Classe {f['classe']}, "
          f"{'+'.join(f['melhorias'])}, {'+'.join(f['restricoes'])}")
    for k, v in deduz(f).items(): print(f"     {k:14} {v}")
