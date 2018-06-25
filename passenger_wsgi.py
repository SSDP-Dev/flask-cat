import sys, os
#
INTERP = "/home/username/directory/cat/venv/bin/python3"
#INTERP is present twice so that the new Python interpreter knows the actual executable path
if sys.executable != INTERP: os.execl(INTERP, INTERP, *sys.argv)
sys.path.append(os.getcwd())

sys.path.append('cat')
#from cat import app as application
import cat

application = cat.create_app()
