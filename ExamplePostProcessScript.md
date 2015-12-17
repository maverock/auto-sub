# Example Post Process #
**TODO: UPDATE INFO FOR NEW RELEASE (0.5)**

**Note: This ExamplePostProcess script is written for Linux / Mac and not tested &supported on Windows**

The post process example scripts allow users to see what is possible with the postprocess function.

To use the postprocess function together with ExamplePostProcess, add postprocesscmd to your config.properties, just like this:

```
postprocesscmd = python2 ExamplePostProcess.py
```

Note: Remember to change the python commando to match your system and make sure the application is able to locate the ExamplePostProcess.py

Functions currently available:
  * echo
    * Simply echos its arguments
  * twitter
    * Posts its arguments on twitter
  * growl
    * Send notifications to a growl server
    * Tested with Growl for Windows (works 100%)
    * Tested with Growl for Linux (work without encryption, don't set a password!)

## Howto use: ##
**Edit ExamplePostProcess.py** Search for the variable "what"
**change what to one of the function available (stated above)** for some functions like twitter additional configuration is required see below

## Twitter configuration ##
To use twitter, first change the variable 'what' to twitter:

```
what = "twitter"
```

Now run the script once from command line without any arguments given. Visit the url given. When you visit the url, login with your twitter username and password. Grant the auto-sub application access and copy the pin given by the website. Paste the pin number into the command shell.
```
$ python2 ExamplePostProcess.py 
Visit: https://api.twitter.com/oauth/authorize?oauth_token=Mc9ONp4EAn4Jbq2rmMv9gaxxxxxxxxxxxxxxx
PIN: 2401853
token_key='476983972-BwhRz2wBjMLLt7IVkxxxxxxxxxxxxxxxxxx'
token_secret='rtZZthfI3YCmudc0hFxxxxxxxxxxxxxxxxxxxxxxxx'
```
A token\_key and a token\_secret will be given by the script, copy both variable.
Paste them between #Twitter options: and #/Twitter options like this:
```
#Twitter options:
token_key='476983972-BwhRz2wBjMLLt7IVkxxxxxxxxxxxxxxxxxx'
token_secret='rtZZthfI3YCmudc0hFxxxxxxxxxxxxxxxxxxxxxxxx'
#/Twitter options
```

Now the postprocess function will post on twitter when something is downloaded.

## Growl configuration ##
edit ExamplePostProcess.py
Tested with:
  * Growl for Windows
    * Works perfectly!
  * Growl for Linux
    * Works if you don't use a password
  * Growl for Mac
    * Works if you use a password
    * Known [issue](http://code.google.com/p/auto-sub/issues/detail?id=29)
First change 'what' to growl:

```
what = "growl"
```

Go to #Growl Options. Set the settings according to your system example:
```
#Growl Options:
growl_host="127.0.0.1"
growl_port=23053
growl_pass="test"
#/Growl Options
```

or if you don't have a password:
```
#Growl Options:
growl_host="127.0.0.1"
growl_port=23053
growl_pass=""
#/Growl Options
```

Now that everything is set, it is important to register the application. To register run the examplepostprocessscript once without giving in any arguments.
```
$ python ExamplePostProcess.py
python2 ExamplePostProcess.py
GNTP/1.0 -OK NONE
Response-Action: REGISTER


GNTP/1.0 -OK NONE
Response-Action: NOTIFY

```

Example create by a user for file moving:
```
import sys, os, glob, shutil, errno
sourcepath = "/volume1/video/_Series_/"
destpath = "/volume1/video/_Series_ok_/"
os.chdir(sourcepath)
serieList = ['Eureka', 'Castle (2009)', 'Hart of Dixie', 'Modern Family', 'Once Upon a Time (2011)', 'Touch (2012)' ]
for serie in serieList:
	sourcepath_serie = sourcepath + serie + "/*/*"
	destpath_serie = destpath + serie
	try:
		os.makedirs(destpath_serie)
	except OSError, e:
		if e.errno != errno.EEXIST:
			print sourcepath_serie
	for file in glob.glob(sourcepath_serie):
		if file[len(file)-7:] == ".nl.srt":
			print file[0:len(file)-7]
			for name_zkr in glob.glob(sourcepath_serie):
				if name_zkr[0:len(name_zkr)-4] == file[0:len(file)-7]:
					shutil.move(name_zkr, destpath_serie)
				if name_zkr[0:len(name_zkr)-5] == file[0:len(file)-7]:
					shutil.move(name_zkr, destpath_serie)
				if name_zkr[0:len(name_zkr)-6] == file[0:len(file)-7]:
					shutil.move(name_zkr, destpath_serie)
				if name_zkr[0:len(name_zkr)-7] == file[0:len(file)-7]:
					shutil.move(name_zkr, destpath_serie)
				if name_zkr[0:len(name_zkr)-8] == file[0:len(file)-7]:
					shutil.move(name_zkr, destpath_serie)
				if name_zkr[0:len(name_zkr)-9] == file[0:len(file)-7]:
					shutil.move(name_zkr, destpath_serie)
```