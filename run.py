import os
import subprocess

os.environ['FLASK_APP'] = 'urlshort'
os.environ['FLASK_ENV'] = 'development'
subprocess.check_call(['flask', 'run'], shell=True)