"""
from distutils.core import setup
import py2exe,sys

#enterFile=sys.argv[2]
#print "enterFile:",enterFile
#sys.exit(0)
setup(console=['main.py'])
"""
from distutils.core import setup
import py2exe
setup(windows=["main.py"],options = { "py2exe":{"dll_excludes":["MSVCP90.dll"]}})

 