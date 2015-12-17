#Howto connect to auto-sub not using port 8083 but http://hostname/auto-sub for example

# Introduction #
This page describes how you can connect to auto-sub using an proxy system and thus connecting to http://hostname/auto-sub and not http://hostname:8083/

This tutorial is written for a Synology machine but will work on any linux system. Only the paths to files are different.

Before we start, make sure auto-sub isn't running

```
$ ps | grep AutoSub.py
10160 root      138m S    /volume1/@appstore/python/bin/python AutoSub.py -c /volume1/@appstore/aut...
# Crap... It is still running
$ cd /volume1/@tmp/
$ wget http://autosub-testing:8083/home/shutdown
```

# Tuturial #

Ok, got to auto-subs location. In our case:
```
cd /volume1/@appstore/auto-sub/
```

Now editing config.properties
```
vi config.properties
# search for
webroot = 
# change it to
webroot = /auto-sub
```

How locate the apache config file. In our case:
```
vi /usr/syno/apache/conf/httpd.conf-user
# add the following at the end of the file:
LoadModule proxy_module modules/mod_proxy.so                        
LoadModule proxy_http_module modules/mod_proxy_http.so
 
<Location /auto-sub>                                                
    ProxyPass http://localhost:8083/auto-sub                             
    ProxyPassReverse http://localhost:8083/auto-sub                      
</Location> 
```
How restart apache and start autosub

```
$ /usr/syno/etc.defaults/rc.d/S97apache-user.sh restart
$ /volume1/@appstore/python/bin/python /volume1/@appstore/auto-sub/AutoSub.py -c /volume1/@appstore/auto-sub/config.properties -d
```

Give it a couple of minutes then visit: http://autosub-testing/auto-sub/

(of course change autosub-testing to your hostname)

# Proxy without webroot #
(Doesn't work on synology)

Add the following to your apache config:
```
<Location /auto-sub>
    ProxyPass http://localhost:8083/auto-sub
    ProxyPassReverse http://localhost:8083/auto-sub
    SetOutputFilter proxy-html
    ProxyHTMLURLMap / /auto-sub/
</Location>
```