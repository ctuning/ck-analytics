import ck.kernel as ck

image='use_dnn_to_classify_image.jpg'

r=ck.access({'action':'ask',
             'module_uoa':'advice',
             'to':'classify_image',
             'image':image})
if r['return']>0: ck.err(r)
