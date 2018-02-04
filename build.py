import sys
import os
import shutil
import subprocess

print("Shell needs to have virtualenv")

if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)

if sys.platform == 'darwin':
    localpython = os.path.join('usr','local','bin','python2.7')
    build_dir = os.path.join(application_path, 'Macbuild')
    #if os.path.exists(build_dir):
    #    shutil.rmtree(build_dir) 
    #os.mkdir(build_dir)
    envdir = os.path.join(build_dir, 'virtualenv-pydfs')
    #subprocess.check_call('virtualenv -p {} {}'.format(localpython, envdir).split())
    print(envdir)
    envpip = os.path.join(envdir,'bin','pip')
    print(envpip)
    subprocess.check_call('{} install Cython==0.26.1'.format(envpip).split())
    subprocess.check_call('{} install kivy==1.10.0'.format(envpip).split())
    subprocess.check_call('{} install pyinstaller==3.3.1'.format(envpip).split())
    subprocess.check_call('{} install pyenchant==2.0.0'.format(envpip).split())
    subprocess.check_call('{} install pyobjc==4.1'.format(envpip).split())
    subprocess.check_call('{} install pydfs-lineup-optimizer==1.1.2'.format(envpip).split())

elif sys.platform == 'win32':
    build_dir = os.path.join(application_path, 'Win32build')
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir) 
elif sys.platform == 'win64':
    build_dir = os.path.join(application_path, 'Win64build')
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir) 
