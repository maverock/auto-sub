README

Thank you for choosing AutoSub! The automated python subtitle downloader for Bierdopje.com.
Many thansk by the Bierdopje.com administrators to expose the API and RSS feeds for us lazy people.

Quick start:
1. To run Autosub please make sure you have Python 2.5 or newer (no Python 3.x support!)
2. Edit the config.properties file to suit your needs.

Config file explanation:
[config]  # main config section
subeng = en  # the postfix of the english subtitle that shall be downloaded e.g. subtitle.en.srt (Only if fallbacktoeng = True)
logfile = AutoSubService.log # Log file of auto sub
rootpath = /mnt/nas1/content/TV/test # Location of your TV content
fallbacktoeng = True # Whether or not to download the english subtitle if available

[skipshow] #skip show section
ShowABC=1,2,3 # Show name to skip followed by the seasons to skip, if everything can be skip set season to 0