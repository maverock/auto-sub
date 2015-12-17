#This page shows all information available for the config.properties file. The config file for AutoSub

**TODO: UPDATE INFO FOR NEW RELEASE (0.5)**

The Config.Properties file is also created if AutoSub can't find one in its current work directory. To prevent AutoSub from using the wrong config file you can specificity it with the --config parameter.

```
python AutoSub.py --config=/home/user/config.properties
```

# Sections #

The available sections are:
  * config - contains the main settings required for autosub to run
  * logfile - contains the settings for the log file
  * skipshow - Allows user to skip a show, which means no subtitle are download for the show
  * namemapping - Allow user to make local file name to a BierDopje ID

## config ##
options available:
  * rootpath - the path to the folders containing the series
  * fallbacktoeng - use this to force autosub to download English files
  * subeng - this variable set lang in Serie.Name.lang.srt for English subtitles
  * subnl - this variable set lang in Serie.Name.lang.srt for Dutch subtitles
  * logfile - the path / name for the Logfile
  * postprocesscmd - the command execute after downloading a subtitle file
  * workdir - the workdirectory for autosub

### rootpath ###
**Required**
The path were the video (and subtitle) files are which need to be watched.
Example:
```
rootpath = /home/user/Series
```

### fallbacktoeng ###
**Required**
Use this variable if you want AutoSub to automatically download English subtitle files if the Dutch are not available.
Either False or True
Example:
```
fallbacktoeng = True
```

### subeng ###
**Required**
This variable set lang in Serie.Name.lang.srt for English subtitles.
If you download an English subtitle for Dexter.S01E01.avi for example the file will be named: Dexter.S01E01.en.srt
default: en
Example
```
subeng = en
```

### subnl ###
**Optional**
This variable set lang in Serie.Name.lang.srt for Dutch subtitles.
If you download an Dutch subtitle for Dexter.S01E01.avi for example the file will be named: Dexter.S01E01.nl.srt

If you don't set this variable Dexter.S01E01.avi will get the following subtitle file: Dexter.S01E01.srt

Example
```
subeng = nl
```

### logfile ###
**Required**
The path and name for the logfile
When workdir is set, it is not required to include the path for the logfile

default:AutoSubService.log

Example
```
logfile = AutoSubService.log
```

### PostProcessCMD ###
**Optional**
If AutoSub need to execute a command after a subtitle has been downloaded. Set this variable to the command which is needed.
If this variable is not set, no command will be executed.
Look at the ExamplePostProcess wikipage for more information

Remember, AutoSub will wait on the PostProcessCmd before it continues.

Example
```
postprocesscmd = python2 ExamplePostProcess.py
```

### WorkDir ###
**Optional**
Set this variable to the directory which contains the libraries and other files.
If this variable is not set, it will point to the current working directory of the user.

Example
```
workdir = /home/user/auto-sub
```

## LogFile Section ##
This section is completely **optional**
Options available
  * loglevel - either set to debug, info, warning, error, critical
  * lognum - the max log files
  * logsize - max log size in bytes
  * loglevelconsole - log level for the console, same options as loglevel

Example
```
[logfile]
loglevel = debug
lognum = 1
logsize = 1000000
loglevelconsole = debug
```

## SkipShow Section ##
**Required**
Allows the user to skip a show or to skip a / multiple season(s)
To Skip a show completely:
```
[skipshow]
Dexter = 0
```
To skip season 1 and 4:
```
[skipshow]
Dexter = 1,4
```

Example
```
[skipshow]
Another Serie = 0
An Another Serie = 1,2 
Dexter = 0
How I Met Your Mother = 1,4,5
```

## NameMapping Section ##
**Required**
Sometimes a file can be named differently local then on BierDopje.com. use this section to name the local serie name to a bierdopje ID

Example:
```
[namemapping]
Hawaii Five 0 2010 = 14211
Prime Suspect Us = 15249
```

# Example Config #
```
[config]
rootpath = /media/USBHDD/Series
fallbacktoeng = True
subeng = en
subnl = nl
logfile = AutoSubService.log
postprocesscmd = python2 ExamplePostProcess.py
workdir = /home/user/auto-sub

[logfile]
loglevel = debug
lognum = 3
logsize = 1000000
loglevelconsole = error


[skipshow]
Another Serie = 0
An Another Serie = 1,2 

[namemapping]
Serie Name = 14211
```