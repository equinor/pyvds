import setuptools

setuptools.setup(name='pyvds',
                 author='equinor',
                 description='Convenience wrapper around OpenVDS+ Python bindings',
                 long_description='Convenience wrapper around OpenVDS+ Python bindings which enables reading VDS files with a syntax familiar to users of segyio.',
                 url='https://github.com/equinor/pyvds',

                 version='0.0.0',
                 install_requires=['openvds'],
                 setup_requires=['setuptools'],
                 packages=['pyvds']
                 )
