from PIL import Image
import numpy as np
from scipy import ndimage as nd
for f in ['TS-SIG-RAW_1','TS-KLC16-VOLT_1','TS-APX14_1','TS-KLC16-CORAL_1','TS-KLC16-GLACIER_1','TS-DZC16_1','TS-HYB13_1']:
    im=Image.open(f'cut/{f}.png'); a=np.asarray(im)[...,3]>40
    lab,n=nd.label(a); sizes=nd.sum(a,lab,range(1,n+1)); order=np.argsort(sizes)[::-1]
    for name,idx in [('paddle',order[0]),('ball',order[1] if n>1 else None)]:
        if idx is None: continue
        m=nd.binary_dilation(lab==idx+1,iterations=3)
        arr=np.asarray(im).copy(); arr[...,3]=np.where(m,arr[...,3],0)
        o=Image.fromarray(arr,'RGBA'); o=o.crop(o.getbbox()); o.save(f'cut/{f}_{name}.png'); print(f,name,o.size)
