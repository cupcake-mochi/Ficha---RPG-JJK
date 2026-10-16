# -*- coding: utf-8 -*-
"""O leitor da aba ANALISE: o embrião do que o bot do Discord (Closure's Lab) vai fazer (14/10/2026, B47, fase 1).

    python3 ler-analise.py <id ou link da planilha>      # lê pelo link aberto, a aba em CSV
    python3 ler-analise.py --xlsx <ficha.xlsx>           # lê a ficha gerada, recalculada no LibreOffice
    python3 ler-analise.py --teste                       # a ficha gerada, recalculada, com as checagens de sempre

O que ele faz é o que o bot fará, na ordem do ESQUEMA-ANALISE.md: confere a versão do formato, junta as chaves por parte
e lista os avisos que a própria ficha já calcula. O que ainda não faz (fica para o bot): comparar as regras com a campanha
cadastrada, conferir o conteúdo custom aprovado e refazer as contas a partir das entradas.

Os valores saem como a planilha os mostra. Numa planilha em português o decimal é vírgula, e a caixa de marcar sai como
1 ou 0 (a aba já a converte). O `normaliza` deixa tudo num formato só.
"""
import csv, io, os, re, shutil, subprocess, sys, tempfile, urllib.request

ABA = "ANALISE"
FORMATOS_CONHECIDOS = {1, 2, 3, 4, 5, 6, 7}


def normaliza(v):
    """'1,5' -> 1.5, '3' -> 3, 'VERDADEIRO'/'TRUE' -> 1, 'FALSO'/'FALSE' -> 0, o resto como texto sem espaço nas pontas"""
    if v is None:
        return ""
    if isinstance(v, bool):
        return int(v)
    if isinstance(v, (int, float)):
        return int(v) if float(v).is_integer() else float(v)
    s = str(v).strip()
    if s.upper() in ("VERDADEIRO", "TRUE"):
        return 1
    if s.upper() in ("FALSO", "FALSE"):
        return 0
    if re.fullmatch(r"-?\d+", s):
        return int(s)
    if re.fullmatch(r"-?\d+[.,]\d+", s):
        return float(s.replace(",", "."))
    return s


def de_linhas(linhas):
    """[[chave, valor, célula, parte], ...] (com o cabeçalho) -> {chave: {valor, celula, parte}}"""
    out = {}
    for l in linhas:
        l = (list(l) + ["", "", "", ""])[:4]
        if not l[0] or l[0] == "chave":
            continue
        valor = str(l[1]).strip() if l[0] == "ficha.versao" and l[1] is not None else normaliza(l[1])
        out[str(l[0])] = {"valor": valor, "celula": l[2] or "", "parte": l[3] or ""}
    return out


def ler_link(id_ou_link):
    """a ficha aberta por link: a aba sai em CSV, sem chave e sem conta"""
    m = re.search(r"/d/([A-Za-z0-9_-]+)", id_ou_link)
    pid = m.group(1) if m else id_ou_link
    url = f"https://docs.google.com/spreadsheets/d/{pid}/gviz/tq?tqx=out:csv&sheet={ABA}"
    with urllib.request.urlopen(url, timeout=60) as r:
        texto = r.read().decode("utf-8")
    return de_linhas(csv.reader(io.StringIO(texto)))


