import sys, os
#
INTERP = "/home/username/directory/cat/bin/python3"
#INTERP is present twice so that the new Python interpreter knows the actual executable path
if sys.executable != INTERP: os.execl(INTERP, INTERP, *sys.argv)
sys.path.append(os.getcwd())

sys.path.append('cat')
from cat.cat import app as application
