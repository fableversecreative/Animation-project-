import json, re
A="voice.mp3"
# speech segments from silencedetect -45 dB, d=0.18
sil=[(2.314,2.916),(4.323,4.782),(5.967,6.636),(9.796,10.024),(12.496,12.893),(16.102,16.583),(17.573,17.888),(19.538,19.968),(21.622,21.999),(23.739,23.994),(26.917,27.200),(29.121,29.374),(30.271,30.725),(33.040,33.321),(35.451,35.883),(36.303,36.724),(38.148,38.371),(39.919,40.249),(42.347,42.701),(44.018,44.199)]
segs=[]; t=0.08
for a,b in sil: segs.append((t,a)); t=b
phr=["Napoleon conquered half of Europe.","But he lost one battle...","to bunnies.",
"In 1807, after signing a big peace treaty,","Napoleon wanted to celebrate with a rabbit hunt.",
"So his chief of staff rounded up hundreds of rabbits.","The cages opened.","The hunters raised their guns.",
"And the rabbits didn't run away.","They ran straight at Napoleon!","Hundreds of them swarmed his feet and climbed up his legs.",
"His men swung whips and sticks.","Nothing worked.","The great emperor retreated to his carriage...",
"and the rabbits chased him there too.","Why?","They weren't wild rabbits.","They were tame farm rabbits.",
"And when they saw a man walking toward them...","they thought it was dinner time."]
assert len(segs)==len(phr),(len(segs),len(phr))
OVR={"1807":4,"napoleon":4,"europe":3,"emperor":3,"carriage":2,"celebrate":3,"cages":2,"weren't":1,"didn't":2,"time":1,"tame":1,"there":1,"their":1,"raised":1,"swarmed":1,"climbed":1,"opened":2,"whips":1}
def syl(w):
    k=re.sub(r"[^a-z0-9']","",w.lower())
    if k in OVR: return OVR[k]
    n=len(re.findall(r"[aeiouy]+",k))
    if k.endswith("e") and not k.endswith("le") and n>1: n-=1
    return max(1,n)
words=[]
for (a,b),p in zip(segs,phr):
    ws=p.split(); wt=[syl(w)+0.6 for w in ws]; T=sum(wt); x=a
    for w,k in zip(ws,wt):
        d=(b-a)*k/T; words.append([round(x,3),round(x+d,3),w]); x+=d
json.dump([[round(a,2),round(b,2),p] for (a,b),p in zip(segs,phr)],open("work/timing.json","w"),indent=1)
json.dump(words,open("work/words.json","w"),indent=0)
for i,((a,b),p) in enumerate(zip(segs,phr),1): print(f"{i:2d} {a:6.2f}-{b:6.2f} ({b-a:4.2f}s) {p}")
print(len(words),"words")
