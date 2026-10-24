import json,numpy as np,sherpa_onnx,subprocess
from prep import prep
d='matcha-icefall-zh-baker'
cfg=sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(
  matcha=sherpa_onnx.OfflineTtsMatchaModelConfig(acoustic_model=f'{d}/model-steps-3.onnx',vocoder='vocos-22khz-univ.onnx',lexicon=f'{d}/lexicon.txt',tokens=f'{d}/tokens.txt',dict_dir=f'{d}/dict'),num_threads=2),
  rule_fsts=f'{d}/phone.fst,{d}/date.fst,{d}/number.fst')
tts=sherpa_onnx.OfflineTts(cfg)
G=json.load(open('../phrases.json',encoding='utf8')); P=json.load(open('../patterns.json',encoding='utf8'))
items=[]
for g in G:
    for i,it in enumerate(g['items']): items.append((f"{g['id']}|{i}",it['zh']))
for i,p in enumerate(P): items.append((f"pm|{i}",p['model']))
for i,p in enumerate(P):
    for j,e in enumerate(p['ex']):
        if 'ref' not in e: items.append((f"pe|{i}|{j}",e['s']))
pcm=[];pos=0;idx={};sr=None;gap=None
for key,text in items:
    t=prep(text.replace('……','，').replace('…','，'))
    ent=[]
    for sp in (0.95,0.7):
        a=tts.generate(t,sid=0,speed=sp); sr=a.sample_rate; s=np.array(a.samples,dtype=np.float32)
        nz=np.where(np.abs(s)>0.01)[0]
        if len(nz): s=s[max(0,nz[0]-400):min(len(s),nz[-1]+1500)]
        s=s/max(0.05,np.abs(s).max())*0.9
        if gap is None: gap=np.zeros(int(sr*0.3),dtype=np.float32)
        pcm+=[s,gap]; ent.append([round(pos/sr,3),round(len(s)/sr,3)]); pos+=len(s)+len(gap)
    idx[key]=ent
raw=(np.clip(np.concatenate(pcm),-1,1)*32767).astype('<i2').tobytes()
subprocess.run(['ffmpeg','-y','-loglevel','error','-f','s16le','-ar',str(sr),'-ac','1','-i','-','-c:a','libmp3lame','-b:a','32k','out/x.mp3'],input=raw,check=True)
json.dump(idx,open('out/x.json','w'))
print('x',len(idx),round(pos/sr),'s')
