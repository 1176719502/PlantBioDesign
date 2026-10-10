from pathlib import Path
import re, shutil, hashlib, json, html
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, NextPageTemplate, KeepTogether, Flowable
from reportlab.lib.pagesizes import A4,A3,landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import pymupdf as fitz
from PIL import Image as PILImage, ImageDraw
ROOT=Path(__file__).resolve().parent
OUT=ROOT
pdfmetrics.registerFont(TTFont('CN','C:/Windows/Fonts/simsun.ttc'))
pdfmetrics.registerFont(TTFont('Mono','C:/Windows/Fonts/consola.ttf'))
styles={
 'body':ParagraphStyle('body',fontName='CN',fontSize=10.5,leading=15.5,spaceAfter=7,rightIndent=10,wordWrap='CJK'),
 'h1':ParagraphStyle('h1',fontName='CN',fontSize=21,leading=29,spaceAfter=18,keepWithNext=True,wordWrap='CJK'),
 'h2':ParagraphStyle('h2',fontName='CN',fontSize=15,leading=21,spaceBefore=12,spaceAfter=10,keepWithNext=True,wordWrap='CJK'),
 'h3':ParagraphStyle('h3',fontName='CN',fontSize=12,leading=18,spaceBefore=9,spaceAfter=7,keepWithNext=True,wordWrap='CJK'),
 'cell':ParagraphStyle('cell',fontName='CN',fontSize=9,leading=13,rightIndent=3,wordWrap='CJK'),
 'caption':ParagraphStyle('caption',fontName='CN',fontSize=10.5,leading=15,spaceBefore=8,wordWrap='CJK'),
}
def inline(s):
 code=[]
 def protect(m):
  code.append(m[1]);return 'INLINECODETOKEN'+str(len(code)-1)+'ENDTOKEN'
 s=re.sub(r'`([^`]+)`',protect,s)
 s=html.escape(s)
 s=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',lambda m:'<link href="'+m[2]+'" color="#18517b">'+m[1]+'</link>',s)
 s=re.sub(r'`([^`]+)`',r'\1',s)
 s=re.sub(r'\*\*([^*]+)\*\*',r'<b>\1</b>',s)
 s=re.sub(r'\*([^*]+)\*',r'\1',s)
 for n,v in enumerate(code):s=s.replace('INLINECODETOKEN'+str(n)+'ENDTOKEN',html.escape(v))
 return s
class Code(Flowable):
 def __init__(self,lines,width):
  Flowable.__init__(self); self.lines=lines; self.width=width
  def lw(s): return sum(pdfmetrics.stringWidth(c,'CN' if ord(c)>255 else 'Mono',8.5) for c in s)
  self.size=8.5*min(1,(width-16)/max(1,max(map(lw,lines))))
  self.lead=10.5;self.height=len(lines)*self.lead+16
 def draw(self):
  c=self.canv;c.setFillColor(colors.HexColor('#f3f5f7'));c.rect(0,0,self.width,self.height,fill=1,stroke=0);c.setFillColor(colors.black)
  y=self.height-8-self.size
  for line in self.lines:
   x=8
   for run in re.findall(r'[\x00-\xff]+|[^\x00-\xff]+',line):
    font='Mono' if ord(run[0])<256 else 'CN';c.setFont(font,self.size);c.drawString(x,y,run);x+=pdfmetrics.stringWidth(run,font,self.size)
   y-=self.lead
def footer(c,d):
 w,h=c._pagesize;c.setStrokeColor(colors.HexColor('#c7cfd7'));c.line(36,31,w-36,31)
 c.setFont('CN',8);c.setFillColor(colors.HexColor('#465564'))
 c.drawString(36,h-26,d.title);c.drawString(36,18,'正式公开文档 | V1.0 | 2026-10-10');c.drawRightString(w-36,18,str(d.page))
