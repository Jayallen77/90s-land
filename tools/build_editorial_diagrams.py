#!/usr/bin/env python3
"""Source-controlled explanatory figures, with no simulated period photographs."""
import argparse,hashlib,json,subprocess
from pathlib import Path
from html import escape as esc
ROOT=Path(__file__).resolve().parents[1]
INK='#25133e';PAPER='#fff2d4';PINK='#ed68a5';BLUE='#71cbd3';YELLOW='#ffcb55';PURPLE='#7053a4'
def text(x,y,value,size=34,fill=INK,weight='normal',anchor='start'):
 return f'<text x="{x}" y="{y}" fill="{fill}" font-family="Arial, sans-serif" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{esc(value)}</text>'
def rect(x,y,w,h,fill,rx=0,stroke=INK):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="4"/>'
def line(x,y,x2,y2,color=INK,width=5):return f'<path d="M{x},{y} L{x2},{y2}" fill="none" stroke="{color}" stroke-width="{width}"/>'
def circle(x,y,r,fill,stroke=INK):return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="4"/>'
def label(x,y,value):return text(x,y,value,22,INK,'bold')
def frame(title,kicker,body,foot):
 return f'<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="800" viewBox="0 0 1280 800" role="img"><title>{esc(title)}</title><rect width="1280" height="800" fill="{PAPER}"/>{rect(20,20,1240,760,PAPER,10)}{rect(20,20,1240,76,INK,8)}{text(54,69,kicker,27,PAPER,"bold")}{text(54,164,title,53,INK,"bold")}{body}{text(54,748,foot,23,INK)} </svg>'
