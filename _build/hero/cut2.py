from PIL import Image, ImageFilter
import numpy as np
from scipy import ndimage as nd
R='/var/www/m2.michael-kuhlman.com/_build/renders/'
for f in ['TS-SIG-RAW_1','TS-KLC16-VOLT_1','TS-APX14_1','TS-T40-3_1','TS-KLC16-CORAL_1','TS-KLC16-GLACIER_1','TS-DZC16_1','TS-HYB13_1']:
    src=Image.open(R+f+'.png').convert('RGB'); im=np.asarray(src).astype(float); h,w,_=im.shape
    L=np.median(im[:,:40],axis=1); Rr=np.median(im[:,-40:],axis=1); t=np.linspace(0,1,w)[None,:,None]
    bg=L[:,None,:]*(1-t)+Rr[:,None,:]*t
    d=np.sqrt(((im-bg)**2).sum(2))
    lum=im.mean(2); blum=bg.mean(2)
    nim=im/np.maximum(lum[...,None],1); nbg=bg/np.maximum(blum[...,None],1)
    chroma=np.sqrt(((nim-nbg)**2).sum(2))*100
    cream=(lum>150)&(chroma<16)
    hard=((d>60)|(chroma>12))&~cream
    hard=nd.binary_opening(hard,iterations=1)
    hard=nd.binary_fill_holes(hard)
    lab,n=nd.label(hard); sizes=nd.sum(hard,lab,range(1,n+1))
    keep=np.isin(lab,[i+1 for i,s in enumerate(sizes) if s>800])
    a=Image.fromarray((keep*255).astype('uint8')).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.1))
    o=src.convert('RGBA'); o.putalpha(a); o=o.crop(o.getbbox()); o.save(f'cut/{f}.png'); print(f,o.size)
