// GERADO por r53/reserva_bolsa_restaurar.js; somente DADOS!CZ41.
var R53_CARGA_ORIGEM_FORMULA_="=LET(cargaOrigem,IF(DADOS_CONFIG!$E$13<>\"\",NA(),IF(DADOS_CONFIG!$C$13=1,DADOS_CONFIG!$D$13,IF(DADOS_CONFIG!$B$13=0,5+DADOS!$CZ$5+N('FICHA PESSOAL'!$L$86),IF((5+DADOS!$CZ$5+N('FICHA PESSOAL'!$L$86))=\"\",\"\",(5+DADOS!$CZ$5+N('FICHA PESSOAL'!$L$86))+DADOS_CONFIG!$B$13)))),IF(OR(cargaOrigem=\"\",DADOS_CONFIG!$C$13=1),cargaOrigem,cargaOrigem+DADOS_CUSTOM!$B$133))";
function r53CargaFormulaNoIdioma_(f, idioma) {
  if (/^en/i.test(String(idioma || ''))) return f;
  var out = '', i = 0, n = f.length, chaves = 0;
  while (i < n) {
    var ch = f.charAt(i);
    if (ch === '"' || ch === "'") {
      var j = i + 1;
      while (j < n) {
        if (f.charAt(j) === ch) {
          if (f.charAt(j + 1) === ch) { j += 2; continue; }
          break;
        }
        j++;
      }
      out += f.slice(i, j + 1);
      i = j + 1;
      continue;
    }
    if (ch === '{') chaves++;
    if (ch === '}') chaves--;
    if (ch === ',') { out += chaves > 0 ? '\\' : ';'; i++; continue; }
    if (/[0-9]/.test(ch) && !/[A-Za-z0-9_$.]/.test(f.charAt(i - 1))) {
      var m = /^[0-9]+(?:\.[0-9]+)?/.exec(f.slice(i))[0];
      out += m.replace('.', ',');
      i += m.length;
      continue;
    }
    out += ch;
    i++;
  }
  return out;
}
function r53RestaurarCargaOrigem_(e){
 if(!e||!e.range)return false;var r=e.range;
 if(r.getRow()>41||r.getLastRow()<41||r.getColumn()>104||r.getLastColumn()<104||r.getSheet().getName()!=='DADOS')return false;
 var sheet=r.getSheet(),cel=sheet.getRange(41,104),formula=r53CargaFormulaNoIdioma_(R53_CARGA_ORIGEM_FORMULA_,sheet.getParent().getSpreadsheetLocale());
 if(cel.getFormula()!==formula)cel.setFormula(formula);
 return true;
}
