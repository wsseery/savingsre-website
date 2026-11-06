"""Flat illustrative SVG scenes for the /listings/ landing pages (generic, not real properties).

    python3 scripts/make_listing_illustrations.py assets/img/listings
"""
import random, sys, os
W,H=1200,450
GROUND=360
NAVY='#0a1628'; BLUE='#2563EB'
def sky(top='#cfe3ff',bot='#f4f8ff',sun=(980,95,46),sun_c='#ffd27a'):
    return (f'<defs><linearGradient id="sk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bot}"/></linearGradient>'
            f'<linearGradient id="sea" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3b82f6"/><stop offset="1" stop-color="#1d4ed8"/></linearGradient>'
            f'<linearGradient id="gl" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#bcd6fb"/><stop offset="1" stop-color="#7fa9ee"/></linearGradient></defs>'
            f'<rect width="{W}" height="{H}" fill="url(#sk)"/>'
            f'<circle cx="{sun[0]}" cy="{sun[1]}" r="{sun[2]}" fill="{sun_c}" opacity=".85"/>'
            + cloud(180,80,1)+cloud(620,60,.8))
def cloud(x,y,s):
    return (f'<g fill="#fff" opacity=".9" transform="translate({x} {y}) scale({s})">'
            '<ellipse cx="0" cy="10" rx="60" ry="16"/><ellipse cx="-22" cy="0" rx="26" ry="18"/><ellipse cx="18" cy="-4" rx="30" ry="22"/></g>')
def ground(c='#d9ead3',y=GROUND):
    return f'<rect y="{y}" width="{W}" height="{H-y}" fill="{c}"/><rect y="{y}" width="{W}" height="6" fill="#b9d3b0"/>'
def road(y=400):
    return f'<rect y="{y}" width="{W}" height="{H-y}" fill="#94a3b8"/>' + ''.join(f'<rect x="{x}" y="{y+22}" width="50" height="5" fill="#f8fafc"/>' for x in range(20,W,110))
def sea(y=300):
    return f'<rect y="{y}" width="{W}" height="{H-y}" fill="url(#sea)"/>' + ''.join(f'<path d="M{x} {y+18+((x//97)%4)*22} q15 -6 30 0" stroke="#bfdbfe" stroke-width="3" fill="none" opacity=".7"/>' for x in range(30,W,97))
def sand(y,h=40,x0=0,x1=W):
    return f'<rect x="{x0}" y="{y}" width="{x1-x0}" height="{h}" fill="#f3e3bf"/>'
def palm(x,base,h=150,s=1):
    t=base-h
    fr=''.join(f'<path d="M{x} {t} q{dx*0.5} {-18} {dx} {dy}" stroke="#2f855a" stroke-width="{9*s}" fill="none" stroke-linecap="round"/>' for dx,dy in [(-70,20),(-55,-10),(60,-12),(75,22),(-30,35),(35,38)])
    return f'<path d="M{x-6*s} {base} q10 {-h*0.5} 6 {-h}" stroke="#8b6b4a" stroke-width="{10*s}" fill="none" stroke-linecap="round"/>' + fr
def win_grid(x,y,w,h,cols,rows,pad=8,fill='url(#gl)',frame=None):
    out=[]; cw=(w-pad*(cols+1))/cols; ch=(h-pad*(rows+1))/rows
    for r in range(rows):
        for c in range(cols):
            out.append(f'<rect x="{x+pad+c*(cw+pad):.1f}" y="{y+pad+r*(ch+pad):.1f}" width="{cw:.1f}" height="{ch:.1f}" rx="2" fill="{fill}"/>')
    return ''.join(out)
