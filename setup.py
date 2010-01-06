#!/usr/bin/env python

from setuptools import setup, find_packages, Extension

import numpy

numpy_include = numpy.get_include()
ex1 = Extension('numina.image._combine',
                ['src/combinemodule.cc', 
                 'src/methods.cc',
                 'src/methods_python.cc',  
                 'src/method_factory.cc',
                 ],
          include_dirs=[numpy_include])

setup(name='pyemir',
      version='0.0.2',
      author='Sergio Pascual',
      author_email='sergiopr@astrax.fis.ucm.es',
      url='http://guaix.fis.ucm.es/projects/emir',
      license='GPLv3',
      description='EMIR Data Processing Pipeline',
      long_description='EMIR Data Processing Pipeline',
      packages=find_packages('lib'),
      package_dir={'': 'lib'},
      package_data={'emir.simulation': ['*.dat'],
                      'numina': ['*.cfg', 'logging.ini']},
      ext_modules=[ex1],
      requires=['pyfits', 'scipy', 'sphinx', 'nose'],
      entry_points={
                      'console_scripts': ['numina = numina.user:main'],
                      },
      test_suite="nose.collector",
      )
