import json,re,glob
data=json.load(open('data.json',encoding='utf8'))
order={c['id']:n for n,c in enumerate(data)}
bank={}
for c in data:
    for i,w in enumerate(c['words']):
        s=w['w']
        if '…' in s: continue
        bank.setdefault(s,[]).append((c['id'],i))
MAXL=max(len(k) for k in bank)
PAT=[]
for c in data:
    for i,w in enumerate(c['words']):
        if '…' in w['w']:
            parts=[p for p in w['w'].split('…') if p]
            if len(parts)==1: bank.setdefault(parts[0],[]).append((c['id'],i))
            else: PAT.append((parts,f"{c['id']}|{i}",c['id']))
def ref_of(cid,w):
    c=[c for c in data if c['id']==cid][0]
    return f"{cid}|{[x['w'] for x in c['words']].index(w)}"
for p1,p2,cid,w in [('盖','被子','6.2','盖被子'),('叹','气','6.3','叹气'),('付','款','7.1','付款'),('拖','地','7.3','拖地'),('利','弊','7.3','利弊'),('遭','罪','6.3','遭罪'),('爬','山','8.1','爬山'),('转','圈','6.1','转圈')]:
    PAT.append(([p1,p2],ref_of(cid,w),cid))
def pick(word,cid,nxt,prev):
    opts=bank[word]
    if word=='还' and cid=='2.4':
        if nxt in '书。，' : return '2.4|'+str([i for c,i in opts if c=='2.4'][0])
        return '2.1|'+str([i for c,i in opts if c=='2.1'][0])
    for c,i in opts:
        if c==cid: return f'{c}|{i}'
    c,i=min(opts,key=lambda o:order[o[0]])
    return f'{c}|{i}'
def skip(word,nxt,prev):
    if word=='长' and nxt in '得着了胖满成起出大': return True
    if word=='得' and prev not in '们我你他她就都也还': return True
    if word=='转' and nxt in '两个一': return True
    if word=='种' and nxt in '了花树菜': return True
    if word=='为' and nxt in '主题': return True
    if word=='还' and nxt in '是': return False
    if word=='花' and nxt in '园草瓣': return True
    NUM='几一二三四五六七八九十两哪这那每'
    if word=='好' and nxt not in '大小多久漂高重累忙远近冷热快慢贵难可开': return True
    if word=='打' and nxt not in '球篮网羽排乒板橄高': return True
    if word in ('门','口','节') and prev not in NUM: return True
    if word=='行' and prev in '进银步自旅不': return True
    if word=='别' and nxt in '的人': return True
    if word=='行' and nxt in '李': return True
    return False
def tok(text,cid):
    out=[];buf=''
    pend={}
    for parts,ref,pc in PAT:
        a=text.find(parts[0])
        while a!=-1:
            b=text.find(parts[1],a+len(parts[0]))
            gap=b-a-len(parts[0])
            if b!=-1 and 0<gap<=(8 if len(parts[0])==1 else 15) and (pc==cid or len(parts[0])>1):
                pend[a]=(parts[0],ref); pend[b]=(parts[1],ref)
            a=text.find(parts[0],a+1)
    def flush():
        nonlocal buf
        if buf: out.append(buf); buf=''
    i=0
    while i<len(text):
        if text[i]=='{':
            j=text.index('}',i); inner=text[i+1:j]; t,py=inner.split('|')
            flush()
            if t in bank: out.append([t,pick(t,cid,'','')])
            else: out.append([t,None,py])
            i=j+1; continue
        if i in pend:
            w,ref=pend[i]; flush(); out.append([w,ref]); i+=len(w); continue
        hit=None
        for L in range(min(MAXL,len(text)-i),0,-1):
            w=text[i:i+L]
            if w in bank:
                nxt=text[i+L] if i+L<len(text) else ''; prev=text[i-1] if i else ''
                if skip(w,nxt,prev): continue
                hit=w
                if not any(c==cid for c,_ in bank[w]):
                    for L2 in range(L-1,1,-1):
                        w2=text[i:i+L2]
                        if w2 in bank and any(c==cid for c,_ in bank[w2]): hit=w2;break
                break
        if hit:
            flush(); nxt=text[i+len(hit)] if i+len(hit)<len(text) else ''
            out.append([hit,pick(hit,cid,nxt,text[i-1] if i else '')]); i+=len(hit)
        else: buf+=text[i]; i+=1
    flush(); return out
chap={};cur=None;pas=None
files=sorted(glob.glob('texts/*.txt'))
for f in files:
    for raw in open(f,encoding='utf8'):
        line=raw.rstrip('\n')
        if not line.strip(): continue
        if line.startswith('@'):
            cur=line[1:].strip(); chap[cur]=[]; continue
        if line.startswith('## '):
            p=line[3:].split('|'); pas={'zh':p[0],'en':p[1],'type':p[2],'title':p[3] if len(p)>3 else '','blocks':[]}
            if pas['title']: pas['titleT']=tok(pas['title'],cur)
            chap[cur].append(pas); continue
        k='p'; t=line
        m={'<':'line','>':'right','^':'diary','#':'head','~':'src','=':'intro'}
        if t[0] in m: k=m[t[0]]; t=t[1:]
        b={'k':k}
        if pas['type']=='d' and k=='p':
            mm=re.match(r'^([^：]{1,8})：(.*)$',t)
            if mm: b['k']='turn'; b['sp']=tok(mm.group(1),cur); t=mm.group(2)
        b['t']=tok(t,cur) if k!='src' else [t]
        pas['blocks'].append(b)
missing=[c['id'] for c in data if c['id'] not in chap]
print('chapters',len(chap),'missing',missing)
n=sum(1 for c in chap.values() for p in c for b in p['blocks'] for x in b['t'] if isinstance(x,list) and x[1])
print('vocab links',n, 'passages',sum(len(v) for v in chap.values()))
json.dump(chap,open('texts.json','w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
# coverage: which current-chapter words appear
for cid,ps in chap.items():
    used={x[1] for p in ps for b in p['blocks'] for x in b['t']+b.get('sp',[]) if isinstance(x,list) and x[1] and x[1].startswith(cid+'|')}
    c=[c for c in data if c['id']==cid][0]
    miss=[w['w'] for i,w in enumerate(c['words']) if not w.get('x') and f'{cid}|{i}' not in used]
    if miss: print(cid,'not linked:',' '.join(miss))
