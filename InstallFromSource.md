#This page describes howto install Auto-Sub from source (the newest version)

# Windows #

## Requirements ##
The following software is required to install Auto-Sub:
  * Mercurial
  * Python 2.5 or higher
  * Cheetah Templating Engine
Recommended:
  * Winrar (to extract a tar.gz file)
  * Notepad++ The default config.properties in writing in linux, windows and linux have a diffrent line ending, this tool makes it easier to edit the file.

Download links:

http://mercurial.selenic.com/wiki/Download
File: Mercurial-2.1 (msI)

http://python.org/download/releases/2.7.2/
File: Windows x86 MSI Installer

http://pypi.python.org/pypi/Cheetah/2.4.4
File:  Cheetah-2.4.4.tar.gz

http://www.winrar.nl/
File: WinRAR 4.10 (32 bit)


## Installing ##
  * Install Python, default settings will do
  * Install Mercurial, default settings will do

**NOTE** Some users reported that it is required to reboot after this step to ensure everything is working.

Extract Cheetah-2.4.4.tar.gz, use winrar or any other extracting tool.

Remember the location where you extracted Cheetah

Open a cmd prompt

```
cd "C:\Documents and Settings\Tja\My Documents\Downloads\Cheetah-2.4.4\Cheetah-2.4.4"
C:\Python27\python.exe setup.py install
```

Output should be a lot of text and then: "Pure Python installation succeeded"

Keep the command prompt open

Now, move to the location where you want to install auto-sub. This tutorial will install it in:

C:\Program Files\auto-sub

So we, change our working directory to that location.
```
cd "C:\Program Files\"
```

Now lets download auto-sub by running the following command:
```
hg clone https://code.google.com/p/auto-sub/
```

Output:
```
C:\Program Files>hg clone https://code.google.com/p/auto-sub/
destination directory: auto-sub
requesting all changes
adding changesets
adding manifests
adding file changes
added 116 changesets with 332 changes to 121 files (+1 heads)
updating to branch default
101 files updated, 0 files merged, 0 files removed, 0 files unresolved
```

Now change working directory to: auto-sub:
```
C:\Program Files>cd auto-sub
```

## Configuration ##

Lets start Auto-Sub!
```
C:\Program Files\auto-sub>C:\Python27\python.exe AutoSub.py
```

A browser will now open, go the config page and set the following variables:

  * path (should point to where auto-sub is located (normally you don't need to change this))
  * rootpath (should point to where your series are located)

That is the bare minimal configuration, look around at the config page for explanations on the other options.

Now press 'save' at the bottom of the config page.
Then, shutdown Auto-Sub

**Note:** make sure the webserver port is set to a free port



You can start auto-sub again using the following command:

```
C:\Program Files\auto-sub>C:\Python27\python.exe AutoSub.py
```

To make it start automatically, follow the instructions below.

## Updating ##
**Note:** Before updating, make sure auto-sub isn't running!

It is very easy to update auto-sub. Open a command prompt and enter the following commands:
```
C:\>cd C:\Program Files\auto-sub
C:\Program Files\auto-sub>hg pull
C:\Program Files\auto-sub>hg update
```

## Tips ##
### How to autostart auto-sub ###
Create a new empty file.

Name the file: AutoSub-start.bat (make sure it is called .bat)

Edit the file with notepad
```
C:\Python27\python.exe "C:\Program Files\auto-sub\AutoSub.py" --config="C:\Program Files\auto-sub\config.properties"
```
Save the file, right click on it. Select: 'Create Shortcut'
Now, in your windows menu. There is a folder called 'Startup'

**NOTE:**(it can be find with (Windows 7): %systemdrive%\users\%username%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup)

Image:
![http://cdn.digitaltrends.com/wp-content/uploads/2009/12/Start_Menu_Startup_Folder.jpg](http://cdn.digitaltrends.com/wp-content/uploads/2009/12/Start_Menu_Startup_Folder.jpg)

Just place the shortcut in the folder and all done!

# Ubuntu #
## requirements ##
Python 2.5 or higher (installed by default)
Mercurial
Cheetah Templating Engine

**NOTE:** All those packages are in the repository

## Installation ##
Make sure you are in the directory you want auto-sub to be installed. For this tutorial I will place auto-sub in the user's home directory
```
sudo apt-get update
sudo apt-get install mercurial python-cheetah
hg clone https://code.google.com/p/auto-sub/
cd auto-sub
```

## Configuration ##

Start Auto-Sub for the first time:

```
#Run AutoSub normally
python AutoSub.py
```

A browser will now open, go the config page and set the following variables:

  * path (should point to where auto-sub is located (normally you don't need to change this))
  * rootpath (should point to where your series are located)

That is the bare minimal configuration, look around at the config page for explanations on the other options.

Now press 'save' at the bottom of the config page.
Then, shutdown Auto-Sub

You can start Auto-Sub in a couple of ways now:

```
#Run AutoSub normally
python AutoSub.py
#Run AutoSub in daemon mode:
python AutoSub.py --daemon
#See the AutoSub help message:
python AutoSub.py --help
```

## Tips ##

### Run AutoSub at start up ###
There are 2 ways to do this:

1. Simple using rc.local
```
sudo vi /etc/rc.local
```

Add the following rule to rc.local:
```
/usr/bin/python /home/zyronix/auto-sub/AutoSub.py --daemon --config=/home/zyronix/auto-sub/config.properties
```

2. Install init.ubuntu on your system:

**NOTE:** Make sure you're in the auto-sub directory

First edit init.ubuntu so it works for your system.
```
sudo cp init.ubuntu /etc/init.d/autosub
sudo chmod 755 /etc/init.d/autosub
sudo update-rc.d autosub defaults
```