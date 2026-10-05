#!/usr/bin/env python3
"""SavingsRE Market Intel email preview PNG (top 4 headlines).
Repo usage: python3 market/tools/market_news_image.py market/news_data.json market/market_data.json assets/2026-07-02_savingsre_img_market-intel-newsfeed_v01.png
The 4 Agile CRM campaigns reference that fixed asset URL, so overwriting it updates every email."""
import sys, json
from PIL import Image, ImageDraw, ImageFont

NAVY=(17,41,74); GOLD=(184,134,11); SLATE=(51,65,85); MUTED=(100,116,139)
BG=(247,249,252); CARD=(255,255,255); BORDER=(224,230,238); BLUE=(37,99,235)
W=1000

CATS={
 "Luxury":("LUXURY",(138,102,8),(245,237,216)),
 "Commercial/CRE":("COMMERCIAL",(31,71,126),(221,231,244)),
 "Multifamily":("MULTIFAMILY",(15,107,69),(220,239,230)),
 "Market Data":("MARKET DATA",(74,58,134),(231,227,244)),
 "Policy/Insurance":("INSURANCE",(143,50,43),(246,226,223)),
 "Development":("DEVELOPMENT",(91,82,64),(234,231,224)),
}
DEF=("NEWS",(74,58,134),(231,227,244))

DEJ="/usr/share/fonts/truetype/dejavu/"
def F(name,sz): return ImageFont.truetype(DEJ+name,sz)
f_word=F("DejaVuSerif-Bold.ttf",40); f_kick=F("DejaVuSans-Bold.ttf",17); f_upd=F("DejaVuSans.ttf",16)
f_title=F("DejaVuSerif-Bold.ttf",25); f_sum=F("DejaVuSans.ttf",17)
f_date=F("DejaVuSans-Bold.ttf",14); f_chip=F("DejaVuSans-Bold.ttf",13); f_src=F("DejaVuSans-Bold.ttf",13)

def fmt_date(s):
    import datetime
    try:
        d=datetime.date.fromisoformat(s)
        return d.strftime("%b %d, %Y").upper()
    except Exception:
        return (s or "").upper()

def wrap(draw,text,font,maxw,maxlines):
    words=(text or "").split(); lines=[]; cur=""; truncated=False
    for idx,w in enumerate(words):
        t=(cur+" "+w).strip()
        if draw.textlength(t,font=font)<=maxw: cur=t
        else:
            lines.append(cur); cur=w
            if len(lines)==maxlines-1:
                rest=" ".join(words[idx:]); cur=rest; truncated=True; break
    if cur and len(lines)<maxlines: lines.append(cur)
    if truncated and lines:
        while lines[-1] and draw.textlength(lines[-1]+"…",font=font)>maxw: lines[-1]=lines[-1].rsplit(" ",1)[0] if " " in lines[-1] else lines[-1][:-1]
        lines[-1]=lines[-1].rstrip()+"…"
    return lines

def main():
    news_path,market_path,out_path=sys.argv[1],sys.argv[2],sys.argv[3]
    news=json.load(open(news_path,encoding="utf-8"))
    news=sorted(news,key=lambda x:x.get("date",""),reverse=True)[:4]
    try:
        rates=json.load(open(market_path,encoding="utf-8")).get("rates",{}).get("cards",[])
    except Exception:
        rates=[]

    pad=28; head_h=104; gap=16; cpad=18
    tmp=Image.new("RGB",(10,10)); td=ImageDraw.Draw(tmp)
    textx=pad+cpad+190
    wrapped=[]; cardhs=[]
    for it in news:
        tl=wrap(td,it.get("title",""),f_title,W-textx-pad-cpad-175,3)
        sl=wrap(td,it.get("summary",""),f_sum,W-textx-pad-cpad-90,2)
        h=max(cpad*2+len(tl)*32+8+len(sl)*24,96)
        wrapped.append((tl,sl)); cardhs.append(h)
    H=head_h+pad+sum(cardhs)+gap*(len(news)-1)+pad
    img=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(img)
    d.rectangle([0,0,W,head_h],fill=NAVY); d.rectangle([0,head_h-4,W,head_h],fill=GOLD)
    d.text((pad,26),"Savings",font=f_word,fill=(255,255,255))
    wx=d.textlength("Savings",font=f_word); d.text((pad+wx,26),"RE",font=f_word,fill=GOLD)
    kick="MARKET INTEL  ·  NEWS FEED"
    d.text((W-pad-d.textlength(kick,font=f_kick),34),kick,font=f_kick,fill=(233,214,160))
    upd="Curated weekly · savingsre.com/market"
    d.text((W-pad-d.textlength(upd,font=f_upd),62),upd,font=f_upd,fill=(180,196,220))
    cy=head_h+pad
    for i,it in enumerate(news):
        tl,sl=wrapped[i]; ch=cardhs[i]
        d.rounded_rectangle([pad,cy,W-pad,cy+ch],radius=10,fill=CARD,outline=BORDER,width=1)
        d.rectangle([pad,cy,pad+4,cy+ch],fill=GOLD)
        lx=pad+cpad
        d.text((lx,cy+cpad+2),fmt_date(it.get("date","")),font=f_date,fill=MUTED)
        lbl,cc,cbg=CATS.get(it.get("category",""),DEF)
        cw=d.textlength(lbl,font=f_chip)
        d.rounded_rectangle([lx,cy+cpad+24,lx+cw+20,cy+cpad+48],radius=12,fill=cbg)
        d.text((lx+10,cy+cpad+28),lbl,font=f_chip,fill=cc)
        tx=lx+190; ty=cy+cpad
        for ln in tl: d.text((tx,ty),ln,font=f_title,fill=NAVY); ty+=32
        ty+=6
        for ln in sl: d.text((tx,ty),ln,font=f_sum,fill=SLATE); ty+=24
        src=(it.get("source","") or "")[:26]
        d.text((W-pad-cpad-d.textlength(src,font=f_src),cy+cpad+2),src,font=f_src,fill=BLUE)
        cy+=ch+gap
    img.save(out_path)
    print("saved",out_path,img.size)

if __name__=="__main__":
    main()
