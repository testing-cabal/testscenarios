#!/usr/bin/env python

from distutils.core import setup

setup(name="testscenarios",
      version="0.1",
      description="Testscenarios, a pyunit extension for dependency injection",
      maintainer="Robert Collins",
      maintainer_email="robertc@robertcollins.net",
      url="https://launchpad.net/testscenarios",
      packages=['testscenarios', 'testscenarios.tests'],
      package_dir = {'':'lib'}
      )