def pc(x,y,name):return rect(x,y,150,102,BLUE,6)+rect(x+12,y+12,126,66,INK)+line(x+75,y+103,x+75,y+124)+line(x+45,y+126,x+105,y+126)+text(x+75,y+164,name,27,INK,'bold','middle')
D={}
def add(id,title,kicker,body,foot,caption,alt,sources):D[id]={'svg':frame(title,kicker,body,foot),'caption':caption,'alt':alt,'sourceIds':sources}
# A budget, not copied game icons or a screenshot of a real card.
b=''
for i in range(15):
 x=70+(i%5)*228;y=225+(i//5)*125;c=BLUE if i<5 else PINK if i<8 else PAPER
 b+=rect(x,y,205,102,c,8)+text(x+102,y+67,str(i+1).zfill(2),43,INK,'bold','middle')
b+=rect(70,635,25,25,BLUE)+text(110,658,'GT: 5',26)+rect(340,635,25,25,PINK)+text(380,658,'FF VII: 3 × 1',26)+rect(710,635,25,25,PAPER)+text(750,658,'FREE: 7',26)
add('memory-blocks','FIFTEEN BLOCKS. YOUR CHOICE.','WORKED EXAMPLE / ORIGINAL PLAYSTATION',b,'Illustrative allocation • Gran Turismo game data + three Final Fantasy VII saves','Original diagram: five Gran Turismo game-data blocks, three one-block Final Fantasy VII saves and seven free blocks. Replays are not included.','A numbered 15-block grid: 1–5 blue for Gran Turismo, 6–8 pink for three Final Fantasy VII saves, 9–15 empty.',['ps-memory','sprint-gt-manual','sprint-ff7-package'])
b=''
for row,order in enumerate([[0,1,2,3],[0,2,2,3]]):
 b+=label(62,247+row*200,'SOURCE ORDER' if row==0 else 'EDITED ORDER')
 for j,n in enumerate(order):
  x=300+j*212;y=205+row*200;c=[BLUE,PINK,YELLOW,'#b8a2dc'][n]
  b+=rect(x,y,190,130,c,5)+text(x+95,y+73,chr(65+n),50,INK,'bold','middle')
  for k in range(8):b+=line(x+20+k*20,y+103,x+20+k*20,y+103-((k*7+n*11)%40),INK,3)
 for j in range(4):b+=text(395+j*212,370+row*200,str(j+1),29,INK,'normal','middle')
b+=text(60,651,'CHOOSE A REGION → REPEAT IT → CHANGE THE ORDER',34,INK,'bold')
add('break-slices','THE BREAK IS MATERIAL.','A TEACHING PATTERN / NOT A SONG TRANSCRIPTION',b,'Original diagram • no audio or proprietary waveform reproduced','Original teaching diagram: A–B–C–D becomes A–C–C–D over the same four-count framework. It is not a transcription of the Amen break or Original Nuttah.','Four colored sample regions A B C D, followed by a rearranged sequence A C C D.',['sprint-shy-interview'])
b=''
for i,(album,year,track,color) in enumerate([('BLUE LINES','1991','Unfinished Sympathy',BLUE),('DUMMY','1994','Roads',PINK),('MAXINQUAYE','1995','Black Steel',YELLOW)]):
 x=72+i*406;b+=circle(x+165,390,145,INK)+circle(x+165,390,67,color)+circle(x+165,390,12,PAPER)+text(x+165,238,year,34,INK,'bold','middle')+text(x+165,592,album,32,INK,'bold','middle')+text(x+165,639,track,27,INK,'normal','middle')
add('bristol-listening','THREE RECORDS. THREE ROOMS.','BRISTOL / A LISTENING ROUTE',b,'Original listening map • text labels, not reproduced album artwork','Original listening map for Blue Lines (1991), Dummy (1994) and Maxinquaye (1995), with one starting track from each.','Three stylized records labeled Blue Lines 1991, Dummy 1994 and Maxinquaye 1995, with Unfinished Sympathy, Roads and Black Steel.',['sprint-blue-lines','sprint-dummy','sprint-tricky'])
b=''
for i,(name,track,word,color) in enumerate([('TLC','Waterfalls','CONTRAST',PINK),('MARY J. BLIGE','My Life','WEIGHT',BLUE),('ERYKAH BADU','On & On','SPACE',YELLOW)]):
 x=80+i*405;b+=rect(x,233,355,425,color,18)+rect(x+134,280,86,160,PAPER,42)+line(x+177,440,x+177,510)+line(x+113,510,x+241,510)+text(x+177,564,name,30,INK,'bold','middle')+text(x+177,608,track,27,INK,'normal','middle')+text(x+177,692,word,28,INK,'bold','middle')
add('rnb-voices','FOLLOW THE VOICE.','R&B / THREE WAYS TO LISTEN',b,'Original listening guide • comparison prompts, not a vocal transcription','Original listening guide: TLC’s contrast, Mary J. Blige’s vocal weight and Erykah Badu’s space between phrases.','Three illustrated microphones labeled TLC Waterfalls, Mary J. Blige My Life and Erykah Badu On and On.',['sprint-tlc','sprint-mary-life','sprint-badu'])
b=rect(65,220,730,448,INK,16)
for i,(rank,name) in enumerate([(1,'BACKSTREET BOYS'),(2,'’N SYNC'),(3,'AALIYAH + TIMBALAND')]):
 y=298+i*142;b+=text(105,y,str(rank).zfill(2),64,[YELLOW,PINK,BLUE][i],'bold')+text(225,y-8,name,32,PAPER,'bold')+line(225,y+23,745,y+23,PURPLE,3)
b+=text(865,300,'SEP',56,INK,'bold')+text(855,442,'14',150,INK,'bold')+text(865,520,'1998',56,INK,'bold')+text(855,612,'FIRST COUNTDOWN',23,INK,'bold')
add('trl-countdown','WHO GOT NUMBER ONE?','TRL / A DATED SNAPSHOT',b,'Top three from ATRL’s archived recap • fan archive, not an official vote ledger','Original chart of the first three places in ATRL’s September 14, 1998 TRL recap. Full countdown and archive provenance appear in the article.','First three in the fan-archived September 14 1998 TRL countdown: Backstreet Boys, N Sync, Aaliyah with Timbaland.',['sprint-trl-recap','trl-retrospective'])
b=rect(76,228,490,420,PINK,12)+rect(660,228,540,420,BLUE,12)
b+=text(115,293,'THE SINGLE',38,INK,'bold')+circle(322,440,108,INK)+circle(322,440,30,PAPER)+text(115,612,'Sour Times',38,INK,'bold')
b+=text(705,293,'THE ALBUM',38,INK,'bold')+rect(705,330,450,220,PAPER,8)+text(745,394,'PORTISHEAD',43,INK,'bold')+text(745,455,'DUMMY',43,INK,'bold')+text(745,510,'Sour Times / Roads / Glory Box',22)+text(705,612,'What comes after the hit?',29,INK,'bold')
add('record-shop-choice','WHAT DID YOU COME IN FOR?','AT THE RECORD COUNTER / AN ILLUSTRATIVE CHOICE',b,'Original package diagram • no album artwork reproduced','Original comparison of buying a familiar single or following it into Portishead’s Dummy. Stylized packages are explanatory, not period sleeve reproductions.','A single labeled Sour Times beside an album labeled Dummy, listing Sour Times, Roads and Glory Box.',['sprint-dummy'])
# Schematic topology, explicitly not a scale reproduction of the source map.
b=line(200,435,1070,435,PURPLE,24)+line(1010,435,1010,265,PURPLE,24)
for x,y,w,h,name,c in [(65,340,210,200,'ROBINSONS-MAY',BLUE),(315,235,235,135,'JCPENNEY',BLUE),(400,405,270,72,'AMC EL CON SIX',YELLOW),(650,535,210,130,'DILLARD’S',BLUE),(935,505,270,150,'MONTGOMERY WARD',BLUE),(895,210,310,110,'THE PAVILION',PINK)]:
 b+=rect(x,y,w,h,c,6)+text(x+w/2,y+h/2+8,name,23,INK,'bold','middle')
b+=circle(750,435,18,YELLOW)+text(670,358,'MEET HERE',26,INK,'bold')+text(895,360,'FOOD COURT ↑',24,INK,'bold')
add('mall-route','MEET BY THE MAP.','EL CON MALL / TUCSON',b,'Schematic from a surviving 1990s directory • photographed 2009 • not to scale','Original orientation diagram based on the surviving El Con Mall directory. Locations are schematic; the source map is reproduced with its own attribution in the article.','Schematic El Con Mall route between Robinsons-May, JCPenney, AMC El Con Six, Dillard’s, Montgomery Ward and The Pavilion food court.',['sprint-mall-map'])
b=line(210,440,1060,440,INK,8)
for x,c in [(240,PINK),(640,BLUE),(1040,YELLOW)]:b+=circle(x,440,24,c)
b+=text(240,300,'1992',50,INK,'bold','middle')+text(240,526,'TIE-TOP HATS',31,INK,'bold','middle')+text(240,576,'Hollis, Queens',27,INK,'normal','middle')
b+=text(640,300,'1995',50,INK,'bold','middle')+text(640,526,'SPORTSWEAR',31,INK,'bold','middle')+text(640,576,'A larger line',27,INK,'normal','middle')
b+=text(1040,300,'ON SCREEN',36,INK,'bold','middle')+text(1040,526,'LL COOL J',31,INK,'bold','middle')+text(1040,576,'The Gap example',27,INK,'normal','middle')+text(640,665,'FOR US, BY US',48,INK,'bold','middle')
add('fubu-garment','A NAME PEOPLE COULD WEAR.','FUBU / FROM A HOUSE TO THE SCREEN',b,'Original diagram based on the founders’ history • commercial appearance not dated here','Original FUBU history diagram: the 1992 founders and tie-top hats, the 1995 sportswear line, and LL Cool J’s documented Gap-commercial crossover.','A FUBU history route from 1992 tie-top hats in Hollis to a 1995 sportswear line and LL Cool J’s Gap commercial.',['new-fubu-history','polish-fubu-gap'])
b=pc(85,235,'PLAYER 1 / HOST')+pc(1040,235,'PLAYER 2')+pc(85,495,'PLAYER 3')+pc(1040,495,'PLAYER 4')
for x,y in [(235,285),(1040,285),(235,545),(1040,545)]:b+=line(x,y,640,440,PURPLE,7)
b+=rect(495,375,290,125,YELLOW,12)+text(640,429,'ETHERNET HUB',29,INK,'bold','middle')
for x in range(535,755,45):b+=rect(x,456,22,16,INK,1)
b+=text(360,644,'ONE CABLE FROM EACH PC TO THE HUB',30,INK,'bold')
add('lan-network','GET THE ROOM CONNECTED.','QUAKE-ERA LOCAL PLAY / ONE POSSIBLE SETUP',b,'Illustrative 10BASE-T star network • the host computer runs the session','Original diagram of a four-PC 10BASE-T Ethernet LAN. Each PC connects to a hub; player one also hosts the game. Other period network arrangements differed.','Four computers connected separately to an Ethernet hub; player one is identified as the host.',['quake-anniversary','chm-net'])
b=rect(60,225,535,445,BLUE,16)+rect(675,225,545,445,PINK,16)
b+=text(100,287,'SCREAM / 1996',35,INK,'bold')+text(715,287,'BLAIR WITCH / 1999',32,INK,'bold')
b+='<path d="M175 350 Q140 440 255 530 L290 485 Q240 455 217 415 L250 380Z" fill="'+INK+'"/>'+line(290,520,435,590,INK,8)
b+=rect(795,355,265,175,INK,10)+circle(928,442,63,PAPER)+circle(928,442,33,INK)+rect(1060,385,65,110,INK,5)
b+=text(110,618,'WHAT DO YOU KNOW?',29,INK,'bold')+text(735,618,'WHAT CAN YOU SEE?',29,INK,'bold')
add('horror-information','TWO WAYS TO HIDE THE THREAT.','HORROR / AN ANNOTATED COMPARISON',b,'Original scene-analysis diagram • no production stills or costume photographs','Original comparison: Scream turns genre knowledge into tension; The Blair Witch Project restricts what the recording can show. Scene spoilers are labeled in the article.','A telephone for Scream 1996 beside a camera for The Blair Witch Project 1999, contrasting knowledge and limited viewpoint.',['polish-scream','polish-blair'])
b=''
for i,(month,day,title,c) in enumerate([('MAY','24','MISSION: IMPOSSIBLE',PINK),('JUNE','07','THE ROCK',BLUE),('JULY','03','INDEPENDENCE DAY',YELLOW)]):
 x=55+i*410;b+=rect(x,235,370,420,c,15)+rect(x,235,370,70,INK,15)+text(x+185,285,month,35,PAPER,'bold','middle')+text(x+185,468,day,140,INK,'bold','middle')+text(x+185,575,title,24,INK,'bold','middle')+text(x+185,615,'US THEATRICAL OPENING',19,INK,'normal','middle')
add('summer-calendar','SUMMER AT THE MULTIPLEX.','1996 / PUT THE OPENING ON THE CALENDAR',b,'Original release-calendar diagram • US dates, not worldwide premieres','Original 1996 US opening-date diagram for Mission: Impossible (May 24), The Rock (June 7) and Independence Day (July 3).','Three calendar panels show May 24 Mission Impossible, June 7 The Rock and July 3 Independence Day, all 1996 US theatrical openings.',['release-1996'])
b=''
for i,(command,effect,c) in enumerate([('IDDQD','GOD MODE',PINK),('IDKFA','WEAPONS / AMMO / KEYS',BLUE),('IDSPISPOPD','THROUGH WALLS: DOOM',YELLOW),('IDCLIP','THROUGH WALLS: DOOM II','#b8a2dc')]):
 y=235+i*104;b+=rect(65,y,570,84,c,8)+text(95,y+56,command,44,INK,'bold')+text(680,y+54,effect,29,INK,'bold')
add('doom-commands','THE CODE NEEDS A VERSION.','CLASSIC PC DOOM / TYPE DURING PLAY',b,'Single-player • non-Nightmare difficulty • not modern console-port instructions','Original command reference for classic PC Doom and Doom II. Single-player and non-Nightmare conditions are explained in the article.','Four classic PC commands with effects: IDDQD god mode, IDKFA inventory, IDSPISPOPD Doom no-clipping and IDCLIP Doom II no-clipping.',['sprint-doom-code'])
b=rect(60,225,550,445,BLUE,16)+rect(670,225,550,445,PINK,16)
b+='<ellipse cx="335" cy="425" rx="118" ry="150" fill="'+PAPER+'" stroke="'+INK+'" stroke-width="6"/>'+rect(260,346,150,112,INK,6)
for x in [280,335,390]:b+=circle(x,500,13,PINK)
b+='<path d="M800 490 L810 340 L880 385 Q950 340 1020 385 L1090 340 L1100 490 Q950 580 800 490Z" fill="'+PAPER+'" stroke="'+INK+'" stroke-width="6"/>'+circle(900,447,23,INK)+circle(1000,447,23,INK)
b+=text(335,607,'BUTTONS + CARE ICONS',28,INK,'bold','middle')+text(950,607,'TOUCH + ROOM SENSORS',28,INK,'bold','middle')+text(335,275,'TAMAGOTCHI',32,INK,'bold','middle')+text(950,275,'ORIGINAL FURBY',32,INK,'bold','middle')
add('responsive-toys','TWO WAYS TO ASK FOR ATTENTION.','ORIGINAL-GENERATION BEHAVIOR / A COMPARISON',b,'Original schematic • functional shapes, not photographs of specific shell editions','Original functional comparison of original Tamagotchi care programs and original-generation Furby sensor interaction. Shapes are schematic, not a model-identification photograph.','A small three-button screen pet beside a larger eared toy, comparing Tamagotchi care icons with original Furby touch and room sensors.',['sprint-original-tamagotchi','sprint-furby-manual'])
LEADS={'the-secret-button-sequence':'doom-commands','holiday-toys-that-answered-back':'responsive-toys','after-school-on-trl':'trl-countdown','bristol-between-the-beats':'bristol-listening','breakbeats-change-the-clock':'break-slices','rnb-had-many-voices':'rnb-voices','record-store-discovery':'record-shop-choice','meet-me-at-the-mall':'mall-route','streetwear-the-logo-and-the-voice':'fubu-garment','lan-party-night':'lan-network','horror-knew-the-rules':'horror-information','summer-at-the-multiplex':'summer-calendar'}
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
 manifest=ROOT/'content/editorial/figures.json';figures=json.loads(manifest.read_text()) if manifest.exists() else {}
 media_path=ROOT/'content/editorial/story-media.json';media=json.loads(media_path.read_text());errors=[]
 for id,record in D.items():
  svg=ROOT/f'assets/editorial/diagrams/{id}.svg';png=ROOT/f'assets/media/stories/{id}-diagram.png'
  if args.check:
   if not svg.exists() or svg.read_text()!=record['svg']:errors.append('Stale SVG: '+id)
   if not png.exists() or hashlib.sha256(png.read_bytes()).hexdigest()!=figures.get(id,{}).get('sha256'):errors.append('Unreviewed raster: '+id)
   continue
  svg.parent.mkdir(parents=True,exist_ok=True);svg.write_text(record['svg'])
  subprocess.run(['node','tools/render_diagram.mjs',str(svg),str(png)],cwd=ROOT,check=True)
  figures[id]={'kind':'image','visualType':'explanatory-diagram','src':'/'+str(png.relative_to(ROOT)),'vectorSrc':'/'+str(svg.relative_to(ROOT)),'width':1280,'height':800,'caption':record['caption'],'alt':record['alt'],'depictedSubject':record['alt'],'sourceIds':record['sourceIds'],'credit':'90s.land','sourceUrl':'https://90s.land/credits/#original-diagrams','sourceIdentity':'90s.land:original-diagram:'+id,'license':'Original 90s.land artwork','licenseUrl':'https://90s.land/credits/#original-diagrams','usageTerms':'Original artwork created for 90s.land; all rights reserved. Historical facts are identified through the linked sources.','eraNote':record['caption'],'reviewedAt':'2026-11-05','sha256':hashlib.sha256(png.read_bytes()).hexdigest()}
 if not args.check:
  for story,id in LEADS.items():media[story]=figures[id]
  manifest.write_text(json.dumps(figures,ensure_ascii=False,indent=2)+'\n');media_path.write_text(json.dumps(media,ensure_ascii=False,indent=2)+'\n')
 print(f'{len(D)} explanatory diagrams; {len(LEADS)} distinct story leads; errors: {errors}')
 return bool(errors)
if __name__=='__main__':raise SystemExit(main())
