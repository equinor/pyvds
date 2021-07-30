import numpy as np
import segyio
from pyvds.accessors import VdsReader

VDS_FILE = 'test_data/small.vds'
SGY_FILE = 'test_data/small.sgy'

def test_read_ilines_list():
    reader = VdsReader(VDS_FILE)
    with segyio.open(SGY_FILE) as sgyfile:
        assert np.all(reader.ilines == sgyfile.ilines)


def test_read_xlines_list():
    reader = VdsReader(VDS_FILE)
    with segyio.open(SGY_FILE) as sgyfile:
        assert np.all(reader.xlines == sgyfile.xlines)


def test_read_samples_list():
    reader = VdsReader(VDS_FILE)
    with segyio.open(SGY_FILE) as sgyfile:
        assert np.all(reader.samples == sgyfile.samples)


def test_read_ilines_datatype():
    reader = VdsReader(VDS_FILE)
    with segyio.open(SGY_FILE) as sgyfile:
        assert reader.ilines.dtype == sgyfile.ilines.dtype


def test_read_xlines_datatype():
    reader = VdsReader(VDS_FILE)
    with segyio.open(SGY_FILE) as sgyfile:
        assert reader.xlines.dtype == sgyfile.xlines.dtype


def test_read_samples_datatype():
    reader = VdsReader(VDS_FILE)
    with segyio.open(SGY_FILE) as sgyfile:
        assert reader.samples.dtype == sgyfile.samples.dtype


def compare_inline(vds_filename, sgy_filename, lines, tolerance):
    with segyio.open(sgy_filename) as segyfile:
        reader = VdsReader(vds_filename)
        for line_number in range(lines):
            slice_vds = reader.read_inline(line_number)
            slice_segy = segyfile.iline[segyfile.ilines[line_number]]
        assert np.allclose(slice_vds, slice_segy, rtol=tolerance)


def compare_inline_number(vds_filename, sgy_filename, line_coords, tolerance):
    with segyio.open(sgy_filename) as segyfile:
        reader = VdsReader(vds_filename)
        for line_number in line_coords:
            slice_vds = reader.read_inline_number(line_number)
            slice_segy = segyfile.iline[line_number]
        assert np.allclose(slice_vds, slice_segy, rtol=tolerance)


def test_read_inline():
    compare_inline(VDS_FILE, SGY_FILE, 5, tolerance=1e-5)
    compare_inline_number(VDS_FILE, SGY_FILE, [1, 2, 3, 4, 5], tolerance=1e-5)


def compare_crossline(vds_filename, sgy_filename, lines, tolerance):
    with segyio.open(sgy_filename) as segyfile:
        reader = VdsReader(vds_filename)
        for line_number in range(lines):
            slice_vds = reader.read_crossline(line_number)
            slice_segy = segyfile.xline[segyfile.xlines[line_number]]
        assert np.allclose(slice_vds, slice_segy, rtol=tolerance)


def compare_crossline_number(vds_filename, sgy_filename, line_coords, tolerance):
    with segyio.open(sgy_filename) as segyfile:
        reader = VdsReader(vds_filename)
        for line_number in line_coords:
            slice_vds = reader.read_crossline_number(line_number)
            slice_segy = segyfile.xline[line_number]
        assert np.allclose(slice_vds, slice_segy, rtol=tolerance)


def test_read_crossline():
    compare_crossline(VDS_FILE, SGY_FILE, 5, tolerance=1e-5)
    compare_crossline_number(VDS_FILE, SGY_FILE, [20, 21, 22, 23, 24], tolerance=1e-5)


def compare_zslice(vds_filename, tolerance):
    with segyio.open(SGY_FILE) as segyfile:
        reader = VdsReader(vds_filename)
        for line_number in range(50):
            slice_vds = reader.read_zslice(line_number)
            slice_segy = segyfile.depth_slice[line_number]
            assert np.allclose(slice_vds, slice_segy, rtol=tolerance)

def compare_zslice_coord(vds_filename, tolerance):
    with segyio.open(SGY_FILE) as segyfile:
        reader = VdsReader(vds_filename)
        for slice_coord, slice_index in zip(range(0, 200, 4), range(50)):
            slice_vds = reader.read_zslice_coord(slice_coord)
            slice_segy = segyfile.depth_slice[slice_index]
            assert np.allclose(slice_vds, slice_segy, rtol=tolerance)

def test_read_zslice():
    compare_zslice(VDS_FILE, tolerance=1e-5)
    compare_zslice_coord(VDS_FILE, tolerance=1e-5)


def compare_subvolume(vds_filename, tolerance):
    min_il, max_il = 2,  3
    min_xl, max_xl = 1,  2
    min_z,  max_z = 10, 20
    vol_vds = VdsReader(vds_filename).read_subvolume(min_il=min_il, max_il=max_il,
                                                     min_xl=min_xl, max_xl=max_xl,
                                                     min_z=min_z, max_z=max_z)
    vol_segy = segyio.tools.cube(SGY_FILE)[min_il:max_il, min_xl:max_xl, min_z:max_z]
    assert np.allclose(vol_vds, vol_segy, rtol=tolerance)

def test_read_subvolume():
    compare_subvolume(VDS_FILE, tolerance=1e-5)
