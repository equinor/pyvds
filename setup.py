import setuptools

setuptools.setup(name='pyvds',
                 author='equinor',
                 description='Convenience wrapper around OpenVDS+ Python bindings',
                 long_description='Convenience wrapper around OpenVDS+ Python bindings which enables reading VDS files with a syntax familiar to users of segyio.',
                 url='https://github.com/equinor/pyvds',

                 use_scm_version=True,
                 install_requires=['openvds'],
                 dependency_links = ['https://bluware.jfrog.io/artifactory/Releases-OpenVDSPlus/2.1/python'],
                 setup_requires=['setuptools', 'setuptools_scm'],
                 packages=['pyvds']
                 )
