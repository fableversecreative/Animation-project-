import sys,glob,cv2,numpy as np
fs=sorted(glob.glob(sys.argv[1]+'/*.jpg'));ims=[cv2.imread(f) for f in fs]
h,w=ims[0].shape[:2];cols=int(sys.argv[3]) if len(sys.argv)>3 else 6
rows=(len(ims)+cols-1)//cols;sheet=np.full((rows*(h+24),cols*w,3),30,np.uint8)
for i,(f,im) in enumerate(zip(fs,ims)):
    r,c=divmod(i,cols);sheet[r*(h+24)+24:r*(h+24)+24+h,c*w:(c+1)*w]=im
    cv2.putText(sheet,f.split('_')[-1][:-4],(c*w+4,r*(h+24)+18),cv2.FONT_HERSHEY_SIMPLEX,0.55,(255,255,255),1)
cv2.imwrite(sys.argv[2],sheet)
