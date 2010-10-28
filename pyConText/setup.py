import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages
setup(name='pyContext',
      version='0.2.5',
      description='Python ConText',
      author='Brian Chapman',
      author_email='chapbe@pitt.edu',
      url='http://www.dbmi.pitt.edu',
      #py_modules = pyn,
      packages=find_packages('src'),
      package_dir={'':'src'},
      #install_requires = ['python>=2.2'],      
     )
