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
                slice_vds = vdsfile.iline[vdsfile.ilines[line_ordinal]]
                assert np.allclose(slice_vds, slice_segy, rtol=tolerance)

def compare_inline_number(vds_filename, sgy_filename, lines_to_test, tolerance):
    with pyvds.open(vds_filename) as vdsfile:
        with segyio.open(sgy_filename) as segyfile:
            for line_number in lines_to_test:
                slice_segy = segyfile.iline[line_number]
                slice_vds = vdsfile.iline[line_number]
                assert np.allclose(slice_vds, slice_segy, rtol=tolerance)

def compare_inline_slicing(vds_filename):
    slices = [slice(1, 5, 2), slice(1, 2, None), slice(1, 3, None), slice(None, 3, None), slice(3, None, None)]
    with pyvds.open(vds_filename) as vdsfile:
        for slice_ in slices:
            slices_slice = np.asarray(vdsfile.iline[slice_])
            start = slice_.start if slice_.start is not None else 1
            stop = slice_.stop if slice_.stop is not None else 6
            step = slice_.step if slice_.step is not None else 1
            slices_concat = np.asarray([vdsfile.iline[i] for i in range(start, stop, step)])
            assert np.array_equal(slices_slice, slices_concat)

def test_inline_accessor():
    compare_inline_ordinal(VDS_FILE, SGY_FILE, [0, 1, 2, 3, 4], tolerance=1e-5)
    compare_inline_number(VDS_FILE, SGY_FILE, [1, 2, 3, 4, 5], tolerance=1e-5)
    compare_inline_slicing(VDS_FILE)


def compare_crossline_ordinal(vds_filename, sgy_filename, lines_to_test, tolerance):
    with pyvds.open(vds_filename) as vdsfile:
        with segyio.open(sgy_filename) as segyfile:
            for line_ordinal in lines_to_test:
                slice_segy = segyfile.xline[segyfile.xlines[line_ordinal]]
                slice_vds = vdsfile.xline[vdsfile.xlines[line_ordinal]]
                assert np.allclose(slice_vds, slice_segy, rtol=tolerance)

def compare_crossline_number(vds_filename, sgy_filename, lines_to_test, tolerance):
    with pyvds.open(vds_filename) as vdsfile:
        with segyio.open(sgy_filename) as segyfile:
            for line_number in lines_to_test:
                slice_segy = segyfile.xline[line_number]
                slice_vds = vdsfile.xline[line_number]
                assert np.allclose(slice_vds, slice_segy, rtol=tolerance)

def compare_crossline_slicing(vds_filename):
    slices = [slice(20, 21, 2), slice(21, 23, 1), slice(None, 22, None), slice(22, None, None)]
    with pyvds.open(vds_filename) as vdsfile:
        for slice_ in slices:
            slices_slice = np.asarray(vdsfile.xline[slice_])
            start = slice_.start if slice_.start is not None else 20
            stop = slice_.stop if slice_.stop is not None else 25
            step = slice_.step if slice_.step is not None else 1
            slices_concat = np.asarray([vdsfile.xline[i] for i in range(start, stop, step)])
            assert np.array_equal(slices_slice, slices_concat)

def test_crossline_accessor():
    compare_crossline_ordinal(VDS_FILE, SGY_FILE, [0, 1, 2, 3, 4], tolerance=1e-5)
    compare_crossline_number(VDS_FILE, SGY_FILE, [20, 21, 22, 23, 24], tolerance=1e-5)
    compare_crossline_slicing(VDS_FILE)


def compare_zslice(vds_filename, tolerance):
    with pyvds.open(vds_filename) as vdsfile:
        with segyio.open(SGY_FILE) as segyfile:
            for line_number in range(50):
                slice_vds = vdsfile.depth_slice[line_number]
                slice_segy = segyfile.depth_slice[line_number]
                assert np.allclose(slice_vds, slice_segy, rtol=tolerance)


def test_zslice_accessor():
    compare_zslice(VDS_FILE, tolerance=1e-5)


def test_trace_accessor():
    with pyvds.open(VDS_FILE) as vdsfile:
        with segyio.open(SGY_FILE) as segyfile:
            for trace_number in range(25):
                vds_trace = vdsfile.trace[trace_number]
                segy_trace = segyfile.trace[trace_number]
                assert np.allclose(vds_trace, segy_trace, rtol=1e-5)

def test_read_bin_header():
    with pyvds.open(VDS_FILE) as vdsfile:
        with segyio.open(SGY_FILE) as segyfile:
            assert vdsfile.bin == segyfile.bin


def test_read_trace_header():
    with pyvds.open(VDS_FILE) as vdsfile:
        with segyio.open(SGY_FILE) as sgyfile:
            for trace_number in range(25):
                sgz_header = vdsfile.header[trace_number]
                sgy_header = sgyfile.header[trace_number]
                assert sgz_header == sgy_header


def test_read_trace_header_slicing():
    slices = [slice(0, 5, None), slice(0, None, 2), slice(5, None, -1), slice(None, None, 10), slice(None, None, None)]
    with pyvds.open(VDS_FILE) as vdsfile:
        with segyio.open(SGY_FILE) as sgyfile:
            for slice_ in slices:
                sgy_headers = sgyfile.header[slice_]
                sgz_headers = vdsfile.header[slice_]
                for sgz_header, sgy_header in zip(sgz_headers, sgy_headers):
                    assert sgz_header == sgy_header


def test_header_is_iterable():
    with pyvds.open(VDS_FILE) as vdsfile:
        with segyio.open(SGY_FILE) as sgy_file:
            for sgz_header, sgy_header in zip(vdsfile.header, sgy_file.header):
                assert sgz_header == sgy_header
