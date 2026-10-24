"""Rebuild index.html (and optionally the single-file offline version) from source/template.html + data/*.json.

    python3 build.py            -> index.html (loads audio/ and ptext/ next to it)
    python3 build.py --offline  -> also Mandarin-Word-Bank-offline.html with every audio file embedded
"""
import json, os, glob, base64, sys, subprocess
ROOT = os.path.dirname(os.path.abspath(__file__))
P = lambda *a: os.path.join(ROOT, *a)
t = open(P('source', 'template.html'), encoding='utf8').read()
R = {'__DATA__': 'data.json', '__CHARS__': 'chars.json', '__TEXTS__': 'texts.json', '__PDURS__': 'pdurs.json',
     '__QS__': 'qs.json', '__PATS__': 'patterns.json', '__PHR__': 'phrases.json', '__AUDIOIDX__': 'audio-index.json'}
for k, f in R.items():
    t = t.replace(k, open(P('data', f), encoding='utf8').read())
page = '<!doctype html>\n<html lang="en"><head><meta name="viewport" content="width=device-width, initial-scale=1">\n' + t.replace('</style>', '</style></head><body>', 1) + '\n</body></html>'
open(P('index.html'), 'w', encoding='utf8').write(page)
print('wrote index.html')
if '--offline' in sys.argv:
    old = "(ctx ? fetch('audio/' + id + '.mp3') : Promise.reject(new Error('no audio')))\n      .then(r => { if (!r.ok) throw new Error('HTTP ' + r.status); return r.arrayBuffer(); })"
    o = page.replace(old, "(ctx ? Promise.resolve(Uint8Array.from(atob(EMBED[id]), c => c.charCodeAt(0)).buffer) : Promise.reject(new Error('no audio')))")
    def enc(path, br, ar):  # re-encode smaller if ffmpeg is available, else embed as-is
        try:
            return subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', path, '-ac', '1', '-ar', ar, '-b:a', br, '-f', 'mp3', '-'], capture_output=True, check=True).stdout
        except Exception:
            return open(path, 'rb').read()
    emb = {os.path.basename(f)[:-4]: base64.b64encode(enc(f, '20k', '22050')).decode() for f in glob.glob(P('audio', '*.mp3'))}
    pemb = {os.path.basename(f)[:-4].replace('_', '|'): base64.b64encode(enc(f, '16k', '16000')).decode() for f in glob.glob(P('ptext', '*.mp3'))}
    o = o.replace("const AIDX = ", "const EMBED = " + json.dumps(emb) + ";\nconst PEMBED = " + json.dumps(pemb) + ";\nconst AIDX = ", 1)
    open(P('Mandarin-Word-Bank-offline.html'), 'w', encoding='utf8').write(o)
    print('wrote Mandarin-Word-Bank-offline.html')
