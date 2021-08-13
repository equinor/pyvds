from pyvds.read import VdsReader

def cube(filename):
    with VdsReader(filename) as reader:
        return reader.read_volume()
