#!/usr/bin/env python3
"""Prévias locais da grade emitida. Não são capturas nem cálculos do Google."""
import argparse,importlib.util,json,re,sys
from lxml import html as dom
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path[:0]=[str(ROOT),str(ROOT/'ficha'),str(ROOT/'ficha-v01')]
import emitir_gs
spec=importlib.util.spec_from_file_location('ver_aba',ROOT/'medidas/ver-aba.py');view=importlib.util.module_from_spec(spec);spec.loader.exec_module(view)
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--saida',type=Path,default=ROOT/'nuvem-b47/saidas/previas');ap.add_argument('--png',action='store_true',help='Rasteriza metadados localmente, sem navegador');a=ap.parse_args();a.saida.mkdir(parents=True,exist_ok=True)
tab=next(a for a in emitir_gs.abas_do_script() if a['nome']=='CONFIGURAÇÃO')
values={(r,c):v for r,c,v,*_ in tab['vals'] if r>=797 and not(isinstance(v,str) and v.startswith('='))}
# Blank factory view: formulas are deliberately not evaluated by this preview.
view.FONTES=''
fontcss="@font-face{font-family:Oswald;src:url('"+(ROOT/'arte/fontes/Oswald.ttf').as_uri()+"')}"
frames=[('pericias-primeiras',797),('pericias-ultimas-oficios-primeiros',853),('oficios-ultimos-familias-primeiras',923),('familias-ultimas-melhorias-primeiras',995),('melhorias-ultimas',1375),('restricoes-ultimas',1688)]
body=view.grade(tab,values,{},0,None,arte={})
def raster(tree,path):
    rootstyle=tree.get('style')
    widths=[int(float(v)) for v in re.search(r'grid-template-columns:([^;]+)',rootstyle)[1].replace('px','').split()]
    heights=[int(float(v)) for v in re.search(r'grid-template-rows:([^;]+)',rootstyle)[1].replace('px','').split()]
    xs=[0];ys=[0]
    for v in widths:xs.append(xs[-1]+v)
    for v in heights:ys.append(ys[-1]+v)
    image=Image.new('RGB',(xs[-1],ys[-1]),'#0A0810');draw=ImageDraw.Draw(image)
    fonts={}
    for cell in tree:
        css=dict(part.split(':',1) for part in cell.get('style','').split(';') if ':' in part)
        if 'grid-area' not in css:continue
        r,c,rr,cc=map(int,css['grid-area'].split('/'));x,y=xs[c-1],ys[r-1];w,h=xs[cc-1]-x,ys[rr-1]-y
        draw.rectangle((x,y,x+w-1,y+h-1),fill=css.get('background','#0A0810'))
        for side in ['top','bottom','left','right']:
            match=re.match(r'(\d+)px solid (#[A-Fa-f0-9]+)',css.get('border-'+side,''))
            if not match:continue
            pts={'top':(x,y,x+w-1,y),'bottom':(x,y+h-1,x+w-1,y+h-1),'left':(x,y,x,y+h-1),'right':(x+w-1,y,x+w-1,y+h-1)}
            draw.line(pts[side],fill=match[2],width=int(match[1]))
        size=round(float(css.get('font-size','10pt').replace('pt',''))*4/3)
        family='Oswald' if 'Oswald' in css.get('font-family','') else 'Roboto'
        if (family,size) not in fonts:
            file=ROOT/'arte/fontes/Oswald.ttf' if family=='Oswald' else Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
            fonts[family,size]=ImageFont.truetype(str(file),size)
        font=fonts[family,size];color=css.get('color','#F4F1F7');text=(cell.text or '')
        lines=[];current=''
        for word in text.split():
            candidate=(current+' '+word).strip()
            if current and css.get('white-space')=='normal' and font.getlength(candidate)>w-6:lines.append(current);current=word
            else:current=candidate
        if current:lines.append(current)
        layer=Image.new('RGBA',(max(1,w-6),max(1,h)),(0,0,0,0));ld=ImageDraw.Draw(layer)
        y0=0 if css.get('align-items')=='flex-start' else max(0,(h-len(lines)*size*1.15)/2)
        for i,line in enumerate(lines):
            tw=font.getlength(line);x0=max(0,(w-6-tw)/2) if css.get('justify-content')=='center' else 0
            ld.text((x0,y0+i*size*1.15),line,font=font,fill=color,anchor='lt')
        image.paste(layer,(x+3,y),layer)
        classes=[el.get('class','') for el in cell.iterdescendants()]
        if any('cx' in cls.split() for cls in classes):draw.rectangle((x+4,y+(h-11)//2,x+15,y+(h+11)//2),outline=color,width=1)
        if 'menu' in classes:draw.polygon([(x+w-10,y+h//2-2),(x+w-4,y+h//2-2),(x+w-7,y+h//2+2)],fill=color)
        if 'nota' in classes:draw.polygon([(x+w-7,y),(x+w,y),(x+w,y+7)],fill=color)
    image.save(path)

for name,row in frames:
    # Crop the grid before rendering. A full 1731-row CSS grid is needlessly
    # expensive for a focal 44-row image, even when most of it is off screen.
    tree=dom.fromstring(body);last=min(row+43,tab['rows'])
    for element in list(tree):
        style=element.get('style','');match=re.search(r'grid-area:(\d+)/(\d+)/(\d+)/(\d+)',style)
        if not match:continue
        r,c,rr,cc=map(int,match.groups())
        if rr<=row or r>last:tree.remove(element);continue
        area=f'grid-area:{max(r,row)-row+1}/{c}/{min(rr,last+1)-row+1}/{cc}'
        element.set('style',style[:match.start()]+area+style[match.end():])
    heights=' '.join(str(int(tab['alturas'].get(str(r),21)))+'px' for r in range(row,last+1))
    tree.set('style',re.sub(r'grid-template-rows:[^;]+','grid-template-rows:'+heights,tree.get('style')))
    html=view.pagina(dom.tostring(tree,encoding='unicode'),'Prévia LOCAL B47 · '+name)
    html=html.replace('</head>',f'<style>{fontcss}body{{margin:0;padding:0;overflow:hidden}}</style></head>')
    (a.saida/(name+'.html')).write_text(html)
    if a.png:raster(tree,a.saida/(name+'.png'))
print(json.dumps({'tipo':'prévia local de fábrica; sem fórmulas calculadas; PNG rasteriza metadados, não é captura do navegador','quadros':[n for n,_ in frames]},ensure_ascii=False))
