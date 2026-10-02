# -*- coding: utf-8 -*-
"""Lê do livro o que cada propriedade de arma faz, e grava em ficha-v01/equipamento-do-livro.json.

    python3 ficha-v01/extrair_equipamento.py            # lê o livro e regrava o arquivo
    python3 ficha-v01/extrair_equipamento.py --confere  # só compara o arquivo com o livro, sem gravar

Por que este arquivo existe: a FICHA PESSOAL mostra, embaixo da arma em uso, as propriedades dela, e o Mizuki pediu
em 01/10/2026 uma nota dizendo o que cada uma faz. O catalogo-projeto-m.json traz as propriedades de cada arma, mas
não o texto delas. Pôr o texto no catálogo é decisão do Mizuki, e até lá a aba lê deste arquivo, que carrega a versão
do livro de onde saiu. O gerador (ficha_pessoal.py) nunca lê o livro: lê só este arquivo, que mora no repositório.

Nenhum texto é digitado aqui. As duas tabelas viram lista, lendo a tabela; a frase que completa uma propriedade (a
tabela diz "Ver Faixa de projétil", e a regra está na seção) tem de estar no capítulo palavra por palavra.
"""
import json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extrair_tecnica import LIVRO, ESTADO, _cap, tabela, frase

AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(AQUI, "equipamento-do-livro.json")
VER = re.compile(r"\s*Ver \*([^*]+)\*$")


def _linha(nome, texto):
    """a célula 'o que faz': o texto, e a seção para onde a tabela manda ("Ver *Munição*")"""
    m = VER.search(texto)
    faz = (texto[:m.start()] if m else texto).replace("*", "").strip()
    return {"nome": nome, "faz": faz if faz.endswith(".") else faz + ".", "ver": m.group(1) if m else None}


def extrai():
    cap = _cap("50-equipamento.md")
    versao = re.search(r"\*\*Versão (v[\d.]+)\.\*\*", open(ESTADO, encoding="utf-8").read()).group(1)
    # a regra que a tabela só aponta: cada frase está na seção citada, do jeito que está escrita aqui
    completa = {
        "Alcance no corpo a corpo": [frase(cap, "O padrão de qualquer arma de mão é 1,5 m. As Armas Longas chegam a 3 m.")],
        "Faixa de projétil": [
            frase(cap, "Faixa normal — até o Longo Alcance da arma. Ataque normal."),
            frase(cap, "Faixa longa — até o segundo número da tabela. Você rola com desvantagem: joga dois d20 e fica com o pior."),
            frase(cap, "Além da faixa longa, você não consegue atingir um alvo."),
            frase(cap, "Colado: atacar com arma de projétil estando adjacente a um inimigo (qualquer inimigo, não só o seu alvo) "
                       "também é desvantagem."),
        ],
        "Munição": [frase(cap, "Você recarrega quando tirar 1 ou 2 natural no ataque, ou depois de X ataques, o que vier primeiro.")],
    }
    # os dois números da frase do alcance: o de toda arma de mão e o de quem "chega" mais longe
    m = re.fullmatch(r"O padrão de qualquer arma de mão é ([\d,]+ m)\. As Armas Longas chegam a ([\d,]+ m)\.",
                     completa["Alcance no corpo a corpo"][0])
    props = [_linha(l[0], l[1]) for l in tabela(cap, "Propriedades")]
    falta = [p["ver"] for p in props if p["ver"] and p["ver"] not in completa]
    if falta:
        raise SystemExit(f"a tabela Propriedades manda ver uma seção que este script não lê: {falta}")
    return {
        "_meta": {"versao_do_livro": versao, "capitulo": "50-equipamento.md",
                  "o_que_e": "o texto das propriedades e das restrições de arma, que o catalogo-projeto-m.json não traz"},
        "propriedades": props,
        "restricoes": [_linha(l[0], l[1]) for l in tabela(cap, "Restrições de arma")],
        "a_regra_da_secao": completa,
        "alcance_no_corpo_a_corpo": {"padrao": m.group(1), "o_que_chega_mais_longe": m.group(2)},
        "soco": frase(cap, "O soco não tem propriedade nenhuma. O dado dele sobe com a maestria."),
        "escudo": frase(cap, "O escudo ocupa uma mão, soma com a sua proteção venha ela de onde vier, e ainda permite somar Destreza — "
                             "se você não estiver de Revestimento —, com um teto para o quanto ela pode entrar."),
    }


if __name__ == "__main__":
    if not os.path.isdir(LIVRO):
        print(f"o livro nao esta nesta maquina ({LIVRO}): nada foi lido.")
        sys.exit(0 if "--confere" in sys.argv else 1)
    novo = extrai()
    if "--confere" in sys.argv:
        velho = json.load(open(SAIDA, encoding="utf-8"))
        igual = json.dumps(velho, ensure_ascii=False, sort_keys=True) == json.dumps(novo, ensure_ascii=False, sort_keys=True)
        print("o arquivo bate com o livro " + novo["_meta"]["versao_do_livro"] if igual else "o arquivo NAO bate com o livro")
        sys.exit(0 if igual else 1)
    json.dump(novo, open(SAIDA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{SAIDA}: livro {novo['_meta']['versao_do_livro']} · {len(novo['propriedades'])} propriedades, "
          f"{len(novo['restricoes'])} restrições de arma")
