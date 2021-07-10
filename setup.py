import glob
import os

from setuptools import setup, Extension


# Target Files
BASE_DIR = os.path.dirname(__file__)
LIBGEONLP_DIR = os.path.join(BASE_DIR, 'libgeonlp')
LIBGEONLP_INCLUDE_DIR = os.path.join(LIBGEONLP_DIR, 'include')
LIBGEONLP_SOURCE_DIR = os.path.join(LIBGEONLP_DIR, 'lib')
LIBGEONLP_FILES = glob.glob(os.path.join(LIBGEONLP_SOURCE_DIR, '*.cpp'))
LIBGEONLP_HEADERS = glob.glob(os.path.join(LIBGEONLP_INCLUDE_DIR, '*.h'))
CPYGEONLP_FILES = glob.glob(os.path.join(LIBGEONLP_DIR, '*.cpp'))

# Other Variables
DESCRIPTION = __doc__
LONG_DESCRIPTION = open("README.md", "r", encoding="utf-8").read()
LICENSE = '2-Clause "Simplified" BSD License'
DATA_FILES = glob.glob(os.path.join(BASE_DIR, 'base_data', '*.*'))


def get_libgeonlp():
    """
    Returns the C++ extension `libgeonlp`.
    The logic for auto-detecting the libraries required for
    the extension is based on the following.
    https://stackoverflow.com/questions/28843765/setup-py-check-if-non-python-library-dependency-exists
    """
    from textwrap import dedent
    import tempfile
    import shutil
    import distutils.sysconfig
    import distutils.ccompiler
    from distutils.errors import LinkError

    boost_libs = ['boost_regex', 'boost_system', 'boost_filesystem']

    # Write a temporary .c file to compile
    c_code = dedent("""
    #include <iostream>
    #include <string>
    #include <boost/regex.hpp>

    int main(int argc, char* argv[])
    {
      boost::regex r("air$");
      boost::smatch m;
      std::string pattern = "chair";

      if (boost::regex_search(pattern, m, r)) {
        std::cout << "match." << std::endl;
      } else {
        std::cout << "not match." << std::endl;
      }
      return 0;
    }
    """)

    tmp_dir = tempfile.mkdtemp(prefix='tmp_boost_')
    bin_file_name = os.path.join(tmp_dir, 'test_boost')
    file_name = bin_file_name + '.cpp'
    with open(file_name, 'w') as fp:
        fp.write(c_code)

    # Try compile and link it
    compiler = distutils.ccompiler.new_compiler()
    assert isinstance(compiler, distutils.ccompiler.CCompiler)
    distutils.sysconfig.customize_compiler(compiler)

    compiled = compiler.compile(sources=[file_name],
                                output_dir='test_boost')

    libraries = None
    if not libraries:
        try:
            compiler.link_shared_lib(
                compiled,
                bin_file_name,
                libraries=boost_libs,
            )
        except LinkError:
            pass
        else:
            libraries = boost_libs

    if not libraries:
        boost_mt_libs = [lib + '-mt' for lib in boost_libs]
        try:
            compiler.link_shared_lib(
                compiled,
                bin_file_name,
                libraries=boost_mt_libs,
            )
        except LinkError:
            pass
        else:
            libraries = boost_mt_libs

    shutil.rmtree(tmp_dir)
    shutil.rmtree('test_boost')

    if not libraries:
        raise RuntimeError("Boost libraries is not installed.")

    libgeonlp = Extension(
        'pygeonlp.capi',
        define_macros=[
            ('MAJOR_VERSION', '1'),
            ('MINOR_VERSION', '0'),
            ('REVISION', '1')
        ],
        include_dirs=[LIBGEONLP_INCLUDE_DIR],
        sources=LIBGEONLP_FILES + CPYGEONLP_FILES,
        libraries=['sqlite3', 'mecab'] + libraries,
    )
    return libgeonlp


# Setup tools
setup(
    name='pygeonlp',
    version='1.0.1',
    description='A Python module for geotagging Japanese texts.',
    author='GeoNLP Project Team',
    author_email='geonlp@nii.ac.jp',
    url='https://github.com/geonlp-platform/pygeonlp',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    ext_modules=[get_libgeonlp()],
    packages=['pygeonlp.api', 'pygeonlp.tests'],
    test_suite='pygeonlp.tests',
    python_requires='>=3.6.8',
    install_requires=['requests>=2.21.0', 'chardet>=4.0.0',
                      'lxml>=4.6.2', 'python-dateutil>=2.8.1',
                      'geographiclib>=1.52'],
    data_files=[('pygeonlp_basedata', DATA_FILES)],
    license=LICENSE,
)
