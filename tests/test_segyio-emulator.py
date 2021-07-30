import numpy as np
import segyio
import pyvds

VDS_FILE = 'test_data/small.vds'
SGY_FILE = 'test_data/small.sgy'


def compare_inline_ordinal(vds_filename, sgy_filename, lines_to_test, tolerance):
    with pyvds.open(vds_filename) as vdsfile:
        with segyio.open(sgy_filename) as segyfile:
            for line_ordinal in lines_to_test:
                slice_segy = segyfile.iline[segyfile.ilines[line_ordinal]]
                slice_sgz = vdsfile.iline[vdsfile.ilines[line_ordinal]]
                print(slice_segy)
                print(slice_sgz)
                assert np.allclose(slice_sgz, slice_segy, rtol=tolerance)


def compare_inline_number(vds_filename, sgy_filename, lines_to_test, tolerance):
    with pyvds.open(vds_filename) as vdsfile:
        with segyio.open(sgy_filename) as segyfile:
            for line_number in lines_to_test:
                slice_segy = segyfile.iline[line_number]
                slice_sgz = vdsfile.iline[line_number]
                assert np.allclose(slice_sgz, slice_segy, rtol=tolerance)


def test_inline_accessor():
    compare_inline_ordinal(VDS_FILE, SGY_FILE, [0, 1, 2, 3, 4], tolerance=1e-5)
    compare_inline_number(VDS_FILE, SGY_FILE, [1, 2, 3, 4, 5], tolerance=1e-5)

def compare_crossline_ordinal(vds_filename, sgy_filename, lines_to_test, tolerance):
    with pyvds.open(vds_filename) as vdsfile:
        with segyio.open(sgy_filename) as segyfile:
            for line_ordinal in lines_to_test:
                slice_segy = segyfile.xline[segyfile.xlines[line_ordinal]]
                slice_sgz = vdsfile.xline[vdsfile.xlines[line_ordinal]]
                assert np.allclose(slice_sgz, slice_segy, rtol=tolerance)


def compare_crossline_number(vds_filename, sgy_filename, lines_to_test, tolerance):
    with pyvds.open(vds_filename) as vdsfile:
        with segyio.open(sgy_filename) as segyfile:
            for line_number in lines_to_test:
                slice_segy = segyfile.xline[line_number]
                slice_sgz = vdsfile.xline[line_number]
                assert np.allclose(slice_sgz, slice_segy, rtol=tolerance)


def test_crossline_accessor():
    compare_crossline_ordinal(VDS_FILE, SGY_FILE, [0, 1, 2, 3, 4], tolerance=1e-5)
    compare_crossline_number(VDS_FILE, SGY_FILE, [20, 21, 22, 23, 24], tolerance=1e-5)


def compare_zslice(vds_filename, tolerance):
    with pyvds.open(vds_filename) as vdsfile:
        with segyio.open(SGY_FILE) as segyfile:
            for line_number in range(50):
                slice_sgz = vdsfile.depth_slice[line_number]
                slice_segy = segyfile.depth_slice[line_number]
                assert np.allclose(slice_sgz, slice_segy, rtol=tolerance)


def test_zslice_accessor():
    compare_zslice(VDS_FILE, tolerance=1e-5)