def rect(x,y,w,h,f,rx=0,extra=''): return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{f}" {extra}/>'
def awning(x,y,w,c): 
    n=int(w//24); return ''.join(f'<path d="M{x+i*w/n:.1f} {y} h{w/n:.1f} l-4 22 h{-w/n+8:.1f} z" fill="{c if i%2==0 else "#fff"}"/>' for i in range(n))
def car(x,y,c):
    return f'<g transform="translate({x} {y})"><rect x="0" y="10" width="70" height="20" rx="8" fill="{c}"/><path d="M12 10 l10 -12 h26 l10 12z" fill="{c}"/><path d="M20 9 l7 -8 h18 l6 8z" fill="#dbeafe"/><circle cx="16" cy="30" r="7" fill="#1e293b"/><circle cx="54" cy="30" r="7" fill="#1e293b"/></g>'
def skyline(y=GROUND,c='#c7d6ee',seed=3):
    r=random.Random(seed); out=[]; x=0
    while x<W:
        w=r.randint(40,90); h=r.randint(60,200); out.append(rect(x,y-h,w,h,c)); x+=w+r.randint(4,14)
    return ''.join(out)
def door(x,y,w=34,h=60): return rect(x,y,w,h,'#334155',2)
def roof_tri(x,y,w,h,c): return f'<path d="M{x-10} {y} L{x+w/2} {y-h} L{x+w+10} {y} z" fill="{c}"/>'
def pool(x,y,w,h): return rect(x,y,w,h,'#38bdf8',6)+f'<path d="M{x+15} {y+h/2} q20 -8 40 0 t40 0" stroke="#e0f2fe" stroke-width="3" fill="none"/>'

S={}
S['storefronts']=lambda: sky()+ground()+road()+rect(120,200,960,160,'#f1e6d6')+rect(120,185,960,18,'#d6c3a5')+''.join(
    rect(140+i*188,250,150,110,'url(#gl)')+door(140+i*188+58,300,34,60)+awning(136+i*188,232,158,['#2563EB','#0f766e','#b45309','#be123c','#1d4ed8'][i])+rect(150+i*188,205,130,22,'#fff',3) for i in range(5))+palm(70,GROUND,170)+palm(1130,GROUND,150)+car(300,372,'#1d4ed8')+car(760,372,'#475569')
S['office-interior']=lambda: rect(0,0,W,H,'#e2e8f0')+'<svg x="60" y="40" width="1080" height="300">'+sky()+skyline(300,'#94acd6',5)+skyline(300,'#b8c8e6',9)+'</svg>'+''.join(rect(60+i*270,40,8,300,'#475569') for i in range(5))+rect(60,40,1088,8,'#475569')+rect(0,340,W,110,'#cbd5e1')+rect(380,300,440,16,'#78716c',3)+rect(400,316,10,60,'#57534e')+rect(790,316,10,60,'#57534e')+rect(470,250,60,50,'#1e293b',4)+rect(560,280,16,20,'#2f855a',3)+f'<ellipse cx="1040" cy="330" rx="40" ry="10" fill="#94a3b8"/>'+palm(1040,330,110,.7)
S['warehouse']=lambda: sky()+ground()+road(395)+rect(80,170,860,190,'#e5e7eb')+rect(80,160,860,14,'#9ca3af')+''.join(rect(120+i*120,250,90,110,'#64748b',2)+''.join(rect(120+i*120,252+k*14,90,2,'#475569') for k in range(7)) for i in range(6))+rect(870,290,40,70,'#334155')+'<g transform="translate(960 268)">'+rect(0,0,170,80,'#f8fafc',4)+rect(170,25,60,55,'#2563EB',6)+rect(185,32,30,20,'#dbeafe',2)+'<circle cx="35" cy="86" r="12" fill="#1e293b"/><circle cx="135" cy="86" r="12" fill="#1e293b"/><circle cx="205" cy="86" r="12" fill="#1e293b"/></g>'+palm(40,GROUND,150)
S['medical']=lambda: sky()+ground()+road()+rect(220,150,760,210,'#f8fafc')+rect(220,140,760,14,'#94a3b8')+win_grid(230,160,740,90,8,1)+win_grid(230,255,300,95,3,1)+win_grid(670,255,300,95,3,1)+rect(540,240,120,120,'url(#gl)')+rect(520,225,160,18,'#2563EB',3)+rect(596,250,4,110,'#64748b')+palm(130,GROUND,170)+palm(1080,GROUND,160)+car(300,372,'#0f766e')+car(820,372,'#64748b')
S['strip-center']=lambda: sky(sun=(1080,80,40))+rect(0,250,W,200,'#cbd5e1')+''.join(rect(90+i*62,330,4,60,'#f8fafc') for i in range(17))+rect(100,150,1000,110,'#f1e6d6')+rect(100,140,1000,14,'#b9a586')+''.join(rect(120+i*162,195,120,65,'url(#gl)')+awning(116+i*162,180,128,['#2563EB','#0f766e','#b45309','#be123c','#1d4ed8','#7c3aed'][i]) for i in range(6))+car(150,340,'#1d4ed8')+car(400,340,'#be123c')+car(710,340,'#475569')+car(960,340,'#0f766e')+palm(60,260,140)+palm(1150,260,130)
S['office-tower']=lambda: sky()+ground()+road()+skyline(GROUND,'#dbe4f3',11)+rect(430,50,340,310,'#1e3a8a')+win_grid(430,50,340,310,6,11,6)+rect(560,300,80,60,'#0f172a')+rect(400,340,400,20,'#cbd5e1')+palm(360,GROUND,150)+palm(840,GROUND,160)+car(180,372,'#64748b')
S['flex']=lambda: sky()+ground()+road()+rect(100,200,1000,160,'#e7e5e4')+rect(100,190,1000,14,'#a8a29e')+''.join(rect(120+i*246,230,100,130,'url(#gl)')+door(155+i*246,300,30,60)+rect(235+i*246,250,95,110,'#78716c',2)+''.join(rect(235+i*246,252+k*13,95,2,'#57534e') for k in range(8)) for i in range(4))+palm(60,GROUND,150)+palm(1140,GROUND,140)+car(500,372,'#2563EB')
S['mixed-use']=lambda: sky()+ground('#e2e8f0')+road()+rect(160,90,880,270,'#fde7c8')+rect(160,80,880,14,'#c2925d')+''.join(win_grid(180,105+r*75,840,60,8,1,14)+''.join(rect(185+c*105,160+r*75,90,6,'#7c5a35') for c in range(8)) for r in range(2))+''.join(rect(175+i*172,265,150,95,'url(#gl)')+awning(171+i*172,250,158,['#0f766e','#2563EB','#b45309','#be123c','#1d4ed8'][i]) for i in range(5))+palm(90,GROUND,170)+palm(1110,GROUND,160)
S['land']=lambda: sky()+skyline(262,'#dbe4f3',21)+rect(0,260,W,190,'#cfe5b8')+rect(0,260,W,6,'#a3c585')+''.join(f'<path d="M{x} {300+(x*7)%70} l6 -14 l6 14" stroke="#7aa35a" stroke-width="2" fill="none"/>' for x in range(30,W,53))+''.join(rect(x,y,6,40,'#b45309')+rect(x,y,6,8,'#f97316') for x,y in [(220,300),(980,300),(260,380),(940,380)])+'<path d="M223 304 L983 304 L943 384 L263 384 Z" stroke="#f97316" stroke-width="2" stroke-dasharray="10 8" fill="none"/>'+rect(560,250,8,90,'#64748b')+rect(510,220,110,40,'#f8fafc',4,'stroke="#2563EB" stroke-width="3"')+palm(80,270,150)+palm(130,270,120)+palm(1100,270,160)
S['nnn']=lambda: sky()+ground()+road()+rect(330,180,540,180,'#f5f5f4')+rect(310,165,580,22,'#0f766e',4)+rect(560,120,80,60,'#0f766e')+rect(350,230,500,80,'url(#gl)')+door(585,300,40,60)+rect(870,240,120,10,'#a8a29e')+rect(900,250,8,110,'#a8a29e')+car(940,340,'#be123c')+rect(130,230,10,130,'#64748b')+rect(95,190,80,50,'#f8fafc',4,'stroke="#0f766e" stroke-width="3"')+palm(250,GROUND,150)+palm(1110,GROUND,160)
S['small-mf']=lambda: sky()+ground()+road()+roof_tri(340,170,520,70,'#b45309')+rect(340,170,520,190,'#fef3c7')+win_grid(360,180,480,80,4,1,24)+win_grid(360,270,190,80,2,1,20)+win_grid(650,270,190,80,2,1,20)+door(570,300,30,60)+door(605,300,30,60)+rect(340,262,520,6,'#d6a85c')+palm(240,GROUND,160)+palm(960,GROUND,150)+car(1000,372,'#2563EB')
S['apartments']=lambda: sky()+ground()+road()+rect(260,80,680,280,'#e0e7ff')+rect(260,70,680,14,'#6366f1')+''.join(win_grid(280,95+r*65,640,45,7,1,16)+''.join(rect(285+c*92,140+r*65,80,6,'#475569') for c in range(7)) for r in range(4))+door(585,300,40,60)+palm(180,GROUND,170)+palm(1020,GROUND,160)+car(1070,372,'#475569')
S['apartment-complex']=lambda: sky()+ground()+''.join(rect(x,y,w,GROUND-y,c)+win_grid(x,y+10,w,GROUND-y-20,int(w//60),int((GROUND-y)//55),12) for x,y,w,c in [(60,140,320,'#e0e7ff'),(440,100,320,'#dbeafe'),(820,150,320,'#e0e7ff')])+pool(380,380,440,50)+palm(400,GROUND,130,.8)+palm(800,GROUND,140,.8)+rect(0,430,W,20,'#cbd5e1')
S['beach-cottage']=lambda: sky(top='#bfdbfe')+sea(250)+sand(300,150)+roof_tri(380,220,300,70,'#0e7490')+rect(380,220,300,110,'#fef9c3')+win_grid(395,235,120,60,2,1,8)+door(560,265,40,65)+rect(370,330,320,10,'#a8a29e')+palm(300,330,170)+palm(760,330,140)+f'<path d="M900 330 l40 -60 l40 60 z" fill="#f97316"/><rect x="938" y="270" width="4" height="70" fill="#78716c"/>'
S['luxury-home']=lambda: sky()+ground('#cfe5b8')+rect(220,150,520,160,'#f8fafc')+rect(640,200,360,110,'#f1f5f9')+rect(200,140,560,14,'#334155')+rect(620,190,400,12,'#334155')+win_grid(230,165,500,130,4,1,12)+win_grid(650,212,340,85,3,1,10)+rect(180,310,860,50,'#e7e5e4')+pool(280,320,560,32)+palm(120,GROUND,190)+palm(1080,GROUND,170)
S['oceanfront']=lambda: sky(sun=(220,90,46))+sea(250)+sand(320,130)+rect(560,150,460,170,'#f8fafc')+rect(540,140,500,14,'#334155')+win_grid(570,160,440,150,4,2,10)+pool(600,325,380,28)+palm(470,330,190)+palm(1100,330,170)+f'<path d="M200 360 l40 -50 l40 50 z" fill="#2563EB"/><rect x="238" y="310" width="4" height="60" fill="#78716c"/>'
S['intracoastal']=lambda: sky()+sea(310)+rect(0,240,W,72,'#cfe5b8')+rect(380,130,440,180,'#fffbeb')+roof_tri(380,130,440,60,'#9a3412')+win_grid(395,145,410,150,4,2,12)+rect(560,312,14,60,'#78716c')+rect(470,330,300,12,'#a16207')+'<g transform="translate(640 360)"><path d="M0 0 h220 l-30 30 h-170 z" fill="#f8fafc"/><rect x="60" y="-26" width="80" height="26" rx="4" fill="#e2e8f0"/><rect x="70" y="-20" width="60" height="12" fill="#93c5fd"/></g>'+palm(300,312,170)+palm(900,312,160)
S['country-club']=lambda: sky()+rect(0,230,W,220,'#a7d18c')+f'<ellipse cx="860" cy="360" rx="230" ry="50" fill="#86c06c"/>'+rect(900,280,4,70,'#f8fafc')+'<path d="M904 280 l40 12 l-40 12z" fill="#dc2626"/><circle cx="902" cy="352" r="5" fill="#1e293b"/>'+rect(120,160,440,170,'#fef3c7')+roof_tri(120,160,440,60,'#b45309')+win_grid(135,175,410,140,4,2,12)+door(320,270,40,60)+palm(620,330,170)+palm(80,330,150)+f'<ellipse cx="400" cy="420" rx="200" ry="20" fill="#e7d7a8"/>'
S['condo-tower']=lambda: sky()+sea(330)+sand(300,32)+rect(470,40,260,262,'#e2e8f0')+''.join(rect(470,58+r*26,260,8,'#94a3b8') for r in range(9))+win_grid(470,40,260,262,5,10,7)+rect(250,180,160,122,'#dbeafe')+win_grid(250,180,160,122,3,5,7)+rect(790,150,150,152,'#dbeafe')+win_grid(790,150,150,152,3,6,7)+palm(180,302,140)+palm(1020,302,150)
S['sfr-rent']=lambda: sky()+ground('#bfe0a8')+road()+rect(380,190,440,170,'#e0f2fe')+roof_tri(380,190,440,80,'#334155')+win_grid(400,210,140,90,2,1,10)+win_grid(660,210,140,90,2,1,10)+door(575,290,50,70)+rect(560,360,80,40,'#cbd5e1')+palm(270,GROUND,160)+palm(930,GROUND,150)+car(700,372,'#2563EB')
S['furnished']=lambda: rect(0,0,W,H,'#fdf6ec')+'<svg x="120" y="50" width="960" height="250">'+sky(sun=(780,60,36))+sea(130)+'</svg>'+''.join(rect(120+i*320,50,8,250,'#e7e5e4') for i in range(4))+rect(120,46,968,8,'#e7e5e4')+rect(0,330,W,120,'#e7d8c3')+rect(330,270,540,80,'#cbd5e1',18)+rect(350,240,500,50,'#e2e8f0',16)+rect(380,250,90,40,'#2563EB',10)+rect(730,250,90,40,'#0f766e',10)+rect(500,380,200,14,'#a16207',4)+rect(530,394,8,40,'#78716c')+rect(662,394,8,40,'#78716c')+palm(1110,330,120,.7)
S['ocean-view']=lambda: sky(top='#fbcfe8',bot='#fde68a',sun=(860,250,60),sun_c='#fb923c')+sea(260)+rect(0,330,W,120,'#e7e5e4')+''.join(rect(x,250,6,90,'#94a3b8') for x in range(0,W,60))+rect(0,250,W,8,'#64748b')+rect(0,258,W,80,'#e0f2fe',0,'opacity=".25"')+'<g transform="translate(180 330)"><path d="M0 40 L60 -20 L240 -20 L210 40 Z" fill="#f8fafc"/><rect x="10" y="40" width="8" height="40" fill="#64748b"/><rect x="190" y="40" width="8" height="40" fill="#64748b"/></g>'+rect(560,360,130,10,'#78716c',3)+rect(615,370,10,40,'#57534e')+'<circle cx="590" cy="350" r="10" fill="#f8fafc"/>'+palm(1080,340,170,.9)
S['hub']=lambda: sky()+sea(330)+skyline(330,'#bcd0ee',2)+skyline(330,'#93b1e3',7)+palm(80,340,150)+palm(1120,340,160)+sand(330,20)

def svg(key,title):
    body=S[key]()
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t"><title id="t">{title}</title>{body}</svg>')
if __name__=='__main__':
    out=sys.argv[1]; os.makedirs(out,exist_ok=True)
    for k in S:
        open(os.path.join(out,f'{k}.svg'),'w').write(svg(k,'Illustration: '+k.replace('-',' ')))
    print(len(S))
