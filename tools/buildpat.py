import json,re
exec(open('patterns.py').read())
data=json.load(open('data.json',encoding='utf8'))
texts=json.load(open('texts.json',encoding='utf8'))
def plain(toks): return ''.join(x if isinstance(x,str) else x[0] for x in toks)
sents=[]
for cid,ps in texts.items():
    for pi,p in enumerate(ps):
        for b in p['blocks']:
            if b['k']=='src': continue
            for s in re.findall(r'[^。！？!?]+[。！？!?”"]*',plain(b['t'])):
                s=s.strip().lstrip('”"：')
                if 4<len(s)<60: sents.append({'s':s,'src':f'{cid} 课文{"一二三"[pi]}','pid':f'{cid}|{pi+1}'})
vs=[]
for c in data:
    for i,w in enumerate(c['words']):
        if not w.get('x'): vs.append({'s':w['s'],'t':w['t'],'ref':f"{c['id']}|{i}",'src':c['id']})
out=[]
for (name,py,en,rx,expl,tmpl,model,tip) in P:
    R=re.compile(rx)
    a=[v for v in vs if R.search(v['s'])]; b=[s for s in sents if R.search(s['s'])]
    seen=set(); ex=[]
    for v in a:
        if v['s'] in seen: continue
        seen.add(v['s']); ex.append(v)
        if len(ex)>=4: break
    n=0
    for s in b:
        if s['s'] in seen: continue
        seen.add(s['s']); ex.append(s); n+=1
        if n>=4: break
    out.append({'name':name,'py':py,'en':en,'rx':rx,'expl':expl,'tmpl':tmpl,'model':model,'tip':tip,'ex':ex})
json.dump(out,open('patterns.json','w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
print(len(out))
for o in out:
    if o['name'] in ('A 没有 B 那么 + adjective','是……的','……才……','verb + 得 + description'): print(o['name'],[e['s'] for e in o['ex']])
for o in out:
    r=re.sub(r'\(\?<?[!=][^)]*\)','',o['rx']); r=re.sub(r'\[[^\]]*\]','',r)
    kw=set(re.findall(r'[一-鿿]+',r))
    o['kw']=sorted(kw)
json.dump(out,open('patterns.json','w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
print([ (o['name'],o['kw']) for o in out][:6])
