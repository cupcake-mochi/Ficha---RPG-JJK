"""Teste estrutural e cenários de recálculo nativo do deslocamento corporal.

Sem escrita remota. --pedidos prepara uma aba de ensaio para uma cópia de QA.
Os resultados esperados são explícitos. A fórmula vem do GS gerado, sem
reimplementar a conta de movimento em Python.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from openpyxl.formula import Tokenizer

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ficha-v01"))
import configuracao as cfg


def fontes():
    js = """const vm=require('vm'),{fontes}=require('./medidas/carregar-ficha.js');
const c={};vm.createContext(c);vm.runInContext(fontes(),c);
function val(aba,l,col){return c.ABAS.find(a=>a.nome===aba).vals.find(r=>r[0]===l&&r[1]===col)[2];}
console.log(JSON.stringify({movimento:val('FICHA',67,15),corporal:val('DADOS_CUSTOM',126,2)}));"""
    return json.loads(subprocess.check_output(["node", "-e", js], cwd=ROOT))


# B:N são entradas controladas. Referências são trocadas por token, nunca por
# substituição global de coordenadas. Qualquer dependência nova exige revisão.
REFS = {"'DADOS_CUSTOM'!$B$126": "B", "'FICHA'!$D$52": "C",
        "'FICHA'!$D$26": "D", "'FICHA'!$J$26": "E", "$W$67": "F",
        "DADOS_CONFIG!$S$9": "G", "DADOS!$CZ$45": "H", "DADOS!$CZ$46": "I",
        "$O$48": "J", "DADOS_CONFIG!$B$12": "K", "DADOS_CONFIG!$C$12": "L",
        "DADOS_CONFIG!$D$12": "M", "DADOS_CONFIG!$E$12": "N",
        "$D$34": "O", "$J$34": "P", "DADOS_AM!$A$2": "Q", "DADOS_AM!$HM$6": "R",
        "DADOS_AM!$HM$25": "S", "DADOS_AM!$HM$26": "T", "DADOS_AM!$HZ$2:$HZ$13": "U"}


def localiza(formula, linha):
    itens = Tokenizer(formula).items
    return "=" + "".join(REFS[t.value] + str(linha)
                         if t.type == "OPERAND" and t.subtype == "RANGE" and t.value not in {"distancia", "tetoExaustao"}
                         else t.value for t in itens)


def pt_br(formula):
    return "=" + "".join(";" if t.type == "SEP" and t.subtype == "ARG" else
                         t.value.replace(".", ",") if t.type == "OPERAND" and t.subtype == "NUMBER" else t.value
                         for t in Tokenizer(formula).items)


def casos():
    out = []
    # corporal, marcante, vida, máximo, buff, base, meia marcha, parado,
    # Exaustão, somar, quantidade de trocas, trocar por, erro de configuração
    padrao = dict(corporal=True, corpo="Corpo Exaurido", vida=12, maximo=23,
                  buff=0, base=9, meia=0, parado=0, exaustao=0, soma=0, trocas=0, troca=0, erro="",
                  integridade=26, integridade_max=26, rota=1, lapidacao=1,
                  anotadas=0, compraveis=0, bencao="")
    def caso(nome, esperado, **entradas):
        out.append([nome, *dict(padrao, **entradas).values(), esperado])
    for corpo in ("Corpo Debilitado", "Corpo Quebradiço"):
        caso(corpo + " saudável", 0, corpo=corpo, vida=23)
        caso(corpo + " com bônus", 0, corpo=corpo, buff=6, soma=3)
        caso(corpo + " com troca", 0, corpo=corpo, trocas=1, troca=28)
        caso(corpo + " residual sem base", 9, corpo=corpo, corporal=False)
    caso("Exaurido acima da metade ímpar", 4.5)
    caso("Exaurido na metade ímpar arredondada", 0, vida=11)
    caso("Exaurido abaixo da metade", 0, vida=10)
    caso("Exaurido acima da metade par", 4.5, maximo=24, vida=13)
    caso("Exaurido na metade par", 0, maximo=24, vida=12)
    caso("Máximo um e vivo", 4.5, maximo=1, vida=1)
    caso("Máximo um e zero vida", 0, maximo=1, vida=0)
    caso("Máximo zero", 0, maximo=0, vida=0)
    caso("Movimento menor preservado", 2, base=2)
    caso("Movimento zero preservado", 0, base=0)
    caso("Meia marcha", 4.5, meia=1)
    caso("Meia marcha menor", 1.5, meia=1, base=3)
    caso("Imóvel pela carga", 0, parado=1)
    caso("Exaustão dois", 4.5, exaustao=2)
    caso("Bônus pessoal", 4.5, buff=10)
    caso("Somar configurado", 4.5, soma=10)
    caso("Trocar por maior", 4.5, trocas=1, troca=28)
    caso("Trocar por menor", 2, trocas=1, troca=2)
    caso("Trocar por zero", 0, trocas=1, troca=0)
    caso("Erro de configuração sem encobrir", "#N/A", erro="Conflito")
    caso("Outra Origem com nome residual", 9, corporal=False)
    caso("Cartão custom inválido, B126 falso", 9, corporal=False, vida=3)
    caso("Corpo próprio conserva deslocamento", 9, corpo="Corpo Próprio", vida=3)
    caso("Criada com mestre conserva deslocamento", 9, corpo="Criada com o mestre", vida=3)
    caso("Outra Origem com bônus e configuração", 14, corporal=False, buff=3, soma=2)
    caso("Outra Origem com meia marcha", 4.5, corporal=False, meia=1)
    caso("Outra Origem com carga", 0, corporal=False, parado=1)
    caso("Outra Origem com troca", 28, corporal=False, trocas=1, troca=28)
    caso("Outra Origem com erro", "#N/A", corporal=False, erro="Entrada inválida")
    caso("Integridade 2 e Exaustão 2 em 9 m", 4.5, corporal=False, integridade=13, exaustao=2)
    caso("Integridade 2 e Exaustão 2 em 6 m", 3, corporal=False, integridade=13, exaustao=2, base=6)
    caso("Integridade 2 arredonda na escala", 3, corporal=False, integridade=13, base=7.5)
    caso("Derrota por Integridade", 0, corporal=False, integridade=0)
    caso("Sem barra", 9, corporal=False, integridade=0, integridade_max=0)
    caso("Vigília habilitada", 9, corporal=False, exaustao=2,
         rota=4, lapidacao=4, anotadas=1, compraveis=1, bencao="Vigília")
    caso("Vigília sem vaga", 4.5, corporal=False, exaustao=2,
         rota=4, lapidacao=4, anotadas=1, compraveis=0, bencao="Vigília")
    return out


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--pedidos", type=Path)
    ap.add_argument("--sheet-id", type=int, default=53018006)
    args=ap.parse_args()
    f=fontes()
    m=cfg.DESLOCAMENTO_CORPORAL.fullmatch(f["movimento"])
    assert m, "O GS gerado não contém a guarda corporal"
    assert cfg.anterior(f["movimento"]) == cfg.anterior("=" + m["base"])
    for adulterada in (f["movimento"].replace("MIN(4.5,", "MIN(9,", 1),
                       f["movimento"].replace('"0 m"', '"1 m"', 1)):
        assert not cfg.DESLOCAMENTO_CORPORAL.fullmatch(adulterada)
    linhas=casos()
    if args.pedidos:
        cab=["Caso", "Base corporal", "Corpo", "Vida", "Vida máxima", "Buff", "Base m", "Meia marcha", "Carga impede", "Exaustão", "Somar", "Trocas", "Trocar por", "Erro", "Integridade", "Integridade máxima", "Rota", "Lapidação", "Anotadas", "Compráveis", "Bênção",
             "Esperado m", "Resultado", "OK"]
        def v(x):
            return {"userEnteredValue": {"boolValue" if isinstance(x,bool) else "numberValue" if isinstance(x,(int,float)) else "stringValue":x}}
        rows=[{"values":[v(x) for x in cab]}]
        for n,caso in enumerate(linhas,2):
            formula=localiza(f["movimento"],n)
            prova=f'=ISNA(W{n})' if caso[-1]=="#N/A" else f'=VALUE(SUBSTITUTE(W{n}," m",""))=V{n}'
            rows.append({"values":[*[v(x) for x in caso],{"userEnteredValue":{"formulaValue":pt_br(formula)}}, {"userEnteredValue":{"formulaValue":pt_br(prova)}}]})
        req=[{"addSheet":{"properties":{"sheetId":args.sheet_id,"title":"QA deslocamento corporal", "gridProperties":{"rowCount":len(rows)+5,"columnCount":24,"frozenRowCount":1}}}},
             {"updateCells":{"start":{"sheetId":args.sheet_id,"rowIndex":0,"columnIndex":0},"rows":rows,"fields":"userEnteredValue"}},
             {"repeatCell":{"range":{"sheetId":args.sheet_id,"startRowIndex":0,"endRowIndex":1},"cell":{"userEnteredFormat":{"textFormat":{"bold":True},"backgroundColor":{"red":0.85,"green":0.9,"blue":0.95}}},"fields":"userEnteredFormat"}},
             {"autoResizeDimensions":{"dimensions":{"sheetId":args.sheet_id,"dimension":"COLUMNS","startIndex":0,"endIndex":24}}}]
        args.pedidos.write_text(json.dumps(req,ensure_ascii=False))
        args.pedidos.with_suffix(".formulas.json").write_text(json.dumps({k:pt_br(v) for k,v in f.items()}, ensure_ascii=False))
    print(json.dumps({"estrutura":"OK", "cenarios_para_recalculo_nativo":len(linhas)}))


if __name__=="__main__": main()
