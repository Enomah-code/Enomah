import cv2, numpy as np
from PIL import Image
from rembg import remove, new_session
OUT='/home/user/Enomah/stone-edits-portfolio/02-showcase-lumen/assets/img/'
im=cv2.imread('w_full.jpg').astype(np.float32)/255
X0,Y0,N=0,1000,4000
crop=im[Y0:Y0+N,X0:X0+N]
# matte (computed at 1600 then upscaled)
rgb=cv2.cvtColor((crop*255).astype(np.uint8),cv2.COLOR_BGR2RGB)
cut=remove(Image.fromarray(rgb).resize((1600,1600),Image.LANCZOS),session=new_session('birefnet-general'))
a=np.array(cut.split()[3].resize((N,N),Image.LANCZOS)).astype(np.float32)/255
a=cv2.erode(a,np.ones((5,5),np.uint8))
a=cv2.GaussianBlur(a,(5,5),0)[...,None]
# remove the '3 Sun' date text from the dial (inpaint bright pixels in its box)
box=np.zeros((N,N),np.uint8); cv2.rectangle(box,(1880,1710),(2280,1940),1,-1)
g8=cv2.cvtColor((crop*255).astype(np.uint8),cv2.COLOR_BGR2GRAY)
txt=((g8>60)&(box>0)).astype(np.uint8)*255
txt=cv2.dilate(txt,np.ones((9,9),np.uint8))
crop=cv2.inpaint((crop*255).astype(np.uint8),txt,9,cv2.INPAINT_TELEA).astype(np.float32)/255
cv2.imwrite('dial_check.jpg',(crop[1100:1600,1350:2000]*255).astype(np.uint8))
# background: palette radial gradient x photo luminance ratio (keeps the real contact shadow)
L=cv2.cvtColor(crop,cv2.COLOR_BGR2GRAY)
# rebuild the table luminance under the watch (inpaint at 1/8 scale) so the shadow ratio has no halo
q=8; Ls=cv2.resize(L,(N//q,N//q),interpolation=cv2.INTER_AREA)
ms=cv2.resize((a[...,0]>0.02).astype(np.uint8),(N//q,N//q),interpolation=cv2.INTER_NEAREST)
ms=cv2.dilate(ms,np.ones((9,9),np.uint8))
Lf=cv2.inpaint((Ls*255).astype(np.uint8),ms*255,12,cv2.INPAINT_TELEA).astype(np.float32)/255
Lf=cv2.resize(Lf,(N,N),interpolation=cv2.INTER_CUBIC)
Lsmooth=cv2.GaussianBlur(Lf,(0,0),220)
ratio=np.clip(cv2.GaussianBlur(Lf,(0,0),4)/np.maximum(Lsmooth,1e-3),0.35,1.08)[...,None]
yy,xx=np.mgrid[0:N,0:N].astype(np.float32)
r=np.sqrt(((xx-N*0.5)/(N*0.62))**2+((yy-N*0.42)/(N*0.6))**2)
c0=np.array([238,243,246],np.float32)/255   # BGR of #F6F3EE (centre)
c1=np.array([231,236,239],np.float32)/255   # #EFECE7
c2=np.array([206,215,221],np.float32)/255   # #DDD7CE (edges)
t=np.clip(r,0,1)[...,None]
grad=np.where(t<0.45,c0+(c1-c0)*(t/0.45),c1+(c2-c1)*((t-0.45)/0.55))
bg=np.clip(grad*ratio,0,1)
# watch grade: warm split-tone, slight lift
w=crop.copy()
lum=cv2.cvtColor(w,cv2.COLOR_BGR2GRAY)[...,None]
w=w*np.array([0.93,0.99,1.06])+ (1-lum)*np.array([0.004,0.006,0.012])  # BGR: less blue, more red
w=np.clip((w-0.01)*1.06,0,1)
plate=np.clip(bg*(1-a)+w*a,0,1)
cv2.imwrite(OUT+'lumen-plate.jpg',(plate*255).astype(np.uint8),[cv2.IMWRITE_JPEG_QUALITY,93])
cutout=np.dstack([(w*255).astype(np.uint8),(a[...,0]*255).astype(np.uint8)])
cv2.imwrite(OUT+'lumen-watch.webp',cutout,[cv2.IMWRITE_WEBP_QUALITY,92])
Q=np.load('screen_quad.npy')-[X0,Y0]; np.save('quad02.npy',Q); print('quad in crop',Q.tolist())
cv2.imwrite('plate_view.jpg',cv2.resize((plate*255).astype(np.uint8),(900,900)))
