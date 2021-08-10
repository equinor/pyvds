import numpy as np
import openvds
import segyio

class VdsReader:
    def __init__(self, filename):
        self.filename = filename
        self.filehandle = openvds.open(self.filename)
        self.access_manager = openvds.getAccessManager(self.filehandle)
        self.layout = openvds.getLayout(self.filehandle)
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
        """Reads one inline from VDS file

        Parameters
        ----------
        il_no : int
            The inline number

        Returns
        -------
        inline : numpy.ndarray of float32, shape: (n_xlines, n_samples)
            The specified inline, decompressed
        """
        return self.read_inline(self.coord_to_index(il_no, self.ilines))

    def read_inline(self, il_idx):
        """Reads one inline from VDS file

        Parameters
        ----------
        il_id : int
            The ordinal number of the inline in the file

        Returns
        -------
        inline : numpy.ndarray of float32, shape: (n_xlines, n_samples)
            The specified inline, decompressed
        """
        req = self.access_manager.requestVolumeSubset(min=(0, 0, il_idx),
                                                      max=(self.n_samples, self.n_xlines, il_idx+1))
        return req.data.reshape((self.n_xlines, self.n_samples))


    def read_crossline_number(self, xl_no):
        """Reads one crossline from VDS file

        Parameters
        ----------
        xl_no : int
            The crossline number

        Returns
        -------
        crossline : numpy.ndarray of float32, shape: (n_ilines, n_samples)
            The specified crossline, decompressed
        """
        return self.read_crossline(self.coord_to_index(xl_no, self.xlines))

    def read_crossline(self, xl_idx):
        """Reads one crossline from VDS file

        Parameters
        ----------
        xl_id : int
            The ordinal number of the crossline in the file

        Returns
        -------
        crossline : numpy.ndarray of float32, shape: (n_ilines, n_samples)
            The specified crossline, decompressed
        """
        req = self.access_manager.requestVolumeSubset(min=(0, xl_idx, 0),
                                                      max=(self.n_samples, xl_idx+1, self.n_ilines))
        return req.data.reshape((self.n_ilines, self.n_samples))


    def read_zslice_coord(self, samp_no):
        """Reads one zslice from VDS file (time or depth, depending on file contents)

        Parameters
        ----------
        zslice_no : int
            The sample time/depth to return a zslice from

        Returns
        -------
        zslice : numpy.ndarray of float32, shape: (n_ilines, n_xlines)
            The specified zslice (time or depth, depending on file contents), decompressed
        """
        return self.read_zslice(self.coord_to_index(samp_no, self.samples))

    def read_zslice(self, z_idx):
        """Reads one zslice from VDS file (time or depth, depending on file contents)

        Parameters
        ----------
        zslice_id : int
            The ordinal number of the zslice in the file

        Returns
        -------
        zslice : numpy.ndarray of float32, shape: (n_ilines, n_xlines)
            The specified zslice (time or depth, depending on file contents), decompressed
        """
        req = self.access_manager.requestVolumeSubset(min=(z_idx, 0, 0),
                                                      max=(z_idx+1, self.n_xlines, self.n_ilines))
        return req.data.reshape((self.n_ilines, self.n_xlines))


    def read_subvolume(self, min_il, max_il, min_xl, max_xl, min_z, max_z):
        """Reads a sub-volume from VDS file

        Parameters
        ----------
        min_il : int
            The index of the first inline to get from the cube. Use 0 to for the first inline in the cube
        max_il : int
            The index of the last inline to get, non inclusive. To get one inline, use max_il = min_il + 1

        min_xl : int
            The index of the first crossline to get from the cube. Use 0 for the first crossline in the cube
        max_xl : int
            The index of the last crossline to get, non inclusive. To get one crossline, use max_xl = min_xl + 1

        min_z : int
            The index of the first time sample to get from the cube. Use 0 for the first time sample in the cube
        max_z : int
            The index of the last time sample to get, non inclusive. To get one time sample, use max_z = min_z + 1

        access_padding : bool, optional
            Functions which manage voxels used for padding themselves may relax bounds-checking to padded dimensions

        Returns
        -------
        subvolume : numpy.ndarray of float32, shape (max_il - min_il, max_xl - min_xl, max_z - min_z)
            The specified subvolume, decompressed
        """
        req = self.access_manager.requestVolumeSubset(min=(min_z, min_xl, min_il),
                                                      max=(max_z, max_xl, max_il))
        return req.data.reshape((max_il-min_il, max_xl-min_xl, max_z-min_z))

    def read_volume(self):
        """Reads the whole volume from VDS file

        Returns
        -------
        volume : numpy.ndarray of float32, shape (n_ilines, n_xline, n_samples)
            The whole volume, decompressed
        """
        return self.read_subvolume(0, self.n_ilines,
                                   0, self.n_xlines,
                                   0, self.n_samples)


    def get_trace(self, index):
        """Reads one trace from VDS file

        Parameters
        ----------
        index : int
            The ordinal number of the trace in the file

        Returns
        -------
        trace : numpy.ndarray of float32, shape (n_samples)
            A single trace, decompressed
        """
        if not 0 <= index < self.n_ilines * self.n_xlines:
            raise IndexError("Index {} is out of range, total traces is {}".format(index, self.n_ilines * self.n_xlines))

        il, xl = index // self.n_xlines, index % self.n_xlines
        req = self.access_manager.requestVolumeSubset(min=(0, xl, il),
                                                      max=(self.n_samples, xl+1, il+1))
        return req.data


    def gen_trace_header(self, index):
        """Reads one trace header from VDS file

        Parameters
        ----------
        index : int
            The ordinal number of the trace header in the file

        Returns
        -------
        header : dict
            A single header as a dictionary of headerword-value pairs
        """
        if not 0 <= index < self.n_ilines * self.n_xlines:
            raise IndexError(self.range_error.format(index, 0, self.tracecount))

        xl_coord, il_coord = index % self.n_ilines, index // self.n_ilines

        req = self.access_manager.requestVolumeSubset((0,xl_coord,il_coord), (240,xl_coord+1,il_coord+1),
                                                     channel=self.layout.getChannelIndex('SEGYTraceHeader'),
                                                     format=openvds.VolumeDataChannelDescriptor.Format.Format_U8)

        return segyio.segy.Field(req.data.tobytes(), kind='trace')

    def get_file_binary_header(self):
        bin = self.layout.getMetadata("SEGY", "BinaryHeader", openvds.core.MetadataType.BLOB)
        return segyio.segy.Field(bin, kind='binary')

    def get_file_text_header(self):
        txt = self.layout.getMetadata("SEGY", "TextHeader", openvds.core.MetadataType.BLOB)
        return [bytearray(txt.decode("cp037"), encoding="ascii", errors="ignore")]
