import numpy as np, subprocess, wave, sys
SR=44100
def load(f,ch=2):
    a=np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',f,'-ac',str(ch),'-ar',str(SR),'-f','f32le','-'],capture_output=True).stdout,dtype=np.float32).reshape(-1,ch).astype(np.float64)
    return a
v=load(sys.argv[1]); m=load(sys.argv[2]); s=load(sys.argv[3])
n=max(len(v),len(m),len(s))
pad=lambda x: np.vstack([x,np.zeros((n-len(x),2))])
v,m,s=pad(v),pad(m),pad(s)
def grms(x):
    mid=x.mean(1); w=int(.05*SR); r=np.sqrt(np.array([ (mid[i:i+w]**2).mean() for i in range(0,len(mid)-w,w)]))
    db=20*np.log10(r+1e-12); g=r[db>db.max()-40]; return np.sqrt((g**2).mean())
import os
SR_=float(os.environ.get('SFXR','0.5'))
rv=grms(v); m*=0.56*rv/grms(m); s*=SR_*rv/grms(s)
env=np.abs(v.mean(1)); w=int(0.15*SR); env=np.convolve(env,np.ones(w)/w,'same'); on=(env>env.max()*0.04).astype(float)
on=np.convolve(on,np.ones(int(0.25*SR))/int(0.25*SR),'same'); m*=(1-0.3*np.clip(on,0,1))[:,None]
vp=np.abs(v.mean(1)).max(); sp=np.abs(s.mean(1)).max()
cap=float(os.environ.get('SFXCAP','0.7'))
if sp>cap*vp: s*=cap*vp/sp
print('music vs voice dB %.1f'%(20*np.log10(grms(m)/rv)),' sfx vs voice dB %.1f'%(20*np.log10(grms(s)/rv)))
out=v+m+s
w=wave.open('mix_raw.wav','wb');w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR)
out=out/max(1,np.abs(out).max()/0.99)
w.writeframes((out*32767).astype(np.int16).tobytes());w.close()
