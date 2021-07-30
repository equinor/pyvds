from collections.abc import Mapping
import numpy as np
import openvds


class VdsReader:
    def __init__(self, filename):
        self.filename = filename
        self.filehandle = openvds.open(self.filename)
        self.access_manager = openvds.getAccessManager(self.filehandle)
        self.n_samples, self.n_xlines, self.n_ilines = self.access_manager.getVolumeDataLayout().numSamples

        il_desc = self.access_manager.getVolumeDataLayout().getAxisDescriptor(2)
        self.ilines = np.arange(int(il_desc.getCoordinateMin()),
                                int(il_desc.getCoordinateMax())+int(il_desc.getCoordinateStep()),
                                int(il_desc.getCoordinateStep()))

        xl_desc = self.access_manager.getVolumeDataLayout().getAxisDescriptor(1)
        self.xlines = np.arange(int(xl_desc.getCoordinateMin()),
                                int(xl_desc.getCoordinateMax())+int(xl_desc.getCoordinateStep()),
                                int(xl_desc.getCoordinateStep()))

        samp_dec = self.access_manager.getVolumeDataLayout().getAxisDescriptor(0)
        self.samples = np.arange(samp_dec.getCoordinateMin(),
                                 samp_dec.getCoordinateMax()+samp_dec.getCoordinateStep(),
                                 samp_dec.getCoordinateStep())


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        openvds.close(self.filehandle)

    @staticmethod
    def coord_to_index(coord, coords, include_stop=False):
        try:
            index = np.where(coords == coord)[0][0]
        except:
            if include_stop and (coord == coords[-1] + (coords[-1] - coords[-2])):
                return len(coords)
            raise IndexError("Coordinate {} not in axis".format(coord))
        return index


    def read_inline_number(self, il_no):
        return self.read_inline(self.coord_to_index(il_no, self.ilines))

    def read_inline(self, il_idx):
        req = self.access_manager.requestVolumeSubset(min=(0, 0, il_idx),
                                                      max=(self.n_samples, self.n_xlines, il_idx+1))
        return req.data.reshape((self.n_xlines, self.n_samples))


    def read_crossline_number(self, xl_no):
        return self.read_crossline(self.coord_to_index(xl_no, self.xlines))

    def read_crossline(self, xl_idx):
        req = self.access_manager.requestVolumeSubset(min=(0, xl_idx, 0),
                                                      max=(self.n_samples, xl_idx+1, self.n_ilines))
        return req.data.reshape((self.n_ilines, self.n_samples))


    def read_zslice_coord(self, samp_no):
        return self.read_zslice(self.coord_to_index(samp_no, self.samples))

    def read_zslice(self, z_idx):
        req = self.access_manager.requestVolumeSubset(min=(z_idx, 0, 0),
                                                      max=(z_idx+1, self.n_xlines, self.n_ilines))
        return req.data.reshape((self.n_ilines, self.n_xlines))


class Accessor(VdsReader):

    def __init__(self, file):
        super(Accessor, self).__init__()

    def __iter__(self):
        return iter(self[:])

    def __len__(self):
        return self.len_object

    def __getitem__(self, subscript):
        if isinstance(subscript, slice):
            start, stop, step = subscript.indices(len(self))
            return [self.values_function(index) for index in range(start, stop, step)]
        else:
            return self.values_function(subscript)

    def __contains__(self, key):
        return key in self.keys_object

    def __hash__(self):
        return hash(self.filename)

    def keys(self):
        return self.keys_object

    def values(self):
        return self[:]

    def items(self):
        return zip(self.keys(), self[:])


class InlineAccessor(Accessor, Mapping):
    def __init__(self, file):
        super(Accessor, self).__init__(file)
        self.len_object = self.n_ilines
        self.keys_object = self.ilines
        self.values_function = self.read_inline_number

class CrosslineAccessor(Accessor, Mapping):
    def __init__(self, file):
        super(Accessor, self).__init__(file)
        self.len_object = self.n_xlines
        self.keys_object = self.xlines
        self.values_function = self.read_crossline_number

class ZsliceAccessor(Accessor, Mapping):
    def __init__(self, file):
        super(Accessor, self).__init__(file)
        self.len_object = self.n_samples
        self.keys_object = self.samples
        self.values_function = self.read_zslice


class SegyioEmulator(VdsReader):
    def __init__(self, filename):
        super(SegyioEmulator, self).__init__(filename)
        self.iline = InlineAccessor(self.filename)
        self.xline = CrosslineAccessor(self.filename)
        self.depth_slice = ZsliceAccessor(self.filename)
