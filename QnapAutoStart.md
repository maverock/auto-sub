
```

#! /bin/sh
### BEGIN INIT INFO
# Provides: Auto-sub application instance
# Required-Start: $all
# Required-Stop: $all
# Default-Start: 2 3 4 5
# Default-Stop: 0 1 6
# Short-Description: starts instance of Auto-sub
# Description: starts instance of Auto-sub using start-stop-daemon
### END INIT INFO
############### EDIT ME ##################
QPKG_NAME=AutoSub
QPKG_DIR=
DAEMON=/usr/bin/python2.6
DAEMON_OPTS=" /share/MD0_DATA/.qpkg/AutoSub/AutoSub.py -c /share/MD0_DATA/.qpkg/AutoSub/config.properties -d -l"
case "$1" in
start)
echo "Starting $QPKG_NAME"
if [ `/sbin/getcfg ${QPKG_NAME} Enable -u -d FALSE -f /etc/config/qpkg.conf` = UNKNOWN ]; then
/sbin/setcfg ${QPKG_NAME} Enable TRUE -f /etc/config/qpkg.conf
elif [ `/sbin/getcfg ${QPKG_NAME} Enable -u -d FALSE -f /etc/config/qpkg.conf` != TRUE ]; then
echo "${QPKG_NAME} is disabled."
exit 1
fi
${DAEMON} ${DAEMON_OPTS}
;;
stop)
echo "Stopping $QPKG_NAME"
for pid in $(/bin/pidof python); do
/bin/grep -q "AutoSub.py" /proc/$pid/cmdline && /bin/kill $pid
done
/bin/sleep 2
;;
restart|force-reload)
echo "Restarting $QPKG_NAME"
$0 stop
$0 start
;;
*)
N=/etc/init.d/$QPKG_NAME
echo "Usage: $N {start|stop|restart|force-reload}" >&2
exit 1
;;
esac
exit 0
```

qpkg.conf
```
[AutoSub]
Name = AutoSub
Version =
Enable = TRUE
QPKG_File =
Date = 2012-12-09
shell = /share/MD0_DATA/.qpkg/AutoSub/AutoSub.sh
Install_Path = /share/MD0_DATA/.qpkg/AutoSub
WebUI = /
Author = Bas
Web_port = 8083
RC_Number = 133
```

Before you can auto start the application run it once from the commandline.:
```
cd /share/MD0_DATA/.qpkg/AutoSub
/usr/bin/python2.6 AutoSub.py
```
Open a webbrowser and connect to: http://<ip of your qnap>:8083/ and go to config and save it once. This will create a default config file. Next shutdown auto-sub and you will be able to use the AutoSub.sh script.