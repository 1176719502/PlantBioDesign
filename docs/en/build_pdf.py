from pathlib import Path
import re, shutil, hashlib, json, html
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, PageBreak, NextPageTemplate, Image, Table, TableStyle, KeepTogether, Preformatted
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4,A3,landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import pymupdf
from PIL import Image as PILImage, ImageDraw

class Paragraph(Paragraph):
    def __init__(self, text, style, *args, **kwargs):
        super().__init__(text, style.clone(style.name), *args, **kwargs)
    def split(self, availWidth, availHeight):
        return []

flow_audit=[]
class AuditDocument(BaseDocTemplate):
    def afterFlowable(self, flowable):
        if isinstance(flowable, Preformatted):
            flow_audit.append({'document':self.title,'type':'code','page':self.page,'lines':len(flowable.lines),'sha256':hashlib.sha256('\n'.join(flowable.lines).encode()).hexdigest()})
        elif isinstance(flowable,Table):
            flow_audit.append({'document':self.title,'type':'table_segment','page':self.page,'rows':len(flowable._cellvalues)})

out=Path(__file__).resolve().parent
docs=[('PlantBioDesign_User_Manual.md','PlantBioDesign_User_Manual','PlantBioDesign_User_Manual.md','MANUAL'),('CASE_INPUT_REPRODUCIBILITY.md','CASE_INPUT_REPRODUCIBILITY','CASE_INPUT_REPRODUCIBILITY.md','CASE'),('PlantBioDesign_Software_Overview.md','PlantBioDesign_Software_Overview','PlantBioDesign_Software_Overview.md','OVERVIEW')]
pdfmetrics.registerFont(TTFont('Body','C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('Bold','C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFont(TTFont('Code','C:/Windows/Fonts/msyh.ttc'))
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='B',fontName='Body',fontSize=9.5,leading=13,spaceAfter=7))
styles.add(ParagraphStyle(name='H1x',fontName='Bold',fontSize=23,leading=28,spaceAfter=16,keepWithNext=True,textColor=colors.HexColor('#163e49')))
styles.add(ParagraphStyle(name='H2x',fontName='Bold',fontSize=15,leading=19,spaceBefore=14,spaceAfter=9,keepWithNext=True,textColor=colors.HexColor('#163e49')))
styles.add(ParagraphStyle(name='H3x',fontName='Bold',fontSize=11.5,leading=16,spaceBefore=10,spaceAfter=7,keepWithNext=True))
styles.add(ParagraphStyle(name='Cell',fontName='Body',fontSize=8,leading=11,spaceAfter=0))
styles.add(ParagraphStyle(name='Cap',fontName='Bold',fontSize=11,leading=14,spaceAfter=8))
styles.add(ParagraphStyle(name='Note',fontName='Body',fontSize=9,leading=12,spaceAfter=6,textColor=colors.HexColor('#3c5056')))

def format_text(s, table=False):
    # Keep destinations isolated from visible text wrapping. Never mutate href.
    reserved=[]
    def display(t):
        t=html.escape(t)
        if table:
            t=re.sub(r'\b[0-9a-f]{40,64}\b',lambda m:'<br/>'.join(m[0][i:i+20] for i in range(0,len(m[0]),20)),t)
        return t
    def reserve(value):
        reserved.append(value)
        return 'RESERVEDTOKEN'+str(len(reserved)-1)+'END'
    def link(m):
        label,url=m.groups()
        if url in {n+'.md' for _,n,_,_ in docs}:
            url=url[:-3]+'.pdf'
        return reserve('<link href="'+html.escape(url,quote=True)+'" color="#216479">'+display(label)+'</link>')
    s=re.sub(r'`([^`]+)`',lambda m:reserve(display(m[1])),s)
    s=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',link,s)
    s=display(s)
    s=re.sub(r'\*\*([^*]+)\*\*',r'<b>\1</b>',s)
    s=re.sub(r'\*([^*]+)\*',r'<i>\1</i>',s)
    for i,v in enumerate(reserved):s=s.replace('RESERVEDTOKEN'+str(i)+'END',v)
    s=re.sub(r'[\u4e00-\u9fff]+',lambda m:'<font name="Code">'+m[0]+'</font>',s)
    return s
fmt=format_text

def footer(c,d):
    w,h=c._pagesize;c.setFont('Body',8);c.setFillColor(colors.HexColor('#536970'))
    c.drawString(32,20,'PlantBioDesign V1.0 | Official public documentation | 2026-10-10')
    c.drawRightString(w-32,20,str(d.page))

