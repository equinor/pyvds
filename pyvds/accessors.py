from collections.abc import Mapping

from .read import VdsReader

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


class SliceAccessor(Accessor):
    def __getitem__(self, subscript):
        if isinstance(subscript, slice):
            # Acquiris Quodcumquae Rapis
            start, stop, step = subscript.start, subscript.stop, subscript.step
            if step is None:
                step = int(self.keys_object[1] - self.keys_object[0])
            if start is None:
                start = int(self.keys_object[0])
            if stop is None:
                stop = int(self.keys_object[-1] + 1)
            return [self.values_function(index) for index in range(start, stop, step)]
        else:
            return self.values_function(subscript)


class InlineAccessor(SliceAccessor, Mapping):
    def __init__(self, file):
        super(Accessor, self).__init__(file)
        self.len_object = self.n_ilines
        self.keys_object = self.ilines
        self.values_function = self.read_inline_number

class CrosslineAccessor(SliceAccessor, Mapping):
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

class TraceAccessor(Accessor, Mapping):
    def __init__(self, file):
        super(Accessor, self).__init__(file)
        self.len_object = self.tracecount
        self.keys_object = list(range(self.tracecount))
        self.values_function = self.get_trace


class SegyioEmulator(VdsReader):
    def __init__(self, filename):
        super(SegyioEmulator, self).__init__(filename)
        self.iline = InlineAccessor(self.filename)
        self.xline = CrosslineAccessor(self.filename)
        self.depth_slice = ZsliceAccessor(self.filename)
        self.trace = TraceAccessor(self.filename)
        self.text = self.get_file_text_header()
