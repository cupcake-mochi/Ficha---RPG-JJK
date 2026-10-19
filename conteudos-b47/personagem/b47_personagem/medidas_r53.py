"""Dimensões de Linha: comprimento e largura conservados separadamente."""
import re

def linha(valor):
 if not isinstance(valor,str):return None
 m=re.fullmatch(r'(\d+(?:,\d+)?) × (\d+(?:,\d+)?) m',valor)
 return tuple(float(v.replace(',','.')) for v in m.groups()) if m else None

def ordem_linha(valor):
 v=linha(valor)
 return v[0]*1000+v[1] if v else None

def numero_linha(cel):
 # Sheets VALUE respeita a localidade da planilha; sem interpretar prosa livre.
 return f'IFERROR(VALUE(REGEXEXTRACT({cel},"^[0-9]+(?:,[0-9]+)?"))*1000+VALUE(REGEXEXTRACT({cel},"× ([0-9]+(?:,[0-9]+)?) m$")),-1)'