audit=[]
for draft,name,source,tag in docs:
    pdf=out/(name+'.pdf')
    doc=AuditDocument(str(pdf),pagesize=A4,leftMargin=42,rightMargin=42,topMargin=40,bottomMargin=40,title=name.replace('_',' '),author='PlantBioDesign')
    templates=[]
    for tid,size in [('body',A4),('screen',landscape(A4)),('map',landscape(A3))]:
        w,h=size; templates.append(PageTemplate(id=tid,frames=[Frame(36 if tid!='body' else 42,40,w-(72 if tid!='body' else 84),h-80,id=tid)],pagesize=size,onPage=footer))
    doc.addPageTemplates(templates)
    styles['B'].leading=13; styles['B'].spaceAfter=7
    styles['H2x'].spaceBefore=14; styles['H2x'].spaceAfter=9
    styles['H3x'].spaceBefore=10; styles['H3x'].spaceAfter=7
    lines=(out/(name+'.md')).read_text(encoding='utf-8').splitlines()
    # Place the report-error illustration after the complete report discussion.
    if name=='PlantBioDesign_User_Manual':
        start=next(k for k,l in enumerate(lines) if l.startswith('![Figure 9.'))
        end=start+1
        while end<len(lines) and (not lines[end].strip() or lines[end].startswith('> ')):end+=1
        figure=lines[start:end]
        lines=lines[:start]+lines[end:]
        target=next(k for k,l in enumerate(lines) if l.startswith('## 13.'))
        lines=lines[:target]+figure+lines[target:]
    story=[];i=0
    while i<len(lines):
        line=lines[i].strip()
        if not line: i+=1;continue
        prefix='\n'.join(lines[:i+1])
        compact = name=='CASE_INPUT_REPRODUCIBILITY' or (name=='PlantBioDesign_User_Manual' and (('### 2.3' in prefix and '## 4.' not in prefix) or ('## 5.' in prefix and '## 7.' not in prefix) or ('### 10.1' in prefix and '## 13.' not in prefix)))
        styles['B'].fontSize=9 if name=='CASE_INPUT_REPRODUCIBILITY' else 9.5
        styles['B'].leading=11 if name=='CASE_INPUT_REPRODUCIBILITY' else 12 if compact else 13; styles['B'].spaceAfter=3 if name=='CASE_INPUT_REPRODUCIBILITY' else 4 if compact else 7
        styles['H2x'].spaceBefore=11 if compact else 14; styles['H2x'].spaceAfter=7 if compact else 9
        styles['H3x'].spaceBefore=8 if compact else 10; styles['H3x'].spaceAfter=5 if compact else 7
        if line.startswith('```'):
            code=[];i+=1
            while not lines[i].startswith('```'):code.append(lines[i]);i+=1
            longest=max(pdfmetrics.stringWidth(l,'Code',1) for l in code)
            fs=min(8, (A4[0]-100)/max(longest,1),690/(len(code)*1.32))
            st=ParagraphStyle('codex',fontName='Code',fontSize=fs,leading=fs*(1.20 if name=="PlantBioDesign_User_Manual" and 120 < i < 151 else 1.32),spaceAfter=10,backColor=colors.HexColor('#f2f5f6'),borderPadding=6)
            story.append(KeepTogether([Preformatted('\n'.join(code),st)]));i+=1;continue
        if line.startswith('!['):
            m=re.match(r'!\[(.*?)\]\((.*?)\)',line); caption,path=m.groups();tid='map' if path.endswith('native-export.png') else 'screen'
            if len(story)>=2 and isinstance(story[-1],PageBreak) and isinstance(story[-2],NextPageTemplate):
                story=story[:-2]
            story.extend([NextPageTemplate(tid),PageBreak()]);size=landscape(A3) if tid=='map' else landscape(A4)
            story.append(Paragraph(fmt(caption),styles['Cap']))
            notes=[];j=i+1
            while j<len(lines) and not lines[j].strip(): j+=1
            if j<len(lines) and lines[j].startswith('> '): notes=[lines[j][2:]];i=j
            iw,ih=PILImage.open(out/path).size;w=size[0]-84;maxh=size[1]-140-(45 if notes else 0);scale=min(w/iw,maxh/ih)
            story.append(Image(str(out/path),width=iw*scale,height=ih*scale))
            story.append(Spacer(1,8))
            for note in notes:story.append(Paragraph(fmt(note),styles['Note']))
            story.extend([NextPageTemplate('body'),PageBreak()]);i+=1;continue
        if line.startswith('|'):
            rows=[]
            while i<len(lines) and lines[i].strip().startswith('|'):
                cells=lines[i].strip().strip('|').split('|')
                # boundary 27|28 occurs only outside Markdown tables in these documents
                if not all(re.fullmatch(r'\s*:?-+:?\s*',c) for c in cells): rows.append([Paragraph(fmt(c.strip(),True),styles['Cell']) for c in cells])
                i+=1
            n=len(rows[0]); widths=[(A4[0]-84)/n]*n
            if n==5: widths=[65,70,155,42,A4[0]-84-332]
            t=Table(rows,colWidths=widths,repeatRows=1,hAlign='LEFT')
            pad=4 if compact else 6
            t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e5eff1')),('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),.35,colors.HexColor('#b8c9ce')),('TOPPADDING',(0,0),(-1,-1),pad),('BOTTOMPADDING',(0,0),(-1,-1),pad)]))
            story.extend([t,Spacer(1,9)]);continue
        if line.startswith('#'):
            level=len(line)-len(line.lstrip('#'))
            st=styles['H1x' if level==1 else 'H2x' if level==2 else 'H3x'].clone('heading')
            if line.startswith('## 13.'):st.keepWithNext=False
            story.append(Paragraph(fmt(line[level:].strip()),st));i+=1;continue
        p=[line[2:] if line.startswith('> ') else line];i+=1
        while i<len(lines) and lines[i].strip() and not re.match(r'^(#|\||!\[|```|\d+\. |>)',lines[i]):p.append(lines[i]);i+=1
        story.append(Paragraph(fmt(' '.join(p)),styles['Note' if line.startswith('> ') else 'B']))
    if isinstance(story[-1],PageBreak):story=story[:-2]
    doc.build(story)
