from setuptools import setup
# To use a consistent encoding
from codecs import open
from os import path

with open('README.rst') as f:
    long_desc = f.read()

setup(name='glucid',
      version='0.3.1',
      description='Configure the Lucid 8824 AD/DA Audio Interface via \
             a Serial Connection',
      url='http://github.com/danmechanic/glucid',
      author='Daniel R Mechanic',
      author_email='dan.mechanic@gmail.com',
      license='GPL V3',
      zip_safe=False,
      entry_points={  # Optional
          'console_scripts': [
              'glucid=glucid.glucid8824:main',
              'xglucid=glucid.xglucid:main'
          ],
      },
      long_description=long_desc,
      keywords='lucid 8824 audio converter',
      packages=['glucid'],
      python_requires=">=3",
      package_dir={ 'glucidi8824' : 'glucid',
                    'xglucid' : 'glucid',
                    'Glucid8824_UI' : 'glucid',
                    'xglucidUIWidgets' : 'glucid',
      },
      long_description_content_type='text/x-rst',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Topic :: Multimedia :: Sound/Audio :: Conversion',
          'Topic :: Multimedia :: Sound/Audio :: Capture/Recording',
      ],
      project_urls={
          'Author': 'http://www.danmechanic.com/',
          'Source': 'https://github.com/danmechanic/glucid/',
      },
      install_requires=[
          'PyQt5>=5.9',
	  'PySerial',
      ]
      )
