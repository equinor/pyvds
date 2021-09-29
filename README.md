# pyVDS
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![CircleCI](https://circleci.com/gh/equinor/pyvds/tree/master.svg?style=shield)](https://circleci.com/gh/equinor/pyvds/tree/master)
[![PyPi Version](https://img.shields.io/pypi/v/pyvds.svg)](https://pypi.org/project/pyvds/)

Convenience wrapper around Bluware's OpenVDS+ Python bindings which enables 
reading of VDS files with a syntax familiar to users of segyio.

---

### Installation

Requires **openvds** package from Bluware.

**N.B. This is licensed under CC-BY-ND 4.0**

- Wheels from [PyPI](https://pypi.org/project/pyvds/): `pip install pyvds`
- Source from [Github](https://github.com/equinor/pyvds): `git clone https://github.com/equinor/pyvds.git`

---

### Usage

#### Use segyio-like interface to read VDS files ####
```python
import pyvds
with pyvds.open("in.vds")) as vdsfile:
    il_slice = vdsfile.iline[vdsfile.ilines[LINE_IDX]]
    xl_slice = vdsfile.xline[LINE_NUMBER]
    zslice = vdsfile.depth_slice[SLICE_IDX]
    trace = vdsfile.trace[TRACE_IDX]
    trace_header = vdsfile.header[TRACE_IDX]
    text_file_header = vdsfile.text[0]
```

#### Read a VDS file with underlying functions ####
```python
from pyvds.accessors import VdsReader
with VdsReader("in.vds") as reader:
    inline_slice = reader.read_inline_number(LINE_NUMBER)
    crossline_slice = reader.read_crossline(LINE_IDX)
    z_slice = reader.read_zslice_coord(SLICE_COORD)
    sub_vol = reader.read_subvolume(min_il=min_il, max_il=max_il,
                                    min_xl=min_xl, max_xl=max_xl,
                                    min_z=min_z, max_z=max_z)
```

---

### Creating VDS files

Example of creating wavelet compressed VDS file from SEG-Y:
```
.\SEGYImport.exe --vdsfile <output_file> --compression-method wavelet --tolerance 1 <input_file>
```
SEGYImport may be obtained from [Bluware's OpenVDSPlus distribution](https://bluware.jfrog.io/native/Releases-OpenVDSPlus/2.1)