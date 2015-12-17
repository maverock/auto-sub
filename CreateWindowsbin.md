# Windows #

```
import shutil
import py2exe
from distutils.core import setup
import sys

import distutils

import os
import zipfile

name = 'Auto-Sub'
releasetype = 'Alpha'
release = '0.5.6'
try:
	os.mkdir('dist/')
except:
	pass


if len(sys.argv) > 1:
    oldArgs = sys.argv[1:]
    del sys.argv[1:]

sys.argv.append('py2exe')

options = dict(
    name=name,
    version=release,
    author='Romke van Dijk',
    author_email='romke.vandijk@gmail.com',
    description=name + ' ' + release,
    scripts=['AutoSub.py'],
)

program = [ {'script': 'AutoSub.py' } ]
options['options'] = {'py2exe':
                        {
                         'bundle_files': 3,
                         'optimize': 2,
						 'packages': ['Cheetah'],
						 'excludes': ['Tkconstants', 'Tkinter', 'tcl'],
                         'compressed': 0
                        }
                     }
options['console'] = program
options['zipfile'] = 'library/autosub.zip'
#options['windows'] = program
#options['zipfile'] = None
setup(**options)

shutil.copy('dist/AutoSub.exe', 'dist/AutoSub-console.exe')

del options['console']
options['windows'] = program
setup(**options)


distutils.dir_util.copy_tree('interface/', 'dist/interface/')
distutils.dir_util.copy_tree('library/', 'dist/library/')
shutil.copy('ExamplePostProcess.py', 'dist/')
shutil.copy('README.txt', 'dist/')
shutil.copy('changelog.xml', 'dist/')

def zipdir(path, zip):
    for root, dirs, files in os.walk(path):
        for file in files:
            zip.write(os.path.join(root, file))

os.chdir('dist')
zip = zipfile.ZipFile('../auto-sub.' + releasetype + '.' + release + '.Windows.zip', 'w')
zipdir('.', zip)
zip.close()

os.chdir('..')
try:
	os.mkdir('auto-sub/')
except:
	pass
	

distutils.dir_util.copy_tree('autosub/', 'auto-sub/autosub/')
distutils.dir_util.copy_tree('cherrypy/', 'auto-sub/cherrypy/')
distutils.dir_util.copy_tree('interface/', 'auto-sub/interface/')
distutils.dir_util.copy_tree('library/', 'auto-sub/library/')
shutil.copy('ExamplePostProcess.py', 'auto-sub/')
shutil.copy('README.txt', 'auto-sub/')
shutil.copy('changelog.xml', 'auto-sub/')
shutil.copy('init.ubuntu', 'auto-sub/')
shutil.copy('AutoSub.py', 'auto-sub/')

zip = zipfile.ZipFile('auto-sub.' + releasetype + '.' + release + '.zip', 'w')
zipdir('auto-sub/', zip)
```