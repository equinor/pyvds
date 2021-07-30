import numpy as np
import openvds

class VdsReader:
    def __init__(self, filename):
        self.filename = filename
        self.filehandle = openvds.open(self.filename)
        self.access_manager = openvds.getAccessManager(self.filehandle)
        self.n_samples, self.n_xlines, self.n_ilines = self.access_manager.getVolumeDataLayout().numSamples
        self.tracecount = self.n_xlines * self.n_ilines

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


    def read_subvolume(self, min_il, max_il, min_xl, max_xl, min_z, max_z):
        req = self.access_manager.requestVolumeSubset(min=(min_z, min_xl, min_il),
                                                      max=(max_z, max_xl, max_il))
        return req.data.reshape((max_il-min_il, max_xl-min_xl, max_z-min_z))


    def get_trace(self, index):
        if not 0 <= index < self.n_ilines * self.n_xlines:
            raise IndexError("Index {} is out of range, total traces is {}".format(index, self.n_ilines * self.n_xlines))

        il, xl = index // self.n_xlines, index % self.n_xlines
        req = self.access_manager.requestVolumeSubset(min=(0, xl, il),
                                                      max=(self.n_samples, xl+1, il+1))
        return req.data

    def get_file_text_header(self):
        layout = openvds.getLayout(self.filehandle)
        bin = layout.getMetadata("SEGY", "TextHeader", openvds.core.MetadataType.BLOB)
        return [bytearray(bin.decode("cp037"), encoding="ascii", errors="ignore")]
