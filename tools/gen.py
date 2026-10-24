import sys,json,numpy as np,sherpa_onnx,subprocess
from prep import prep
d='matcha-icefall-zh-baker'
cfg=sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(
  matcha=sherpa_onnx.OfflineTtsMatchaModelConfig(acoustic_model=f'{d}/model-steps-3.onnx',vocoder='vocos-22khz-univ.onnx',lexicon=f'{d}/lexicon.txt',tokens=f'{d}/tokens.txt',dict_dir=f'{d}/dict'),num_threads=2),
  rule_fsts=f'{d}/phone.fst,{d}/date.fst,{d}/number.fst')
tts=sherpa_onnx.OfflineTts(cfg)
data=json.load(open('../data.json',encoding='utf8'))
for cid in sys.argv[1:]:
    c=[x for x in data if x['id']==cid][0]
    sr=None; pcm=[]; pos=0; idx=[]
    gap=None
    for w in c['words']:
        ent=[]
        for text,speed in (((w.get('say') or w['w']),0.9),((w.get('say') or w['w']),0.6),(w['s'],1.0),(w['s'],0.75)):
            a=tts.generate(prep(text),sid=0,speed=speed)
            sr=a.sample_rate; s=np.array(a.samples,dtype=np.float32)
            # trim leading/trailing near-silence
            nz=np.where(np.abs(s)>0.01)[0]
            if len(nz): s=s[max(0,nz[0]-400):min(len(s),nz[-1]+1500)]
            s=s/ max(0.05,np.abs(s).max())*0.9
            if gap is None: gap=np.zeros(int(sr*0.35),dtype=np.float32)
            pcm+= [s,gap]; ent.append([round(pos/sr,3),round(len(s)/sr,3)]); pos+=len(s)+len(gap)
        idx.append(ent)
    allp=np.concatenate(pcm); raw=(np.clip(allp,-1,1)*32767).astype('<i2').tobytes()
    subprocess.run(['ffmpeg','-y','-loglevel','error','-f','s16le','-ar',str(sr),'-ac','1','-i','-','-c:a','libmp3lame','-b:a','32k',f'out/{cid}.mp3'],input=raw,check=True)
    json.dump(idx,open(f'out/{cid}.json','w'))
    print(cid,round(pos/sr),'s',flush=True)