def ler_xlsx(caminho, recalcula=True):
    """a ficha gerada: o LibreOffice recalcula as fórmulas e a aba é lida pelos valores"""
    from openpyxl import load_workbook
    if recalcula:
        pasta = tempfile.mkdtemp(prefix="analise-")
        copia = os.path.join(pasta, "ficha.xlsx")
        shutil.copy(caminho, copia)
        wb = load_workbook(copia)
        for ws in wb:                       # o IFS só é reconhecido pelo LibreOffice com o prefixo do Excel
            for c in tuple(ws._cells.values()):
                if isinstance(c.value, str) and c.value.startswith("=") and "IFS(" in c.value and "_xlfn.IFS(" not in c.value:
                    c.value = re.sub(r"(?<![A-Z_.])IFS\(", "_xlfn.IFS(", c.value)
        wb.save(copia)
        saida = os.path.join(pasta, "saida")
        subprocess.run(["libreoffice", "--headless", "--convert-to", "xlsx", "--outdir", saida, copia],
                       capture_output=True, timeout=900)
        feito = os.path.join(saida, "ficha.xlsx")
        if not os.path.exists(feito):
            sys.exit("o LibreOffice não converteu a ficha")
        wb = load_workbook(feito, data_only=True)
        shutil.rmtree(pasta, ignore_errors=True)
    else:
        wb = load_workbook(caminho, data_only=True)
    ws = wb[ABA]
    return de_linhas([[c.value for c in l] for l in ws.iter_rows(max_col=4)])


def relatorio(ficha):
    """o que o bot responderia hoje: a versão, quantas chaves de cada parte, e os avisos acesos"""
    fmt = ficha.get("formato.versao", {}).get("valor")
    if fmt not in FORMATOS_CONHECIDOS:
        return ["reprovada", [f"formato da aba ANALISE desconhecido: {fmt!r}"]]
    avisos = []
    for k, v in ficha.items():
        if v["parte"] != "aviso" or v["valor"] in ("", 0):
            continue
        t = str(v["valor"])
        if k.startswith(("aviso.efeito.", "aviso.efeito_caixa.")):
            avisos.append(f"{k} ({v['celula']}): {t}")
            continue
        # os X de Y que estão certos dizem "Tudo escolhido" ou não têm o sinal de erro: só o ⚠ e o "acima" acendem
        if k.startswith("aviso.") and "⚠" not in t and "acima" not in t.lower() and "falta" not in t.lower() \
                and "sem treino" not in t.lower() and "não cumprido" not in t.lower() and "pede " not in t.lower():
            continue
        avisos.append(f"{k} ({v['celula']}): {t}")
    return ["aprovada" if not avisos else "reprovada", avisos]


def resumo(ficha):
    partes = {}
    for v in ficha.values():
        partes[v["parte"]] = partes.get(v["parte"], 0) + 1
    return partes


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    if args[0] == "--teste":
        ficha = ler_xlsx(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ficha-v01", "ficha-projeto-m-0.1.xlsx"))
    elif args[0] == "--xlsx":
        ficha = ler_xlsx(args[1])
    else:
        ficha = ler_link(args[0])
    print(f"{len(ficha)} chaves · {resumo(ficha)}")
    for k in ("formato.versao", "ficha.versao", "ficha.livro", "nome", "caminho", "origem", "nivel", "vida_max", "defesa"):
        if k in ficha:
            print(f"  {k} = {ficha[k]['valor']!r}")
    veredito, avisos = relatorio(ficha)
    print(f"\n{veredito.upper()}" + (f": {len(avisos)} aviso(s)" if avisos else ""))
    for a in avisos[:30]:
        print("  - " + a)
    if args[0] == "--teste":
        falhas = []
        if len(ficha) < 2000:
            falhas.append(f"a aba devia ter mais de 2.000 chaves, e tem {len(ficha)}")
        if ficha.get("formato.versao", {}).get("valor") not in FORMATOS_CONHECIDOS:
            falhas.append("formato.versao desconhecido")
        if not str(ficha.get("ficha.livro", {}).get("valor", "")).startswith("Ciclo Maldito R"):
            falhas.append("ficha.livro não diz o livro")
        for k in ("sequela.1", "pericia.atletismo.treino", "tr.fisico.treino"):
            if ficha.get(k, {}).get("valor") not in (0, 1):
                falhas.append(f"{k} devia sair como 0 ou 1, e saiu {ficha.get(k, {}).get('valor')!r}")
        print("\nTESTE: " + ("OK" if not falhas else "FALHOU: " + "; ".join(falhas)))
        sys.exit(1 if falhas else 0)