def make(md,pdf):
 title=md.read_text(encoding='utf-8').splitlines()[0].lstrip('# ')
 doc=BaseDocTemplate(str(pdf),pagesize=A4,title=title,author='PlantBioDesign',leftMargin=42,rightMargin=42,topMargin=45,bottomMargin=42)
 doc.title=title
 for name,size in [('P',A4),('L',landscape(A4)),('M',landscape(A3))]:
  w,h=size; doc.addPageTemplates(PageTemplate(id=name,pagesize=size,frames=[Frame(42,42,w-84,h-87,leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)],onPage=footer))
 lines=md.read_text(encoding='utf-8').splitlines(); story=[];i=0;width=A4[0]-84;figures=[]
 while i<len(lines):
  s=lines[i];i+=1
  if not s.strip():continue
  if s.startswith('```'):
   block=[]
   while i<len(lines) and not lines[i].startswith('```'):block.append(lines[i]);i+=1
   i+=1;story.extend([Code(block,width),Spacer(1,10)]);continue
  im=re.fullmatch(r'!\[(.*?)\]\((.*?)\)',s)
  if im:
   if len(story)>=2 and isinstance(story[-1],PageBreak) and isinstance(story[-2],NextPageTemplate):story=story[:-2]
   cap,path=im.groups(); native=path.endswith('native-export.png');size=landscape(A3 if native else A4);w,h=size
   imagepath=OUT/path;pw,ph=PILImage.open(imagepath).size;scale=min((w-84)/pw,(h-135)/ph)
   story.extend([NextPageTemplate('M' if native else 'L'),PageBreak(),Image(str(imagepath),pw*scale,ph*scale),Paragraph(inline(cap),styles['caption'])])
   # Keep the immediate evidence caveat on its figure page.
   k=i
   while k<len(lines) and not lines[k].strip():k+=1
   if k<len(lines) and lines[k].startswith('> '):
    story.append(Paragraph(inline(lines[k][2:]),styles['caption']));i=k+1
   story.extend([NextPageTemplate('P'),PageBreak()])
   figures.append({'caption':cap,'path':path,'pixels':[pw,ph],'display_mm':[round(pw*scale/72*25.4,2),round(ph*scale/72*25.4,2)]});continue
  if s.startswith('|'):
   rows=[s]
   while i<len(lines) and lines[i].startswith('|'):rows.append(lines[i]);i+=1
   rows=[r for r in rows if not re.match(r'^\|[\s:|\-]+\|$',r)]
   cells=[[x.strip() for x in r.strip('|').split('|')] for r in rows]
   # Literal 27|28 is inline text outside these tables in baseline.
   n=max(map(len,cells));assert all(len(r)==n for r in cells)
   weights=[1]*n
   if n==5:weights=[.85,1.0,1.6,.5,2.1]
   elif n==3:weights=[1.1,1.8,2.1]
   data=[[Paragraph(inline(x),styles['cell']) for x in r] for r in cells]
   t=Table(data,colWidths=[width*v/sum(weights) for v in weights],repeatRows=1,hAlign='LEFT')
   t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e7edf2')),('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#b8c4ce')),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
   if t.wrap(width,10000)[1]<450:story.append(KeepTogether(t))
   else:story.append(t)
   story.append(Spacer(1,10));continue
  heading=re.match(r'^(#{1,6})\s+(.*)',s)
  if heading:
   lev=min(len(heading[1]),3)
   sty=styles['h'+str(lev)]
   if heading[2].startswith('13. 常见问题'):sty=ParagraphStyle('longtableheading',parent=sty,keepWithNext=False)
   story.append(Paragraph(inline(heading[2]),sty));continue
  para=[s.lstrip('> ')]
  while i<len(lines) and lines[i].strip() and not re.match(r'^(#|\||```|!\[|> |\d+\. |\- )',lines[i]):para.append(lines[i]);i+=1
  if s.startswith('原次同一R5保存项目的Markdown/PDF'):story.append(PageBreak())
  story.append(Paragraph(inline(' '.join(para)),styles['body']))
 # Avoid trailing blank page after a terminal image.
 if story and isinstance(story[-1],PageBreak):story=story[:-2]
 doc.build(story)
 return figures
docs=['PlantBioDesign_中文使用手册.md','CASE_INPUT_REPRODUCIBILITY.md','PlantBioDesign_软件简介.md']
for md,pdf in zip(docs,['PlantBioDesign_中文使用手册.pdf','PlantBioDesign_案例复现说明.pdf','PlantBioDesign_软件简介.pdf']):
 make(OUT/md,OUT/pdf)
