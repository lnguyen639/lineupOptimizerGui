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
        return os.path.join('/usr','local','bin','python2.7')
    else:
        return os.path.join('C:\\','Python27','python.exe')

def get_builddir(buildos):
    return os.path.join(abspath, '{}build'.format(buildos))

def get_envpip(buildos):
    if buildos == 'mac':
        return os.path.join(envdir,'bin','pip')               
    else:
        return os.path.join(envdir,'Scripts','pip.exe')

def get_envpython(buildos):
    if buildos == 'mac':
        return os.path.join(envdir,'bin','python')
    else:
        return os.path.join(envdir,'Scripts','python.exe')

def get_lineup_optimizer_py(buildos):
    if buildos == 'mac':
        return os.path.join(envdir,'lib','python2.7','site-packages','pydfs_lineup_optimizer','lineup_optimizer.py')
    else:
        return os.path.join(envdir,'lib','site-packages','pydfs_lineup_optimizer','lineup_optimizer.py')

def setup_pyenv(buildos):
    subprocess.check_call('virtualenv -p {} {}'.format(localpython, envdir).split())
    if buildos == 'mac':
        subprocess.check_call('{} install Cython==0.26.1'.format(envpip).split())
        subprocess.check_call('{} install pyobjc==4.1'.format(envpip).split())
    else:
        subprocess.check_call('{} install --upgrade pip wheel setuptools'.format(envpip).split())
        subprocess.check_call('{} install docutils==0.14'.format(envpip).split())
        subprocess.check_call('{} install Pygments==2.2.0'.format(envpip).split())
        subprocess.check_call('{} install pypiwin32==219'.format(envpip).split())
        subprocess.check_call('{} install kivy.deps.sdl2==0.1.17'.format(envpip).split())
        subprocess.check_call('{} install kivy.deps.glew==0.1.9'.format(envpip).split())
        subprocess.check_call('{} install kivy.deps.gstreamer==0.1.12'.format(envpip).split())
    subprocess.check_call('{} install kivy==1.10.0'.format(envpip).split())
    subprocess.check_call('{} install pyinstaller==3.3.1'.format(envpip).split())
    subprocess.check_call('{} install pydfs-lineup-optimizer==1.1.2'.format(envpip).split())

localpython = get_localpython(buildos)
srcpath = os.path.join(abspath, 'src')                  #cwd/src
lineupmainpy = os.path.join(srcpath ,'lineupmain.py')
builddir = get_builddir(buildos)                        #cwd/[mac/win]build
envdir = os.path.join(builddir, 'virtualenv-pydfs')     #cwd/[mac/win]build/virtualenv-pydfs
envpip = get_envpip(buildos)
envpython = get_envpython(buildos)
pkgdir = os.path.join(builddir, 'package')               #cwd/[mac/win]build/package
appname = 'lineupOptGuiPkg'
specfile = os.path.join(pkgdir,'{}.spec'.format(appname))
lineup_optimizer_py = get_lineup_optimizer_py(buildos)

def get_build_cmd(buildos):
    if buildos == 'mac':
        return '{} -m PyInstaller -y --clean --windowed --name {} --exclude-module _tkinter --exclude-module Tkinter --exclude-module enchant   --exclude-module twisted {}'.format(envpython, appname, lineupmainpy)
    else:
        return '{} -m PyInstaller --name {} {}'.format(envpython, appname, lineupmainpy)

def fix_spec_file(buildos):
    if buildos == 'mac':
        collect_line = 'COLLECT(exe,Tree(\'{}\'),'.format(srcpath)
    else:
        # Insert import for windows
        f = open(specfile, "r")
        contents = f.readlines()
        f.close()
        
        line='from kivy.deps import sdl2, glew\n'
        contents.insert(1, line)
        
        f = open(specfile, "w")
        contents = "".join(contents)
        f.write(contents)
        f.close()

        collect_line = 'a.datas, \n*[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],'
        for line in fileinput.input(specfile, inplace=True):
            print(line.replace('a.datas,',collect_line)), #comma at the end for print not to print new line

        #Fix path issue in windows, for .spec file
        srcpathreplace = srcpath.replace('\\','\\\\')
        print(srcpath)
        print(srcpathreplace)
        collect_line = 'COLLECT(exe,Tree(\'{}\'),'.format(srcpathreplace)

    #Add Tree() command in COLLECT() statement in .spec file
    for line in fileinput.input(specfile, inplace=True):
        print(line.replace('COLLECT(exe,',collect_line)), #comma at the end for print not to print new line

if args.setup:
    if os.path.exists(builddir):
        shutil.rmtree(builddir) 
    os.mkdir(builddir)

    setup_pyenv(buildos)

    #Replace lineup_optimizer.py with modified version of it
    newlineup_optimizer_py = os.path.join(srcpath,'lineup_optimizer.py')
    os.remove(lineup_optimizer_py)
    shutil.copyfile(newlineup_optimizer_py, lineup_optimizer_py)

if not args.setup:
    #Build pkgdir with dist, build, and .spec file
    if os.path.exists(pkgdir):
        shutil.rmtree(pkgdir) 
    os.mkdir(pkgdir)
    print(pkgdir)
    cmd = get_build_cmd(buildos)
    print(cmd)
    subprocess.check_call(cmd.split(), cwd=pkgdir)

    fix_spec_file(buildos)

#Rebuild .spec and binaries
subprocess.check_call('{} -m PyInstaller -y --clean --windowed {}'.format(envpython, specfile).split(), cwd=pkgdir)
