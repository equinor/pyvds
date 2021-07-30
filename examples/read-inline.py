import pyvds
import segyio
import time
import os
import sys

from PIL import Image
import numpy as np
from matplotlib import cm

base_path = sys.argv[1]
LINE_IDX = int(sys.argv[2])

if len(sys.argv) != 3:
    raise RuntimeError("This example accepts exactly 2 arguments: input_file & line_idx")

CLIP = 0.2
SCALE = 1.0/(2.0*CLIP)

with pyvds.open(os.path.join(base_path, '0.vds')) as vdsfile:
    t0 = time.time()
    slice_vds = vdsfile.iline[vdsfile.ilines[LINE_IDX]]
    print("pyvds took", time.time() - t0)

im = Image.fromarray(np.uint8(cm.seismic((slice_vds.T.clip(-CLIP, CLIP) + CLIP) * SCALE)*255))
im.save(os.path.join(base_path, 'out_inline-vds.png'))


with segyio.open(os.path.join(base_path, '0.sgy')) as segyfile:
    t0 = time.time()
    slice_segy = segyfile.iline[segyfile.ilines[LINE_IDX]]
    print("segyio took", time.time() - t0)

im = Image.fromarray(np.uint8(cm.seismic((slice_segy.T.clip(-CLIP, CLIP) + CLIP) * SCALE)*255))
im.save(os.path.join(base_path, 'out_inline-sgy.png'))

im = Image.fromarray(np.uint8(cm.seismic(((slice_segy-slice_vds).T.clip(-CLIP, CLIP) + CLIP) * SCALE)*255))
im.save(os.path.join(base_path, 'out_inline-dif.png'))
