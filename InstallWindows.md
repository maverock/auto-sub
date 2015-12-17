# Windows #

  1. Downloads the script from our download page, make sure you download the windows version
  1. Unpack the zip
  1. Click AutoSub.exe, a webbrowser should now open
  1. Go to the config page, check the settings, make sure you set atleast: path (Should point to the location where AutoSub.py is located. Rootpath (Should point to the root of your series folder)
  1. Shutdown AutoSub and start it again
  1. Enjoy your subtitles!


## FAQ ##

Q: How do I prevent AutoSub from launching a browser?

A: Create a shortcut to AutoSub.exe. Right click on the shortcut, click on properties. In the Target text area you will see the path to AutoSub.py for example "C:\Program Files\auto-sub\AutoSub.exe"
Enter '--nolaunch' at the end of the target field.
so it looks like this:

"C:\Program Files\auto-sub\AutoSub.exe" --nolaunch

Make sure you enter --nolaunch after the " and not inside.