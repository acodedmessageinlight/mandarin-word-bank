import json,re,jieba
from pypinyin import lazy_pinyin, Style
D='matcha-icefall-zh-baker'
lex={}
for l in open(f'{D}/lexicon.txt',encoding='utf8'):
    p=l.split()
    if p: lex[p[0]]=p[1:]   # last wins (check behaviour later)
jieba.set_dictionary(f'{D}/dict/jieba.dict.utf8'); jieba.load_userdict(f'{D}/dict/user.dict.utf8')
jieba.setLogLevel(60)
def engine(t):
    out=[]
    for w in jieba.cut(t,HMM=True):
        if not re.search(r'[一-鿿]',w): continue
        if w in lex: out+=[(w,' '.join(lex[w]))]
        else: out+=[(ch,' '.join(lex.get(ch,['?']))) for ch in w if '一'<=ch<='鿿']
    return out
def flat(e): return ' '.join(p for _,p in e).split()
def ref(t):
    return [x for x in lazy_pinyin(t,style=Style.TONE3,neutral_tone_with_five=True,v_to_u=False) if re.match(r'^[a-z]+\d$',x)]
norm=lambda s:s.replace('5','').replace('er','r') 
if __name__=='__main__':
  data=json.load(open('../data.json',encoding='utf8'))
  n=0
  for c in data:
    for w in c['words']:
      for t in (w.get('say') or w['w'], w['s']):
        t=t.replace('…','，')
        e=flat(engine(t)); r=ref(t)
        hz=[ch for ch in t if '一'<=ch<='鿿']
        if len(e)!=len(r): print('LEN',c['id'],t,e,r); continue
        diffs=[(hz[i] if i<len(hz) else '?',e[i],r[i]) for i in range(len(e)) if norm(e[i])!=norm(r[i]) and not(e[i][:-1]==r[i][:-1] and ('5' in r[i] or e[i][-1] not in '1234'))]
        # ignore 一/不 sandhi and 3-3 sandhi
        diffs=[d for d in diffs if d[0] not in '一不' and not(d[1][:-1]==d[2][:-1] and d[1][-1]=='2' and d[2][-1]=='3')]
        if diffs: n+=1; print(c['id'],t,diffs)
  print(n)
