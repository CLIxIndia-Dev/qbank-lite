from distutils.core import setup
import py2exe

setup(console=['main.py'],
      options={
            "py2exe": {
                "packages": ["dlkit", "records"]
            }
      },
      version='0.0.9')
