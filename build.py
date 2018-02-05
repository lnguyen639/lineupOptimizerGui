import sys
import os
import shutil
import subprocess
import fileinput
import argparse

if sys.platform == 'darwin':
    buildos = 'mac'
elif sys.platform == 'win32':
    buildos = 'win32'
elif sys.platform == 'win64':
    buildos = 'win64'

p = argparse.ArgumentParser()
p.add_argument('--setup', action='store_true', default=False)
args = p.parse_args()

print("Shell needs to have virtualenv")

if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
    abspath = os.path.abspath(application_path)
elif __file__:
    application_path = os.path.dirname(__file__)
    abspath = os.path.abspath(application_path)

def get_localpython(buildos):
    if buildos == 'mac':
        localpython = os.path.join('/usr','local','bin','python2.7')
    else:
        localpython = os.path.join('C:','Python27','python.exe')
    return localpython

def get_builddir(buildos):
    return os.path.join(abspath, '{}build'.format(buildos))

def setup_pyenv(buildos):
    if buildos == 'mac':
        subprocess.check_call('virtualenv -p {} {}'.format(localpython, envdir).split())
        subprocess.check_call('{} install Cython==0.26.1'.format(envpip).split())
        subprocess.check_call('{} install kivy==1.10.0'.format(envpip).split())
        subprocess.check_call('{} install pyinstaller==3.3.1'.format(envpip).split())
        subprocess.check_call('{} install pyobjc==4.1'.format(envpip).split())
        subprocess.check_call('{} install pydfs-lineup-optimizer==1.1.2'.format(envpip).split())
    else:
        pass

localpython = get_localpython(buildos)
srcpath = os.path.join(abspath, 'src')                  #cwd/src
lineupmainpy = os.path.join(srcpath ,'lineupmain.py')
builddir = get_builddir(buildos)                        #cwd/[mac/win]build
envdir = os.path.join(builddir, 'virtualenv-pydfs')     #cwd/[mac/win]build/virtualenv-pydfs
envpip = os.path.join(envdir,'bin','pip')               
envpython = os.path.join(envdir,'bin','python')
pkgdir = os.path.join(builddir, 'package')               #cwd/[mac/win]build/package
appname = 'lineupOptGuiPkg'
specfile = os.path.join(pkgdir,'{}.spec'.format(appname))

if args.setup:
    if os.path.exists(builddir):
        shutil.rmtree(builddir) 
    os.mkdir(builddir)

    setup_pyenv(buildos)

    #Replace lineup_optimizer.py with modified version of it
    lineup_optimizer_py = os.path.join(envdir,'lib','python2.7','site-packages','pydfs_lineup_optimizer','lineup_optimizer.py')
    newlineup_optimizer_py = os.path.join(srcpath,'lineup_optimizer.py')
    os.remove(lineup_optimizer_py)
    shutil.copyfile(newlineup_optimizer_py, lineup_optimizer_py)

    #Build pkgdir with dist, build, and .spec file
    if os.path.exists(pkgdir):
        shutil.rmtree(pkgdir) 
    os.mkdir(pkgdir)
    print(pkgdir)
    cmd = '{} -m PyInstaller -y --clean --windowed --name {} --exclude-module _tkinter --exclude-module Tkinter --exclude-module enchant   --exclude-module twisted {}'.format(envpython, appname, lineupmainpy)
    print(cmd)
    subprocess.check_call(cmd.split(), cwd=pkgdir)
    #Add Tree() command in COLLECT() statement in .spec file
    for line in fileinput.input(specfile, inplace=True):
        print(line.replace('COLLECT(exe,','COLLECT(exe,Tree("{}"),'.format(srcpath))),

#Rebuild .spec and binaries
subprocess.check_call('{} -m PyInstaller -y --clean --windowed {}'.format(envpython, specfile).split(), cwd=pkgdir)
