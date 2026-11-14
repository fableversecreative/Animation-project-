import numpy as np, wave, math, random
SR=44100; DUR=44.6; N=int(SR*DUR)
rnd=np.random.default_rng(7)
def tt(d): return np.arange(int(SR*d))/SR
def env(n,a=0.005,r=0.1):
    e=np.ones(n); na=max(1,int(a*SR)); nr=max(1,int(r*SR))
    e[:na]=np.linspace(0,1,na); e[-nr:]*=np.linspace(1,0,nr); return e
def lp(x,k):
    k=max(1,int(k)); return np.convolve(x,np.ones(k)/k,'same')
def place(buf,x,t,g=1.0,pan=0.0):
    i=int(t*SR); 
    if i>=len(buf): return
    x=x[:len(buf)-i]
    l=g*math.cos((pan+1)*math.pi/4); r=g*math.sin((pan+1)*math.pi/4)
    buf[i:i+len(x),0]+=x*l*1.41; buf[i:i+len(x),1]+=x*r*1.41
noise=lambda d: rnd.standard_normal(int(SR*d))
def whoosh(d=0.5,up=True):
    n=noise(d); t=tt(d); e=np.sin(np.pi*t/d)**2
    out=np.zeros_like(n); 
    for k,w in ((3,0.5),(9,0.3),(30,0.2)): out+=lp(n,k)*w
    return out*e*0.6
def riser(d=0.6):
    t=tt(d); return (lp(noise(d),4)*0.4+0.2*np.sin(2*np.pi*(300+900*t/d)*t))*(t/d)**2
def impact(d=0.9,f=55):
    t=tt(d); sub=np.sin(2*np.pi*(f*np.exp(-t*3))*t*2)*np.exp(-t*5)
    click=noise(d)*np.exp(-t*80)*0.6; crunch=lp(noise(d),3)*np.exp(-t*14)*0.4
    return sub+click+crunch
def pop(f=600):
    t=tt(0.12); return np.sin(2*np.pi*f*t*(1+3*np.exp(-t*40)))*np.exp(-t*35)
def boing():
    t=tt(0.5); return np.sin(2*np.pi*(180+120*np.sin(2*np.pi*9*t))*t)*np.exp(-t*6)*0.8
def ting(f=1800):
    t=tt(1.0); x=sum(np.sin(2*np.pi*f*m*t+ 2*np.sin(2*np.pi*f*1.4*t)*np.exp(-t*6))*a for m,a in ((1,1),(2.01,0.4),(3.03,0.2)))
    return x*np.exp(-t*5)*0.5
def tick(): t=tt(0.03); return np.sin(2*np.pi*2400*t)*np.exp(-t*200)*0.6
def thunk(): t=tt(0.25); return (np.sin(2*np.pi*110*t)*np.exp(-t*25)+lp(noise(0.25),6)*np.exp(-t*30)*0.6)
def clang():
    t=tt(0.9); x=sum(np.sin(2*np.pi*f*t)*a for f,a in ((523,1),(1187,.6),(1789,.5),(2650,.3)))
    return (x*np.exp(-t*6)*0.5+noise(0.9)*np.exp(-t*60)*0.5)
def crash():
    t=tt(1.0); x=lp(noise(1.0),2)*np.exp(-t*5)
    for k in range(6): 
        i=int(rnd.uniform(0,0.4)*SR); x[i:i+3000]+=thunk()[:3000][:len(x[i:i+3000])]*0.8
    return x
def chomp(): t=tt(0.15); return lp(noise(0.15),5)*np.exp(-t*30)*np.sin(np.pi*t/0.15)
def scratch():
    t=tt(0.6); f=600+500*np.sin(2*np.pi*3*t); return (np.sin(2*np.pi*np.cumsum(f)/SR)*0.3+lp(noise(0.6),2)*0.5)*np.exp(-t*3)
def click(): t=tt(0.08); return noise(0.08)*np.exp(-t*120)+np.sin(2*np.pi*3000*t)*np.exp(-t*90)*0.5
def puff(): t=tt(0.6); return lp(noise(0.6),20)*np.exp(-t*6)*1.5
def rumble(d):
    t=tt(d); x=lp(noise(d),60)*3; 
    steps=np.zeros_like(t)
    for k in np.arange(0,d-0.06,0.07): 
        i=int((k+rnd.uniform(0,0.03))*SR); steps[i:i+800]+=np.exp(-np.arange(800)/120)*rnd.uniform(0.3,1)
    return (x*0.6+lp(steps,8)*1.5)*np.minimum(1,np.minimum(t/0.3,(d-t)/0.4))
def engine(d,f=38):
    t=tt(d); x=np.sign(np.sin(2*np.pi*f*t+0.3*np.sin(2*np.pi*7*t)))*0.3; return lp(x,10)*np.minimum(1,np.minimum(t/0.2,(d-t)/0.5))
def strain(): t=tt(0.7); return lp(noise(0.7),3)*np.sin(np.pi*t/0.7)*0.4
def ring():
    t=tt(0.8); x=np.sin(2*np.pi*1100*t)*(0.5+0.5*np.sign(np.sin(2*np.pi*20*t))); return x*0.4*np.minimum(1,(0.8-t)*8)
def chalk(): t=tt(0.12); return lp(noise(0.12),2)*np.sin(np.pi*t/0.12)*0.5
def cheer(d=1.6):
    t=tt(d); x=np.zeros_like(t)
    for k in range(10):
        f=rnd.uniform(500,900); x+=np.sin(2*np.pi*f*t*(1+0.05*np.sin(2*np.pi*rnd.uniform(5,9)*t)))*rnd.uniform(.2,.5)
    return x*np.minimum(1,np.minimum(t/0.1,(d-t)/0.6))*0.25
def splash(): t=tt(0.4); return lp(noise(0.4),2)*np.exp(-t*10)*0.6

