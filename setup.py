# -*- coding: utf-8 -*-

from pip.req import parse_requirements
from pip.download import PipSession
from setuptools import setup, find_packages

install_reqs = parse_requirements("requirements.txt", session=PipSession())
requires = [str(ir.req) for ir in install_reqs if ir.req is not None]

setup(name='wktprojectionservice',
      version='1.0.1',
      description='A SDShare push receiver that projects WKT coordinates from one system to another',
      author='Petr Vasilev',
      author_email='petr.vasilev@sesam.io',
      url='http://sesam.io',
      packages=find_packages(),
      include_package_data=True,
      install_requires=requires,
      setup_requires=['pip'],
      tests_require=requires,
      test_suite = 'nose.collector',
      license = "Proprietary",
      # Some packages don't deal well with binary eggs...
      zip_safe=False,
      keywords = "sdshare rest wkt receiver http post",
      classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows"
        "Operating System :: POSIX",
        "Topic :: Utilities",
        "Topic :: Text Processing :: Markup :: XML",
        "Programming Language :: Python",
        "License :: Other/Proprietary License",
      ],
      entry_points={
          'console_scripts': [
              'wktprojectionservice=wktprojectionservice.receiver:main',
          ],
      })
